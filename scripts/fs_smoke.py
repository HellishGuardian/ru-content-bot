from pathlib import Path
from dotenv import load_dotenv
import os
from google.oauth2 import service_account
from google.cloud import firestore

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

project_env = os.getenv("FIRESTORE_PROJECT_ID")
cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
db_id = os.getenv("FIRESTORE_DATABASE_ID", "(default)")

assert project_env, "FIRESTORE_PROJECT_ID missing in .env"
assert cred_path and Path(cred_path).exists(), f"Credentials file not found: {cred_path}"

creds = service_account.Credentials.from_service_account_file(cred_path)
project_key = creds.project_id

print("ENV project:", project_env)
print("KEY project:", project_key)
print("DB id:", db_id)

if project_env != project_key:
    raise RuntimeError("Project mismatch: .env vs service-account key")

db = firestore.Client(project=project_key, credentials=creds, database=db_id)
doc = db.collection("_smoke").document("ping")
doc.set({"ok": True})
print("Firestore OK:", doc.get().to_dict())
