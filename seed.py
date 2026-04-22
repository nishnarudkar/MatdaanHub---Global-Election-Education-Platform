import json
import firebase_admin
from firebase_admin import firestore

# Initialize Firebase using default application credentials
try:
    firebase_admin.initialize_app()
except ValueError:
    pass # App already initialized

db = firestore.client()

def seed():
    print("Connecting to Firestore...")
    
    with open('data/elections.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    print(f"Found {len(data)} countries to seed.")
    
    for cid, cdata in data.items():
        print(f"Seeding data for: {cid}...")
        # Write to the elections collection
        db.collection("elections").document(cid).set(cdata)
        
    print("✅ Firestore seeding complete!")

if __name__ == "__main__":
    seed()
