from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: str = "user"


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    role: str
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class AnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=10000)
    language: Optional[str] = None  # auto-detect if None


class URLFeatures(BaseModel):
    urls_found: List[str]
    url_risk_score: int
    risk_keywords: Dict[str, List[str]]
    caps_ratio: float


class AnalysisResult(BaseModel):
    prediction: str
    confidence: float
    confidence_percent: float
    explanation: List[str]
    language: str
    features: URLFeatures
    probabilities: Dict[str, float]


class AnalysisResponse(BaseModel):
    id: Optional[str] = None
    text_preview: str
    result: AnalysisResult
    analyzed_at: datetime


class HistoryItem(BaseModel):
    id: str
    text_preview: str
    prediction: str
    confidence_percent: float
    language: str
    analyzed_at: datetime


class DashboardStats(BaseModel):
    total_analyzed: int
    phishing_count: int
    suspicious_count: int
    legitimate_count: int
    phishing_percentage: float
    recent_analyses: List[HistoryItem]
    weekly_data: List[Dict[str, Any]]


class TrainRequest(BaseModel):
    dataset_path: Optional[str] = None
    model_type: str = "logistic"
