"""Medical AI metadata extractor — THE DOMAIN DIFFERENTIATOR.

Two-pass extraction:
1. Rule-based keyword matching (fast, high recall)
2. LLM-based extraction via Groq (high precision, structured output)
"""

from __future__ import annotations

import re
import json
import logging
from typing import Any

from backend.extractors.base import MedicalDocument, MedicalMetadata

log = logging.getLogger(__name__)

# ── Comprehensive Medical AI Vocabulary ─────────────────────

MODALITIES = {
    "MRI": ["mri", "magnetic resonance", "t1-weighted", "t2-weighted", "flair", "dwi", "dti"],
    "CT": ["ct scan", "computed tomography", "ct image", "ct volume"],
    "X-ray": ["x-ray", "xray", "radiograph", "chest x-ray", "cxr"],
    "Ultrasound": ["ultrasound", "ultrasonography", "sonography", "echocardiography"],
    "Fundus": ["fundus", "fundoscopy", "retinal photograph", "color fundus"],
    "OCT": ["oct", "optical coherence tomography"],
    "Histology": ["histology", "histopathology", "h&e", "whole slide image", "wsi", "pathology slide"],
    "Endoscopy": ["endoscopy", "colonoscopy", "gastroscopy", "capsule endoscopy"],
    "Mammography": ["mammography", "mammogram", "breast imaging"],
    "PET": ["pet scan", "pet/ct", "positron emission"],
    "SPECT": ["spect", "single-photon emission"],
    "ECG": ["ecg", "ekg", "electrocardiogram", "electrocardiography"],
    "EEG": ["eeg", "electroencephalogram", "electroencephalography"],
    "Dermoscopy": ["dermoscopy", "dermatoscopy", "skin imaging"],
}

ANATOMIES = {
    "brain": ["brain", "cerebral", "intracranial", "cortex", "hippocampus", "glioma", "neuroimaging"],
    "retina": ["retina", "retinal", "fundus", "optic disc", "macula", "fovea"],
    "lung": ["lung", "pulmonary", "bronchial", "airway"],
    "chest": ["chest", "thorax", "thoracic", "mediastinal"],
    "skin": ["skin", "dermatological", "cutaneous", "melanoma", "lesion"],
    "bone marrow": ["bone marrow", "hematological", "blood smear", "leukocyte"],
    "liver": ["liver", "hepatic", "hepatocellular"],
    "heart": ["heart", "cardiac", "coronary", "myocardial", "echocardiogram"],
    "colon": ["colon", "colorectal", "colonic", "polyp detection"],
    "breast": ["breast", "mammary"],
    "prostate": ["prostate", "prostatic"],
    "spine": ["spine", "spinal", "vertebral"],
    "kidney": ["kidney", "renal", "nephrology"],
    "pancreas": ["pancreas", "pancreatic"],
    "thyroid": ["thyroid"],
    "eye": ["eye", "ocular", "ophthalmic", "strabismus", "cataract", "glaucoma"],
}

CONDITIONS = {
    "tumor": ["tumor", "tumour", "neoplasm", "cancer", "malignant", "benign"],
    "diabetic retinopathy": ["diabetic retinopathy", "dr grading", "proliferative dr", "non-proliferative"],
    "glaucoma": ["glaucoma", "optic nerve head", "cup-to-disc"],
    "strabismus": ["strabismus", "squint", "eye misalignment"],
    "glioma": ["glioma", "glioblastoma", "gbm", "astrocytoma"],
    "leukemia": ["leukemia", "leukaemia", "acute lymphoblastic", "acute myeloid leukemia"],
    "thalassemia": ["thalassemia", "thalassaemia", "iron overload"],
    "brain tumor": ["brain tumor", "brain tumour", "intracranial tumor"],
    "melanoma": ["melanoma", "malignant melanoma", "skin cancer"],
    "pneumonia": ["pneumonia", "lung infection"],
    "COVID-19": ["covid", "sars-cov-2", "coronavirus"],
    "alzheimer": ["alzheimer", "alzheimer's", "dementia", "cognitive decline"],
    "stroke": ["stroke", "cerebrovascular", "ischemic stroke"],
    "fracture": ["fracture", "bone fracture"],
    "polyp": ["polyp", "adenoma", "colorectal polyp"],
    "cardiomyopathy": ["cardiomyopathy", "heart disease", "cardiac dysfunction"],
    "age-related macular degeneration": ["amd", "age-related macular degeneration", "macular degeneration"],
    "cataract": ["cataract"],
    "retinal vessel occlusion": ["retinal vessel", "vessel occlusion", "vein occlusion"],
    "epilepsy": ["epilepsy", "seizure", "epileptic"],
}

ARCHITECTURES = {
    "U-Net": ["u-net", "unet"],
    "ViT": ["vit", "vision transformer"],
    "ResNet": ["resnet", "resnet50", "resnet101", "resnet18", "residual network"],
    "EfficientNet": ["efficientnet"],
    "DenseNet": ["densenet"],
    "VGG": ["vgg", "vgg16", "vgg19"],
    "Inception": ["inception", "inceptionv3", "googlenet"],
    "BERT": ["bert", "biobert", "scibert", "clinicalbert", "pubmedbert"],
    "GPT": ["gpt", "gpt-4", "chatgpt", "gpt-3"],
    "SAM": ["sam", "segment anything"],
    "DINO": ["dino", "dinov2"],
    "MAE": ["mae", "masked autoencoder"],
    "TransUNet": ["transunet"],
    "Swin-UNet": ["swin-unet", "swin transformer"],
    "nnU-Net": ["nnunet", "nnu-net"],
    "YOLO": ["yolo", "yolov5", "yolov8"],
    "Faster R-CNN": ["faster r-cnn", "faster rcnn"],
    "GAN": ["gan", "generative adversarial", "cyclegan", "pix2pix", "stylegan"],
    "VAE": ["vae", "variational autoencoder"],
    "CLIP": ["clip", "contrastive language-image"],
    "RETFound": ["retfound"],
    "MedSAM": ["medsam"],
    "BiomedCLIP": ["biomedclip"],
    "LLaVA-Med": ["llava-med", "llavamed"],
}

DATASETS = {
    "MIMIC-III": ["mimic-iii", "mimic3", "mimic"],
    "CheXpert": ["chexpert"],
    "NIH ChestX-ray": ["nih chestx-ray", "chestx-ray14", "nih chest"],
    "BraTS": ["brats", "brain tumor segmentation challenge"],
    "DRIVE": ["drive dataset", "drive retinal"],
    "ISIC": ["isic", "isic 2018", "isic 2019", "isic 2020"],
    "HAM10000": ["ham10000"],
    "OASIS": ["oasis", "open access series of imaging studies"],
    "ADNI": ["adni", "alzheimer's disease neuroimaging"],
    "UK Biobank": ["uk biobank"],
    "ImageNet": ["imagenet"],
    "CIFAR": ["cifar-10", "cifar-100"],
    "Messidor": ["messidor"],
    "STARE": ["stare dataset"],
    "CHASE_DB1": ["chase_db1", "chase db1"],
    "Kvasir": ["kvasir"],
    "LUNA16": ["luna16", "luna 16"],
    "LIDC-IDRI": ["lidc", "lidc-idri"],
    "PadChest": ["padchest"],
    "VinDr-CXR": ["vindr", "vindr-cxr"],
    "EyePACS": ["eyepacs"],
    "APTOS": ["aptos 2019", "aptos"],
    "Montgomery": ["montgomery county", "montgomery tb"],
    "Shenzhen": ["shenzhen dataset", "shenzhen tb"],
    "IU X-Ray": ["iu x-ray", "indiana university"],
}

METRICS = [
    "AUC", "AUROC", "accuracy", "precision", "recall", "sensitivity",
    "specificity", "F1", "F1-score", "Dice", "Dice coefficient", "IoU",
    "Jaccard", "mAP", "AP", "BLEU", "ROUGE", "perplexity", "FID",
    "Hausdorff distance", "mean absolute error", "MAE", "RMSE",
    "Cohen's kappa", "kappa", "PPV", "NPV", "MCC",
]

TECHNIQUES = {
    "Grad-CAM": ["grad-cam", "gradcam", "gradient-weighted class activation"],
    "SHAP": ["shap", "shapley"],
    "LIME": ["lime", "local interpretable"],
    "Federated Learning": ["federated learning", "federated", "fl protocol"],
    "Self-supervised Learning": ["self-supervised", "ssl", "contrastive learning", "pretext task"],
    "Transfer Learning": ["transfer learning", "pre-trained", "pretrained", "fine-tuning", "fine-tune"],
    "Data Augmentation": ["data augmentation", "augmentation strategy", "mixup", "cutmix"],
    "Knowledge Distillation": ["knowledge distillation", "teacher-student"],
    "Attention Mechanism": ["attention mechanism", "self-attention", "cross-attention"],
    "Multi-task Learning": ["multi-task", "multitask"],
    "Active Learning": ["active learning"],
    "Few-shot Learning": ["few-shot", "zero-shot", "meta-learning"],
    "Domain Adaptation": ["domain adaptation", "domain shift", "distribution shift"],
    "Ensemble": ["ensemble", "model ensemble", "ensemble learning"],
    "Quantization": ["quantization", "model compression", "pruning"],
    "Kalman Filter": ["kalman filter", "extended kalman"],
}


class MedicalMetaExtractor:
    """Extract medical AI metadata from documents using rule-based + LLM."""

    def extract_rules(self, text: str) -> MedicalMetadata:
        """Pass 1: Fast rule-based keyword matching."""
        text_lower = text.lower()
        meta = MedicalMetadata()

        for name, keywords in MODALITIES.items():
            if any(kw in text_lower for kw in keywords):
                meta.imaging_modalities.append(name)

        for name, keywords in ANATOMIES.items():
            if any(kw in text_lower for kw in keywords):
                meta.anatomies.append(name)

        for name, keywords in CONDITIONS.items():
            if any(kw in text_lower for kw in keywords):
                meta.conditions.append(name)

        for name, keywords in ARCHITECTURES.items():
            if any(kw in text_lower for kw in keywords):
                meta.architectures.append(name)

        for name, keywords in DATASETS.items():
            if any(kw in text_lower for kw in keywords):
                meta.datasets.append(name)

        for metric in METRICS:
            if metric.lower() in text_lower:
                if metric not in meta.metrics:
                    meta.metrics.append(metric)

        for name, keywords in TECHNIQUES.items():
            if any(kw in text_lower for kw in keywords):
                meta.techniques.append(name)

        # Extract limitations
        limit_section = re.search(
            r"(?:limitation|weakness|shortcoming|drawback)[s]?[:\s](.{50,500})",
            text_lower,
        )
        if limit_section:
            meta.limitations.append(limit_section.group(1).strip()[:300])

        # Extract future work
        future_section = re.search(
            r"(?:future work|future direction|future stud)[s]?[:\s](.{50,500})",
            text_lower,
        )
        if future_section:
            meta.future_work.append(future_section.group(1).strip()[:300])

        return meta

    async def extract_llm(self, text: str, llm_router: Any) -> MedicalMetadata:
        """Pass 2: LLM-based extraction for precision."""
        prompt = f"""Extract medical AI metadata from this research text. Return ONLY valid JSON.

Text (first 3000 chars):
{text[:3000]}

Return this exact JSON structure:
{{
  "imaging_modalities": ["list of imaging types used"],
  "anatomies": ["body parts/organs studied"],
  "conditions": ["medical conditions addressed"],
  "architectures": ["ML model architectures used"],
  "datasets": ["dataset names used"],
  "metrics": ["evaluation metrics reported"],
  "techniques": ["ML techniques applied"],
  "limitations": ["stated limitations"],
  "future_work": ["suggested future directions"],
  "clinical_relevance": "high|medium|low"
}}"""

        try:
            response = await llm_router.generate(
                "medical_extraction",
                prompt,
                system_prompt="You are a medical AI research metadata extractor. Extract precise entities only. Never fabricate.",
                json_mode=True,
                temperature=0.1,
            )
            data = json.loads(response)
            return MedicalMetadata(
                imaging_modalities=data.get("imaging_modalities", []),
                anatomies=data.get("anatomies", []),
                conditions=data.get("conditions", []),
                architectures=data.get("architectures", []),
                datasets=data.get("datasets", []),
                metrics=data.get("metrics", []),
                techniques=data.get("techniques", []),
                limitations=data.get("limitations", []),
                future_work=data.get("future_work", []),
                clinical_relevance=data.get("clinical_relevance", "unknown"),
            )
        except Exception as e:
            log.warning("LLM extraction failed: %s", e)
            return MedicalMetadata()

    async def extract(
        self, doc: MedicalDocument, llm_router: Any | None = None
    ) -> MedicalMetadata:
        """Combined two-pass extraction."""
        text = doc.full_text() or doc.raw_content

        # Pass 1: Rules
        rule_meta = self.extract_rules(text)

        # Pass 2: LLM (if available)
        llm_meta = MedicalMetadata()
        if llm_router:
            llm_meta = await self.extract_llm(text, llm_router)

        # Merge (union of both passes, deduplicated)
        return MedicalMetadata(
            imaging_modalities=list(set(rule_meta.imaging_modalities + llm_meta.imaging_modalities)),
            anatomies=list(set(rule_meta.anatomies + llm_meta.anatomies)),
            conditions=list(set(rule_meta.conditions + llm_meta.conditions)),
            architectures=list(set(rule_meta.architectures + llm_meta.architectures)),
            datasets=list(set(rule_meta.datasets + llm_meta.datasets)),
            metrics=list(set(rule_meta.metrics + llm_meta.metrics)),
            techniques=list(set(rule_meta.techniques + llm_meta.techniques)),
            limitations=list(set(rule_meta.limitations + llm_meta.limitations)),
            future_work=list(set(rule_meta.future_work + llm_meta.future_work)),
            clinical_relevance=llm_meta.clinical_relevance if llm_meta.clinical_relevance != "unknown" else rule_meta.clinical_relevance,
            mesh_terms=doc.medical_metadata.mesh_terms,
        )
