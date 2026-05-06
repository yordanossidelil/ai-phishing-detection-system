# 🛡️ AI-Based Phishing Detection and Prevention System

An AI-powered web application that detects phishing emails, messages, and URLs using Machine Learning and NLP. Supports **English**, **Amharic (አማርኛ)**, and **Afaan Oromo** with automatic language detection.

---

## ✨ Features

| Feature | Details |
|---------|---------|
| 🤖 ML Detection | Logistic Regression + Naive Bayes with TF-IDF |
| 🌍 Multilingual | English, Amharic, Afaan Oromo (auto-detect) |
| 📊 Dashboard | Stats, weekly charts, recent activity |
| 🔐 Auth | JWT authentication, role-based access |
| 🚦 Rate Limiting | 30 req/min per IP |
| 🔍 Explainable AI | Reasons for every classification |
| 🌐 REST API | FastAPI with auto-generated Swagger docs |
| 🗄️ Database | MongoDB Atlas |

---

## 🏗️ Project Structure

```
ai-phishing-detection-system/
├── ai_model/
│   ├── data/phishing_dataset.csv   # Training dataset
│   ├── models/                     # Trained .pkl models
│   ├── preprocessor.py             # NLP pipeline + feature extraction
│   └── train_model.py              # Training + PhishingDetector class
├── backend/
│   ├── app/
│   │   ├── api/                    # analysis.py, auth.py
│   │   ├── core/                   # config, database, security
│   │   ├── middleware/             # rate limiting
│   │   ├── models/                 # Pydantic schemas
│   │   ├── services/               # ml_service.py
│   │   └── main.py                 # FastAPI app
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/             # Navbar, ResultCard
│   │   ├── pages/                  # Analyze, Dashboard, History, Auth, Admin
│   │   ├── hooks/                  # useAuth, useLang
│   │   ├── i18n/translations.js    # EN/AM/OR translations
│   │   └── utils/api.js            # Axios client
│   └── Dockerfile
├── database/
│   └── setup_db.py                 # MongoDB indexes + schema docs
├── docs/
│   └── API.md                      # Full API documentation
└── docker-compose.yml
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- MongoDB Atlas account (or local MongoDB)

### 1. Clone & Configure

```bash
git clone <repo>
cd ai-phishing-detection-system
```

Copy the example env file and fill in your credentials:
```bash
cp backend/.env.example backend/.env
```

### 2. Train the ML Model

```bash
cd ai_model
pip install scikit-learn pandas numpy
python train_model.py
```

### 3. Start Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 4. Start Frontend

```bash
cd frontend
npm install
npm run dev
```

Open: http://localhost:3000

### 5. Docker (Full Stack)

```bash
docker-compose up --build
```

---

## 🧠 ML Pipeline

```
Input Text
    ↓
Language Detection (English / Amharic / Oromo)
    ↓
Text Preprocessing (lowercase, URL/email tokens, punctuation removal)
    ↓
TF-IDF Vectorization (10,000 features, bigrams)
    ↓
Logistic Regression / Naive Bayes
    ↓
URL Feature Analysis (TLD, domain, suspicious keywords)
    ↓
Risk Keyword Detection (urgency, threat, reward, financial)
    ↓
Output: { prediction, confidence, explanation, language }
```

**Model Performance (on sample dataset):**
- Logistic Regression: **90% accuracy**
- Naive Bayes: **80% accuracy**

---

## 🌍 Multilingual Examples

**English:**
```
Input:  "URGENT: Your account suspended! Click http://fake-bank.xyz"
Output: ❌ PHISHING (92.3%) — Urgent language, Suspicious URL
```

**Amharic:**
```
Input:  "አካውንትዎ ተዘግቷል እባክዎ እዚህ ይጫኑ http://fake-bank.com"
Output: ❌ ፊሺንግ (89.1%) — የአማርኛ ፊሺንግ ቃላት ተገኝተዋል
```

**Afaan Oromo:**
```
Input:  "Herregaa! Cuqaasi: http://iccitii.fake.com"
Output: ❌ PHISHING (87.4%) — Jecha phishing Oromoo argame
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/analyze` | Analyze text for phishing |
| GET | `/api/history` | Get analysis history |
| GET | `/api/dashboard` | Dashboard statistics |
| POST | `/api/train` | Retrain model (admin) |
| POST | `/api/auth/register` | Register user |
| POST | `/api/auth/login` | Login |
| GET | `/api/auth/me` | Current user |
| GET | `/health` | Health check |

Full docs: `http://localhost:8000/docs`

---

## 🗄️ Database Schema (MongoDB)

- **users** — username, email, password_hash, role
- **analysis_results** — text, prediction, confidence, explanation, language, features
- **logs** — phishing events, IP addresses, timestamps
- **urls** — URL risk scores and metadata

---

## 🔐 Security

- JWT tokens (HS256, 60min expiry)
- Bcrypt password hashing
- Rate limiting (30 req/min)
- Input validation via Pydantic
- Suspicious activity logging
- CORS protection

---

## 📦 Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, Vite, Tailwind CSS, Recharts |
| Backend | FastAPI, Python 3.11 |
| ML | scikit-learn, TF-IDF, Logistic Regression |
| Database | MongoDB Atlas (Motor async driver) |
| Auth | JWT (python-jose), bcrypt |
| Deploy | Docker, Docker Compose, Nginx |
