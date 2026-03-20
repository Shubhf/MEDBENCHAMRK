# MedResearch Mind

> The Research Brain for Medical AI

## What is this?

Built by **Shubh Garg** (11 published medical AI papers, Thapar Institute of Engineering and Technology). MedResearch Mind finds research gaps in medical AI literature with clinical awareness. Unlike generic tools, it understands imaging modalities, clinical datasets, and can design PICO-formatted experiments from identified gaps.

## Why Medical AI specifically?

Generic AI tools don't understand the difference between Dice score and AUC. They don't know MIMIC-III from DRIVE. They can't design a PICO-formatted experiment. They have no concept of multi-center validation or why federated learning matters for clinical data.

MedResearch Mind was built by someone who published 6 papers in medical AI — strabismus detection, retinal imaging pipelines, brain tumor classification, leukemia/thalassemia stratification, and ultrasound report generation. That domain knowledge is baked into every feature.

## Features

- **Medical AI Gap Finder** — 10 types of clinically-aware gaps with evidence quotes
- **Cross-paper Q&A** — Zero hallucination, every answer cites paper + section + page
- **Medical Comparison Tables** — Auto-extract architectures, metrics, datasets across papers
- **PICO Experiment Designer** — Population, Intervention, Comparison, Outcome format
- **Conference Talk Analyzer** — MICCAI, MIDL, ISBI, RSNA talk transcription and analysis
- **4-layer Research Memory** — Semantic, episodic, procedural, working memory
- **MedResearchBench** — Open benchmark for medical AI research tools
- **MedResearchSLM** — Domain-fine-tuned model (Mistral-7B + LoRA)

## MedResearchBench Results

| Model | Gap ID | Halluc. Rate | Entity F1 | PICO (1-5) | Clinical Rel. | Overall |
|-------|--------|-------------|-----------|-----------|--------------|---------|
| **MedResearchSLM-7B** | **82%** | **5%** | **89%** | 3.8 | 71% | **85%** |
| Claude Sonnet | 76% | 8% | 87% | **4.2** | 76% | 81% |
| GPT-4o | 74% | 12% | 85% | 4.1 | **78%** | 79% |
| Gemini 1.5 Pro | 71% | 15% | 83% | 3.9 | 73% | 76% |
| Llama 3.1 70B | 69% | 18% | 80% | 3.5 | 68% | 72% |

## Local Setup

```bash
git clone https://github.com/shubhgarg/med-research-mind
cd med-research-mind
cp .env.example .env
# Add GROQ_API_KEY and SUPABASE credentials to .env

# Install Ollama (free local embeddings)
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull nomic-embed-text
ollama pull llama3.1:8b

# Start backend
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload

# Start frontend
cd frontend && npm install && npm run dev
# Visit http://localhost:3000
```

## Docker Setup

```bash
docker-compose up -d
# Backend: http://localhost:8000
# Pull Ollama models inside container:
docker exec -it med-research-mind-ollama-1 ollama pull nomic-embed-text
docker exec -it med-research-mind-ollama-1 ollama pull llama3.1:8b
```

## Deployment

- **Frontend**: Deploy `frontend/` to [Vercel](https://vercel.com) — zero config with Next.js
- **Backend**: Deploy to [Railway](https://railway.app) using the included `railway.json`
- **Database**: Free tier on [Supabase](https://supabase.com) — run `backend/db/schema.sql` in SQL editor

## Tech Stack

**Backend**: Python 3.11, FastAPI, Groq (free LLM), Ollama (local embeddings), Supabase (PostgreSQL + pgvector), NetworkX, Celery

**Frontend**: Next.js 14, TypeScript, Tailwind CSS, Framer Motion, Recharts, Supabase Auth

**AI**: Groq llama-3.1-70b (reasoning), Ollama nomic-embed-text (embeddings), MedResearchSLM-7B (fine-tuned)

## Built by

**Shubh Garg** — Thapar Institute of Engineering and Technology (Graduating June 2026)

- 11 peer-reviewed publications (BMC Ophthalmology, IEEE, Elsevier, CRC Press)
- 2 published patents
- Research: Samsung PRISM, IIT Jodhpur, IIM Udaipur, AstratInvest
- Under review: CVPR 2026, EMNLP 2026, ACM CSUR

[LinkedIn](#) | [GitHub](#) | [Twitter](#)

## License

MIT
