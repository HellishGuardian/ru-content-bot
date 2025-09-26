from pathlib import Path
from dotenv import load_dotenv
from google.oauth2 import service_account
from google.cloud import firestore
import os

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

creds = service_account.Credentials.from_service_account_file(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
db = firestore.Client(
    project=os.getenv("FIRESTORE_PROJECT_ID"),
    credentials=creds,
    database=os.getenv("FIRESTORE_DATABASE_ID", "(default)"),
)

print("Users:")
for doc in db.collection("users").limit(10).stream():
    print("-", doc.id, doc.to_dict())

print("\nSmoke doc:")
print(db.collection("_smoke").document("ping").get().to_dict())
