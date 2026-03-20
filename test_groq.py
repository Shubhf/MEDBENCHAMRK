"""Quick test: Groq API + Ollama connectivity."""

import asyncio
import os
import sys

# Load .env
from pathlib import Path
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, val = line.partition("=")
            os.environ.setdefault(key.strip(), val.strip())


async def test_groq():
    """Test Groq API connection."""
    print("=" * 50)
    print("TEST 1: Groq API")
    print("=" * 50)

    api_key = os.getenv("GROQ_API_KEY", "")
    if not api_key:
        print("FAIL: GROQ_API_KEY not set in .env")
        print("  → Go to console.groq.com → API Keys → Create API Key")
        print("  → Paste it in .env as GROQ_API_KEY=gsk_...")
        return False

    try:
        import groq
        client = groq.AsyncGroq(api_key=api_key)

        print(f"  API Key: {api_key[:8]}...{api_key[-4:]}")
        print("  Calling Llama 3.3 70B...")

        resp = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a medical AI research assistant."},
                {"role": "user", "content": "What is the DRIVE dataset used for in medical AI? Answer in 2 sentences."},
            ],
            temperature=0.3,
            max_tokens=200,
        )

        answer = resp.choices[0].message.content
        print(f"  PASS: Got response ({len(answer)} chars)")
        print(f"  Response: {answer}")
        print(f"  Model: {resp.model}")
        print(f"  Tokens: {resp.usage.total_tokens}")
        return True

    except Exception as e:
        print(f"  FAIL: {e}")
        return False


async def test_groq_json():
    """Test Groq JSON mode (used for medical extraction)."""
    print("\n" + "=" * 50)
    print("TEST 2: Groq JSON Mode (Medical Extraction)")
    print("=" * 50)

    api_key = os.getenv("GROQ_API_KEY", "")
    if not api_key:
        print("  SKIP: No API key")
        return False

    try:
        import groq
        client = groq.AsyncGroq(api_key=api_key)

        resp = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Extract medical AI metadata. Return ONLY valid JSON."},
                {"role": "user", "content": """Extract entities from: "We propose a Vision Transformer for retinal vessel segmentation on the DRIVE dataset, achieving Dice score of 0.82 using fundus photography."

Return JSON: {"imaging_modalities": [], "anatomies": [], "conditions": [], "architectures": [], "datasets": [], "metrics": []}"""},
            ],
            temperature=0.1,
            max_tokens=300,
            response_format={"type": "json_object"},
        )

        import json
        answer = resp.choices[0].message.content
        parsed = json.loads(answer)
        print(f"  PASS: Valid JSON returned")
        print(f"  Modalities: {parsed.get('imaging_modalities', [])}")
        print(f"  Anatomies: {parsed.get('anatomies', [])}")
        print(f"  Architectures: {parsed.get('architectures', [])}")
        print(f"  Datasets: {parsed.get('datasets', [])}")
        print(f"  Metrics: {parsed.get('metrics', [])}")
        return True

    except Exception as e:
        print(f"  FAIL: {e}")
        return False


async def test_ollama():
    """Test Ollama local connection."""
    print("\n" + "=" * 50)
    print("TEST 3: Ollama (Local Embeddings)")
    print("=" * 50)

    try:
        import httpx
        base = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

        async with httpx.AsyncClient(timeout=10.0) as http:
            # Health check
            r = await http.get(f"{base}/api/tags")
            if r.status_code != 200:
                print(f"  FAIL: Ollama not running at {base}")
                print("  → Install: curl -fsSL https://ollama.ai/install.sh | sh")
                print("  → Start: ollama serve")
                return False

            models = [m["name"] for m in r.json().get("models", [])]
            print(f"  Ollama running. Models: {models}")

            # Test embedding
            if any("nomic" in m for m in models):
                r = await http.post(
                    f"{base}/api/embeddings",
                    json={"model": "nomic-embed-text", "prompt": "retinal vessel segmentation"},
                )
                if r.status_code == 200:
                    embedding = r.json()["embedding"]
                    print(f"  PASS: Embedding generated ({len(embedding)} dims)")
                    return True
                else:
                    print(f"  FAIL: Embedding request failed: {r.status_code}")
                    return False
            else:
                print("  WARN: nomic-embed-text not pulled")
                print("  → Run: ollama pull nomic-embed-text")
                return False

    except Exception as e:
        print(f"  FAIL: Ollama not reachable — {e}")
        print("  → Install: curl -fsSL https://ollama.ai/install.sh | sh")
        print("  → Run: ollama pull nomic-embed-text")
        return False


async def test_gap_prompt():
    """Test a full gap analysis prompt (the hero feature)."""
    print("\n" + "=" * 50)
    print("TEST 4: Gap Analysis Prompt (Hero Feature)")
    print("=" * 50)

    api_key = os.getenv("GROQ_API_KEY", "")
    if not api_key:
        print("  SKIP: No API key")
        return False

    try:
        import groq
        import json
        client = groq.AsyncGroq(api_key=api_key)

        prompt = """You are a medical AI research gap detector. Analyze these papers and identify research gaps.

PAPER 1: "U-Net for Retinal Vessel Segmentation"
Modality: fundus photography. Architecture: U-Net. Dataset: DRIVE (40 images). Metrics: Dice 0.82. Single-center, adult patients only.

PAPER 2: "ResNet50 for Diabetic Retinopathy Grading"
Modality: fundus photography. Architecture: ResNet50. Dataset: EyePACS (88k images). Metrics: AUC 0.95. No interpretability analysis.

PAPER 3: "DenseNet for Glaucoma Detection"
Modality: fundus photography. Architecture: DenseNet121. Dataset: ORIGA (650 images). Metrics: AUC 0.88. Western population only.

Return JSON array of gaps:
[{"gap_type": "...", "description": "...", "evidence": "...", "clinical_relevance_score": 0.0}]"""

        resp = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are an expert medical AI researcher. Identify genuine research gaps."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=1500,
            response_format={"type": "json_object"},
        )

        answer = resp.choices[0].message.content
        gaps = json.loads(answer)

        # Handle both direct array and wrapped object
        if isinstance(gaps, dict):
            gaps = gaps.get("gaps", gaps.get("research_gaps", [gaps]))
        if not isinstance(gaps, list):
            gaps = [gaps]

        print(f"  PASS: Found {len(gaps)} gaps!")
        for i, gap in enumerate(gaps[:5]):
            desc = gap.get("description", str(gap))[:100]
            score = gap.get("clinical_relevance_score", "N/A")
            gtype = gap.get("gap_type", "unknown")
            print(f"  Gap {i+1} [{gtype}] (relevance: {score}): {desc}")

        print(f"\n  Tokens used: {resp.usage.total_tokens}")
        return True

    except Exception as e:
        print(f"  FAIL: {e}")
        return False


async def main():
    print("\nMedResearch Mind — System Test")
    print("=" * 50)

    results = {
        "Groq API": await test_groq(),
        "Groq JSON Mode": await test_groq_json(),
        "Ollama Embeddings": await test_ollama(),
        "Gap Analysis": await test_gap_prompt(),
    }

    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    for test, passed in results.items():
        status = "PASS" if passed else "FAIL"
        icon = "+" if passed else "-"
        print(f"  [{icon}] {test}: {status}")

    total = sum(results.values())
    print(f"\n  {total}/{len(results)} tests passed")

    if not results["Groq API"]:
        print("\n  NEXT STEP: Add GROQ_API_KEY to .env")
        print("  → console.groq.com → API Keys → Create API Key")
    if not results["Ollama Embeddings"]:
        print("\n  NEXT STEP: Install Ollama")
        print("  → curl -fsSL https://ollama.ai/install.sh | sh")
        print("  → ollama pull nomic-embed-text")


if __name__ == "__main__":
    asyncio.run(main())
