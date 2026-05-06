from fastapi import APIRouter, Depends, HTTPException, Request
from datetime import datetime
from bson import ObjectId

from app.models.schemas import AnalyzeRequest, AnalysisResponse, TrainRequest
from app.core.database import get_db
from app.core.security import get_optional_user
from app.services.ml_service import analyze_text, retrain_model

router = APIRouter(prefix="/api", tags=["analysis"])


def _serialize(doc) -> dict:
    doc["id"] = str(doc.pop("_id"))
    return doc


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze(
    request: AnalyzeRequest,
    req: Request,
    current_user: dict = Depends(get_optional_user),
):
    result = analyze_text(request.text)
    db = get_db()

    doc = {
        "text": request.text,
        "text_preview": request.text[:100] + ("..." if len(request.text) > 100 else ""),
        "result": result,
        "user_id": current_user.get("sub") if current_user else None,
        "ip_address": req.client.host,
        "analyzed_at": datetime.utcnow(),
    }

    inserted = await db.analysis_results.insert_one(doc)

    # Log suspicious/phishing activity
    if result["prediction"] in ("phishing", "suspicious"):
        await db.logs.insert_one({
            "event": "phishing_detected",
            "prediction": result["prediction"],
            "confidence": result["confidence"],
            "ip_address": req.client.host,
            "user_id": current_user.get("sub") if current_user else None,
            "text_preview": doc["text_preview"],
            "timestamp": datetime.utcnow(),
        })

    return AnalysisResponse(
        id=str(inserted.inserted_id),
        text_preview=doc["text_preview"],
        result=result,
        analyzed_at=doc["analyzed_at"],
    )


@router.get("/history")
async def get_history(
    page: int = 1,
    limit: int = 20,
    current_user: dict = Depends(get_optional_user),
):
    db = get_db()
    skip = (page - 1) * limit
    query = {}
    if current_user:
        query["user_id"] = current_user.get("sub")

    cursor = db.analysis_results.find(query).sort("analyzed_at", -1).skip(skip).limit(limit)
    docs = await cursor.to_list(length=limit)
    total = await db.analysis_results.count_documents(query)

    items = []
    for doc in docs:
        items.append({
            "id": str(doc["_id"]),
            "text_preview": doc.get("text_preview", ""),
            "prediction": doc["result"]["prediction"],
            "confidence_percent": doc["result"]["confidence_percent"],
            "language": doc["result"]["language"],
            "analyzed_at": doc["analyzed_at"],
        })

    return {"items": items, "total": total, "page": page, "limit": limit}


@router.get("/dashboard")
async def get_dashboard(current_user: dict = Depends(get_optional_user)):
    db = get_db()
    total = await db.analysis_results.count_documents({})
    phishing = await db.analysis_results.count_documents({"result.prediction": "phishing"})
    suspicious = await db.analysis_results.count_documents({"result.prediction": "suspicious"})
    legitimate = await db.analysis_results.count_documents({"result.prediction": "legitimate"})

    # Weekly data (last 7 days)
    from datetime import timedelta
    weekly_data = []
    for i in range(6, -1, -1):
        day = datetime.utcnow() - timedelta(days=i)
        start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
        count = await db.analysis_results.count_documents({
            "analyzed_at": {"$gte": start, "$lt": end}
        })
        phish_count = await db.analysis_results.count_documents({
            "analyzed_at": {"$gte": start, "$lt": end},
            "result.prediction": "phishing"
        })
        weekly_data.append({
            "date": start.strftime("%Y-%m-%d"),
            "day": start.strftime("%a"),
            "total": count,
            "phishing": phish_count,
        })

    # Recent 5
    cursor = db.analysis_results.find({}).sort("analyzed_at", -1).limit(5)
    recent_docs = await cursor.to_list(length=5)
    recent = [{
        "id": str(d["_id"]),
        "text_preview": d.get("text_preview", ""),
        "prediction": d["result"]["prediction"],
        "confidence_percent": d["result"]["confidence_percent"],
        "language": d["result"]["language"],
        "analyzed_at": d["analyzed_at"],
    } for d in recent_docs]

    return {
        "total_analyzed": total,
        "phishing_count": phishing,
        "suspicious_count": suspicious,
        "legitimate_count": legitimate,
        "phishing_percentage": round(phishing / total * 100, 1) if total > 0 else 0,
        "recent_analyses": recent,
        "weekly_data": weekly_data,
    }


@router.post("/train")
async def train_model(
    request: TrainRequest,
    current_user: dict = Depends(get_optional_user),
):
    if not current_user or current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    results = retrain_model(request.dataset_path, request.model_type)
    return {"message": "Model retrained successfully", "results": results}
