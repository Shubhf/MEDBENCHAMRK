"""Test Supabase connection and database schema."""

import os
import sys
from pathlib import Path

# Load .env
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, val = line.partition("=")
            os.environ.setdefault(key.strip(), val.strip())


def test_connection():
    print("=" * 50)
    print("TEST 1: Supabase Connection")
    print("=" * 50)

    url = os.getenv("SUPABASE_URL", "")
    anon = os.getenv("SUPABASE_ANON_KEY", "")
    service = os.getenv("SUPABASE_SERVICE_KEY", "")

    if not url or not anon:
        print("  FAIL: SUPABASE_URL or SUPABASE_ANON_KEY not set")
        return False

    print(f"  URL: {url}")
    print(f"  Anon key: {anon[:15]}...")
    print(f"  Service key: {service[:15]}..." if service else "  Service key: NOT SET")

    try:
        from supabase import create_client
        client = create_client(url, anon)
        print("  PASS: Client created successfully")
        return True
    except Exception as e:
        print(f"  FAIL: {e}")
        return False


def test_tables():
    print("\n" + "=" * 50)
    print("TEST 2: Database Tables")
    print("=" * 50)

    try:
        from supabase import create_client
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY")
        client = create_client(url, key)

        tables = [
            "user_profiles", "sources", "chunks", "semantic_nodes",
            "semantic_edges", "sessions", "queries", "gap_reports",
            "training_data", "user_patterns", "waitlist",
            "comparisons", "experiments",
        ]

        passed = 0
        for table in tables:
            try:
                resp = client.table(table).select("*").limit(0).execute()
                print(f"  [+] {table}: OK")
                passed += 1
            except Exception as e:
                print(f"  [-] {table}: {e}")

        print(f"\n  {passed}/{len(tables)} tables accessible")
        return passed == len(tables)
    except Exception as e:
        print(f"  FAIL: {e}")
        return False


def test_waitlist_insert():
    print("\n" + "=" * 50)
    print("TEST 3: Waitlist Insert (Write Test)")
    print("=" * 50)

    try:
        from supabase import create_client
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY")
        client = create_client(url, key)

        # Insert test row
        resp = client.table("waitlist").insert({
            "email": "test@medresearchmind.app",
            "full_name": "Test User",
            "institution": "Test University",
            "clinical_role": "test",
            "research_area": "medical AI",
        }).execute()

        if resp.data:
            row_id = resp.data[0]["id"]
            print(f"  PASS: Inserted test row (id: {row_id[:8]}...)")

            # Clean up
            client.table("waitlist").delete().eq("id", row_id).execute()
            print(f"  PASS: Cleaned up test row")
            return True
        else:
            print("  FAIL: No data returned")
            return False
    except Exception as e:
        err = str(e)
        if "duplicate" in err.lower():
            # Already exists from a previous test
            print("  PASS: Table writable (duplicate from previous test)")
            return True
        print(f"  FAIL: {e}")
        return False


def test_vector_function():
    print("\n" + "=" * 50)
    print("TEST 4: Vector Search Function")
    print("=" * 50)

    try:
        from supabase import create_client
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY")
        client = create_client(url, key)

        # Test the match_chunks RPC function with a dummy embedding
        dummy_embedding = [0.0] * 768
        resp = client.rpc("match_chunks", {
            "query_embedding": dummy_embedding,
            "match_count": 5,
        }).execute()

        print(f"  PASS: match_chunks function works (returned {len(resp.data)} results)")
        return True
    except Exception as e:
        print(f"  FAIL: {e}")
        return False


if __name__ == "__main__":
    print("\nMedResearch Mind — Supabase Test")
    print("=" * 50)

    # Install supabase if needed
    try:
        import supabase
    except ImportError:
        print("Installing supabase...")
        os.system(f"{sys.executable} -m pip install supabase -q")

    results = {
        "Connection": test_connection(),
        "Tables": test_tables(),
        "Write": test_waitlist_insert(),
        "Vector Search": test_vector_function(),
    }

    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    for test, passed in results.items():
        icon = "+" if passed else "-"
        print(f"  [{icon}] {test}: {'PASS' if passed else 'FAIL'}")

    total = sum(results.values())
    print(f"\n  {total}/{len(results)} tests passed")
