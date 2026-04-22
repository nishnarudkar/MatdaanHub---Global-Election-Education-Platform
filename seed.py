import json
import sys
import firebase_admin
from firebase_admin import firestore

# Initialize Firebase using default application credentials
try:
    firebase_admin.initialize_app()
except ValueError:
    pass  # App already initialized

db = firestore.client()


def seed():
    print("Connecting to Firestore...")
    errors = []

    # ── Seed elections ──
    try:
        with open('data/elections.json', 'r', encoding='utf-8') as f:
            elections = json.load(f)
        print(f"Found {len(elections)} countries to seed.")
        for cid, cdata in elections.items():
            try:
                db.collection("elections").document(cid).set(cdata)
                print(f"  ✅ elections/{cid}")
            except Exception as e:
                msg = f"  ❌ elections/{cid}: {e}"
                print(msg)
                errors.append(msg)
    except FileNotFoundError:
        print("❌ data/elections.json not found — skipping elections seed.")
        errors.append("Missing data/elections.json")

    # ── Seed glossary ──
    try:
        with open('data/glossary.json', 'r', encoding='utf-8') as f:
            glossary_data = json.load(f)
        terms = glossary_data.get("glossary", [])
        print(f"Found {len(terms)} glossary terms to seed.")
        for term_obj in terms:
            term_key = term_obj["term"].lower().replace(" ", "_").replace("(", "").replace(")", "")
            try:
                db.collection("glossary").document(term_key).set(term_obj)
                print(f"  ✅ glossary/{term_key}")
            except Exception as e:
                msg = f"  ❌ glossary/{term_key}: {e}"
                print(msg)
                errors.append(msg)
    except FileNotFoundError:
        print("❌ data/glossary.json not found — skipping glossary seed.")
        errors.append("Missing data/glossary.json")

    if errors:
        print(f"\n⚠️  Seeding completed with {len(errors)} error(s):")
        for err in errors:
            print(f"   {err}")
        sys.exit(1)
    else:
        print("\n✅ Firestore seeding complete!")


if __name__ == "__main__":
    seed()
