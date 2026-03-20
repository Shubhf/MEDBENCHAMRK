"""ClinicalTrials.gov extractor via API v2."""

from __future__ import annotations

import re
from typing import Any

import httpx

from backend.extractors.base import BaseExtractor, MedicalDocument, Chunk


def _parse_nct(url: str) -> str:
    m = re.search(r"(NCT\d{8})", url, re.IGNORECASE)
    if m:
        return m.group(1).upper()
    raise ValueError(f"Cannot parse NCT ID from: {url}")


class ClinicalTrialsExtractor(BaseExtractor):
    """Extract clinical trial information from ClinicalTrials.gov."""

    async def extract(self, source: str, **kwargs: Any) -> MedicalDocument:
        nct_id = _parse_nct(source)

        async with httpx.AsyncClient(timeout=30.0) as http:
            resp = await http.get(
                f"https://clinicaltrials.gov/api/v2/studies/{nct_id}"
            )
            resp.raise_for_status()
            data = resp.json()

        proto = data.get("protocolSection", {})
        id_mod = proto.get("identificationModule", {})
        status_mod = proto.get("statusModule", {})
        desc_mod = proto.get("descriptionModule", {})
        design_mod = proto.get("designModule", {})
        arms_mod = proto.get("armsInterventionsModule", {})
        outcomes_mod = proto.get("outcomesModule", {})
        eligibility_mod = proto.get("eligibilityModule", {})
        contacts_mod = proto.get("contactsLocationsModule", {})

        title = id_mod.get("officialTitle", id_mod.get("briefTitle", ""))
        brief_summary = desc_mod.get("briefSummary", "")
        detailed_desc = desc_mod.get("detailedDescription", "")
        status = status_mod.get("overallStatus", "")
        phase_list = (design_mod.get("phases") or ["Not Applicable"])
        enrollment_info = design_mod.get("enrollmentInfo", {})
        enrollment = enrollment_info.get("count", "N/A")

        interventions = []
        for arm in (arms_mod.get("interventions") or []):
            interventions.append(f"{arm.get('type', '')}: {arm.get('name', '')}")

        primary_outcomes = []
        for o in (outcomes_mod.get("primaryOutcomes") or []):
            primary_outcomes.append(o.get("measure", ""))

        secondary_outcomes = []
        for o in (outcomes_mod.get("secondaryOutcomes") or []):
            secondary_outcomes.append(o.get("measure", ""))

        eligibility = eligibility_mod.get("eligibilityCriteria", "")

        full_text = (
            f"Title: {title}\nNCT ID: {nct_id}\nStatus: {status}\n"
            f"Phase: {', '.join(phase_list)}\nEnrollment: {enrollment}\n\n"
            f"Summary: {brief_summary}\n\n"
            f"Description: {detailed_desc}\n\n"
            f"Interventions: {'; '.join(interventions)}\n\n"
            f"Primary Outcomes: {'; '.join(primary_outcomes)}\n"
            f"Secondary Outcomes: {'; '.join(secondary_outcomes)}\n\n"
            f"Eligibility: {eligibility}"
        )

        chunks = [Chunk(text=full_text[:3000], section="Trial Summary", chunk_index=0)]
        if len(full_text) > 3000:
            chunks.append(Chunk(text=full_text[3000:6000], section="Trial Details", chunk_index=1))

        return MedicalDocument(
            source_type="clinical_trial",
            source_url=source,
            title=title,
            raw_content=full_text,
            content_chunks=chunks,
            metadata={
                "nct_id": nct_id,
                "status": status,
                "phase": phase_list,
                "enrollment": enrollment,
                "interventions": interventions,
                "primary_outcomes": primary_outcomes,
                "secondary_outcomes": secondary_outcomes,
            },
        )
