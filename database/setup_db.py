"""
MongoDB Schema Setup — creates indexes for optimal query performance
Run once on first deployment: python setup_db.py
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "phishing_detection")


async def setup():
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]

    # users: unique email index
    await db.users.create_index("email", unique=True)
    await db.users.create_index("username")
    print("✓ users indexes created")

    # analysis_results: query by user, prediction, date
    await db.analysis_results.create_index("user_id")
    await db.analysis_results.create_index("analyzed_at")
    await db.analysis_results.create_index([("result.prediction", 1), ("analyzed_at", -1)])
    print("✓ analysis_results indexes created")

    # logs: query by event type and timestamp
    await db.logs.create_index("event")
    await db.logs.create_index("timestamp")
    await db.logs.create_index("ip_address")
    print("✓ logs indexes created")

    # urls: for URL deduplication and lookup
    await db.urls.create_index("url", unique=True)
    await db.urls.create_index("risk_score")
    print("✓ urls indexes created")

    print("\nDatabase setup complete!")
    print(f"Collections: users, analysis_results, logs, urls")
    client.close()


"""
SCHEMA DOCUMENTATION
====================

Collection: users
-----------------
{
  _id: ObjectId,
  username: str,
  email: str (unique),
  password_hash: str,
  role: "user" | "admin",
  created_at: datetime
}

Collection: analysis_results
-----------------------------
{
  _id: ObjectId,
  text: str,
  text_preview: str,
  result: {
    prediction: "phishing" | "suspicious" | "legitimate",
    confidence: float,
    confidence_percent: float,
    explanation: [str],
    language: "english" | "amharic" | "oromo",
    features: {
      urls_found: [str],
      url_risk_score: int,
      risk_keywords: {category: [str]},
      caps_ratio: float
    },
    probabilities: {legitimate: float, suspicious: float, phishing: float}
  },
  user_id: str | null,
  ip_address: str,
  analyzed_at: datetime
}

Collection: logs
----------------
{
  _id: ObjectId,
  event: str,
  prediction: str,
  confidence: float,
  ip_address: str,
  user_id: str | null,
  text_preview: str,
  timestamp: datetime
}

Collection: urls
----------------
{
  _id: ObjectId,
  url: str (unique),
  domain: str,
  risk_score: int,
  is_malicious: bool,
  first_seen: datetime,
  last_seen: datetime,
  scan_count: int
}
"""

if __name__ == "__main__":
    asyncio.run(setup())
