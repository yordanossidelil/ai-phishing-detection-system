# API Documentation — AI Phishing Detection System

Base URL: `http://localhost:8000`

---

## Authentication

### POST /api/auth/register
Register a new user.

**Request:**
```json
{ "username": "john", "email": "john@example.com", "password": "secret123" }
```
**Response:**
```json
{
  "access_token": "<jwt_token>",
  "token_type": "bearer",
  "user": { "id": "...", "username": "john", "email": "john@example.com", "role": "user", "created_at": "..." }
}
```

### POST /api/auth/login
Login with email and password.

**Request:**
```json
{ "email": "john@example.com", "password": "secret123" }
```
**Response:** Same as register.

### GET /api/auth/me
Get current user info. Requires `Authorization: Bearer <token>`.

---

## Analysis

### POST /api/analyze
Analyze a message for phishing. Auth optional (saves to user history if authenticated).

**Request:**
```json
{ "text": "URGENT: Your account is suspended! Click http://fake-bank.xyz" }
```

**Response:**
```json
{
  "id": "665abc123...",
  "text_preview": "URGENT: Your account is suspended!...",
  "result": {
    "prediction": "phishing",
    "confidence": 0.9234,
    "confidence_percent": 92.3,
    "explanation": ["Urgent language detected", "Account threat/suspension language", "Suspicious/malicious URL detected"],
    "language": "english",
    "features": {
      "urls_found": ["http://fake-bank.xyz"],
      "url_risk_score": 4,
      "risk_keywords": { "urgency": ["urgent"], "threat": ["suspended"] },
      "caps_ratio": 0.12
    },
    "probabilities": { "legitimate": 0.04, "suspicious": 0.03, "phishing": 0.93 }
  },
  "analyzed_at": "2024-01-15T10:30:00Z"
}
```

**Multilingual Example (Amharic):**
```json
{ "text": "አካውንትዎ ተዘግቷል እባክዎ እዚህ ይጫኑ http://fake-bank.com/verify" }
```
Response `language` will be `"amharic"` and `explanation` in Amharic.

**Multilingual Example (Afaan Oromo):**
```json
{ "text": "Herregaa! Lakkoofsi iccitii kee jijjiirameera. Cuqaasi: http://iccitii.fake.com" }
```
Response `language` will be `"oromo"` and `explanation` in Afaan Oromo.

---

### GET /api/history
Get analysis history. Auth optional (returns all if unauthenticated, user-specific if authenticated).

**Query params:** `page=1&limit=20`

**Response:**
```json
{
  "items": [
    {
      "id": "...",
      "text_preview": "URGENT: Your account...",
      "prediction": "phishing",
      "confidence_percent": 92.3,
      "language": "english",
      "analyzed_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 150,
  "page": 1,
  "limit": 20
}
```

---

### GET /api/dashboard
Get dashboard statistics and weekly chart data.

**Response:**
```json
{
  "total_analyzed": 500,
  "phishing_count": 210,
  "suspicious_count": 85,
  "legitimate_count": 205,
  "phishing_percentage": 42.0,
  "recent_analyses": [...],
  "weekly_data": [
    { "date": "2024-01-09", "day": "Tue", "total": 45, "phishing": 18 },
    ...
  ]
}
```

---

### POST /api/train
Retrain the ML model. **Admin only.**

**Request:**
```json
{ "model_type": "logistic" }
```
**Response:**
```json
{ "message": "Model retrained successfully", "results": { "logistic": { "accuracy": 0.94 } } }
```

---

## Health Check

### GET /health
```json
{ "status": "ok", "service": "AI Phishing Detection API" }
```

---

## Error Responses

| Code | Description |
|------|-------------|
| 400  | Bad request / validation error |
| 401  | Unauthorized — invalid/missing token |
| 403  | Forbidden — insufficient permissions |
| 422  | Unprocessable entity — invalid input |
| 429  | Rate limit exceeded (30 req/min) |
| 500  | Internal server error |

---

## Rate Limiting
- 30 requests per minute per IP
- Returns 429 with message when exceeded

## Interactive Docs
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
