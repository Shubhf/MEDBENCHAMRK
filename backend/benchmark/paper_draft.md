# MedResearchBench: A Benchmark for Evaluating AI Systems on Medical Research Intelligence Tasks

## Abstract

The proliferation of AI-powered research tools necessitates rigorous evaluation, particularly in the medical AI domain where inaccurate outputs carry clinical safety implications. We introduce MedResearchBench, a benchmark comprising five tasks specifically designed to evaluate AI systems on medical research intelligence: (1) medical research gap identification from paper collections, (2) clinical claim hallucination detection, (3) medical entity extraction covering imaging modalities, anatomies, architectures, and datasets, (4) PICO-formatted experiment design from research gaps, and (5) clinical relevance assessment. We evaluate five frontier language models across all tasks. Our key finding is that domain-specific fine-tuning yields significant improvements on gap identification (82% vs. 74% for GPT-4o), hallucination reduction (5% vs. 12%), and entity extraction (89% vs. 85% F1), while general-purpose models retain advantages on open-ended tasks like PICO design.

## 1. Introduction

Medical AI research has grown exponentially, with thousands of papers published annually across venues like MICCAI, IEEE, and clinical journals. Researchers increasingly rely on AI tools for literature review and gap identification. However, no standardized benchmark exists to evaluate these tools on medical AI research tasks specifically. This is concerning because errors in medical AI research tools — fabricated citations, missed clinical constraints, hallucinated statistics — can propagate into research decisions with downstream clinical implications.

We address this gap with MedResearchBench: five tasks that test the core capabilities needed for medical AI research intelligence.

## 2. Tasks

**Task 1: Gap Identification.** Given 10 medical AI papers on the same clinical condition, identify research gaps that were subsequently addressed in papers published 6 months later. Metric: Recall@5, Precision@5.

**Task 2: Hallucination Detection.** Given questions about medical AI papers, answer with citations. We check whether citations are real and claims are supported by the source text. Metric: Hallucination rate (lower is better).

**Task 3: Entity Extraction.** Given a medical AI paper, extract: imaging modalities, anatomies, conditions, architectures, datasets, metrics, and techniques. Metric: F1 per entity type.

**Task 4: PICO Design.** Given a medical AI research gap, design an experiment in PICO format (Population, Intervention, Comparison, Outcome). Metric: Expert preference score (1-5) on completeness, specificity, and feasibility.

**Task 5: Clinical Relevance Assessment.** Given a medical AI paper abstract, rate clinical translation potential on a 1-5 scale. Metric: Pearson correlation with expert clinician ratings.

## 3. Results

| Model | Gap ID | Halluc. | Entity F1 | PICO | Clinical |
|-------|--------|---------|-----------|------|----------|
| MedResearchSLM-7B | **0.82** | **0.05** | **0.89** | 3.8 | 0.71 |
| GPT-4o | 0.74 | 0.12 | 0.85 | 4.1 | **0.78** |
| Claude Sonnet | 0.76 | 0.08 | 0.87 | **4.2** | 0.76 |
| Gemini 1.5 Pro | 0.71 | 0.15 | 0.83 | 3.9 | 0.73 |
| Llama 3.1 70B | 0.69 | 0.18 | 0.80 | 3.5 | 0.68 |

## 4. Discussion

Domain-specific fine-tuning provides clear advantages on structured extraction and gap identification tasks, where knowledge of medical AI vocabulary and concepts is essential. General-purpose models perform better on open-ended generation tasks (PICO design) where broad reasoning capabilities matter more. Notably, hallucination rates are significantly lower for domain-specific models, which is critical in the medical context.

## 5. Conclusion

We release MedResearchBench as an open dataset on HuggingFace to establish a standardized evaluation framework for medical AI research tools. We encourage the community to submit evaluations of new models.

## References

1. Garg, S. et al. (2025). StrabNet-CQ: Strabismus classification. BMC Ophthalmology.
2. Thirunavukarasu, A.J. et al. (2023). Large language models in medicine. Nature Medicine.
3. Hu, E.J. et al. (2022). LoRA: Low-Rank Adaptation of Large Language Models. ICLR.
