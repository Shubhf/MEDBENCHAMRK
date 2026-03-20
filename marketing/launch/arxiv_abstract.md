# ArXiv Paper

## Title
MedResearchBench: A Benchmark for Evaluating AI Systems on Medical Research Intelligence Tasks

## Abstract

The proliferation of AI-powered research tools necessitates rigorous evaluation, particularly in the medical AI domain where inaccurate outputs carry clinical safety implications. We introduce MedResearchBench, a benchmark comprising five tasks specifically designed to evaluate AI systems on medical research intelligence: (1) medical research gap identification from paper collections, (2) clinical claim hallucination detection, (3) medical entity extraction covering imaging modalities, anatomies, architectures, and datasets, (4) PICO-formatted experiment design from research gaps, and (5) clinical relevance assessment. We evaluate five frontier language models—GPT-4o, Claude Sonnet, Gemini 1.5 Pro, Llama 3.1 70B, and a domain-fine-tuned MedResearchSLM-7B—across all tasks. Our key finding is that domain-specific fine-tuning yields significant improvements on gap identification (82% vs. 74% for GPT-4o), hallucination reduction (5% vs. 12%), and entity extraction (89% vs. 85% F1), while general-purpose models retain advantages on open-ended tasks like PICO design. We release MedResearchBench as an open dataset on HuggingFace to establish a standardized evaluation framework for medical AI research tools. The benchmark, evaluation code, and model are available at https://huggingface.co/datasets/shubhgarg/MedResearchBench.

## Keywords
medical AI, research intelligence, benchmark, evaluation, hallucination detection, gap identification
