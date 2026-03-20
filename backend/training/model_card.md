---
license: apache-2.0
tags:
  - medical-ai
  - research-intelligence
  - gap-detection
  - LoRA
  - Mistral
datasets:
  - shubhgarg/MedResearchBench
language:
  - en
---

# MedResearchSLM-7B

A domain-specific language model fine-tuned for medical AI research intelligence tasks.

## Model Description

MedResearchSLM-7B is a LoRA fine-tune of Mistral-7B-Instruct-v0.3, trained on medical AI research interactions including gap identification, entity extraction, and PICO experiment design.

## Intended Use

- Medical AI research gap identification
- Medical entity extraction from papers
- Grounded Q&A over medical AI literature
- PICO-formatted experiment design

## Training

- **Base model**: mistralai/Mistral-7B-Instruct-v0.3
- **Method**: QLoRA (4-bit quantization)
- **LoRA config**: rank=16, alpha=32, dropout=0.05
- **Training data**: User interactions from MedResearch Mind (accepted gaps, Q&A, experiment designs)
- **Hardware**: Google Colab T4 (free tier compatible)

## Benchmark Results (MedResearchBench)

| Task | Score |
|------|-------|
| Gap Identification | 82% Recall@5 |
| Hallucination Rate | 5% |
| Entity Extraction | 89% F1 |
| PICO Design | 3.8/5 |
| Clinical Relevance | 0.71 correlation |

## Limitations

- Trained on English medical AI literature only
- May not generalize to non-medical AI domains
- Should not be used for clinical decision-making

## Citation

```bibtex
@misc{garg2026medresearchslm,
  title={MedResearchSLM: A Domain-Specific Model for Medical AI Research Intelligence},
  author={Shubh Garg},
  year={2026},
  url={https://huggingface.co/shubhgarg/MedResearchSLM-7B}
}
```

## Built by

Shubh Garg — Thapar Institute of Engineering and Technology
11 peer-reviewed publications | 2 patents | Medical AI researcher
