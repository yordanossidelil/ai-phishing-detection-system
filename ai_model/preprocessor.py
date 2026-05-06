"""
NLP Preprocessing and Feature Extraction for Phishing Detection
"""
import re
import string
from urllib.parse import urlparse
from typing import List, Dict, Any

# Risk keywords by category
RISK_KEYWORDS = {
    "urgency": ["urgent", "immediate", "now", "asap", "quickly", "hurry", "fast", "today", "expire", "expiring"],
    "threat": ["suspended", "blocked", "locked", "deleted", "terminated", "banned", "restricted", "limited"],
    "reward": ["winner", "won", "prize", "free", "congratulations", "selected", "lucky", "reward", "bonus"],
    "action": ["click", "verify", "confirm", "update", "validate", "login", "signin", "submit", "provide"],
    "financial": ["bank", "account", "credit", "debit", "payment", "transfer", "money", "cash", "loan", "refund"],
    "security": ["password", "security", "breach", "hacked", "compromised", "suspicious", "alert", "warning"],
}

# Amharic risk keywords
AMHARIC_RISK_KEYWORDS = [
    "አስቸኳይ", "ይጫኑ", "ያረጋግጡ", "ተዘግቷል", "ተገድቧል", "ነፃ", "አሸናፊ",
    "ይሸልሙ", "ወዲያውኑ", "አካውንት", "ይዘምኑ", "ይለቁ"
]

# Afaan Oromo risk keywords
OROMO_RISK_KEYWORDS = [
    "hatattamaan", "cuqaasi", "mirkaneessi", "cufame", "dhaabate", "bilisaan",
    "mo'ate", "badhaasa", "amma", "herregaa", "lakkoofsa", "iccitii"
]

SUSPICIOUS_TLDS = {".xyz", ".tk", ".ml", ".ga", ".cf", ".gq", ".top", ".click", ".link", ".online", ".site"}
LEGITIMATE_DOMAINS = {"google.com", "microsoft.com", "amazon.com", "paypal.com", "apple.com", "facebook.com"}


def extract_urls(text: str) -> List[str]:
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    return re.findall(url_pattern, text)


def analyze_url(url: str) -> Dict[str, Any]:
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        path = parsed.path.lower()
        tld = "." + domain.split(".")[-1] if "." in domain else ""

        features = {
            "has_ip": bool(re.match(r'\d+\.\d+\.\d+\.\d+', domain)),
            "suspicious_tld": tld in SUSPICIOUS_TLDS,
            "is_legitimate_domain": any(ld in domain for ld in LEGITIMATE_DOMAINS),
            "has_suspicious_keywords": any(kw in domain + path for kw in ["login", "verify", "secure", "update", "confirm", "account"]),
            "url_length": len(url),
            "subdomain_count": len(domain.split(".")) - 2,
            "has_at_symbol": "@" in url,
            "has_double_slash": "//" in parsed.path,
        }
        features["risk_score"] = sum([
            features["has_ip"] * 3,
            features["suspicious_tld"] * 2,
            not features["is_legitimate_domain"] and features["has_suspicious_keywords"],
            features["has_at_symbol"] * 2,
            features["has_double_slash"],
            (features["url_length"] > 75),
            (features["subdomain_count"] > 2),
        ])
        return features
    except Exception:
        return {"risk_score": 0}


def detect_language(text: str) -> str:
    """Detect language: amharic, oromo, or english"""
    amharic_chars = len(re.findall(r'[\u1200-\u137F]', text))
    if amharic_chars > 2:
        return "amharic"

    oromo_markers = ["tti", "dha", "irra", "irraa", "keessa", "maaloo", "herregaa", "cuqaasi", "walgahii"]
    oromo_count = sum(1 for m in oromo_markers if m.lower() in text.lower())
    if oromo_count >= 2:
        return "oromo"

    return "english"


def preprocess_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r'http\S+', ' urltoken ', text)
    text = re.sub(r'\S+@\S+', ' emailtoken ', text)
    text = re.sub(r'\d+', ' numtoken ', text)
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def extract_risk_features(text: str) -> Dict[str, Any]:
    text_lower = text.lower()
    urls = extract_urls(text)

    keyword_hits = {}
    for category, keywords in RISK_KEYWORDS.items():
        hits = [kw for kw in keywords if kw in text_lower]
        if hits:
            keyword_hits[category] = hits

    url_risks = [analyze_url(url) for url in urls]
    max_url_risk = max((u.get("risk_score", 0) for u in url_risks), default=0)

    amharic_hits = [kw for kw in AMHARIC_RISK_KEYWORDS if kw in text]
    oromo_hits = [kw for kw in OROMO_RISK_KEYWORDS if kw.lower() in text.lower()]

    return {
        "keyword_hits": keyword_hits,
        "urls": urls,
        "url_risk_score": max_url_risk,
        "has_urls": len(urls) > 0,
        "amharic_risk_keywords": amharic_hits,
        "oromo_risk_keywords": oromo_hits,
        "exclamation_count": text.count("!"),
        "caps_ratio": sum(1 for c in text if c.isupper()) / max(len(text), 1),
        "language": detect_language(text),
    }


def build_explanation(features: Dict, prediction: str, lang: str = "english") -> List[str]:
    reasons = []

    if features["keyword_hits"].get("urgency"):
        reasons.append({
            "english": "Urgent language detected",
            "amharic": "አስቸኳይ ቃላት ተገኝተዋል",
            "oromo": "Jecha hatattamaa argame"
        }[lang])

    if features["keyword_hits"].get("threat"):
        reasons.append({
            "english": "Account threat/suspension language",
            "amharic": "የአካውንት ማስፈራሪያ ቃላት",
            "oromo": "Jecha doorsisa herregaa"
        }[lang])

    if features["keyword_hits"].get("reward"):
        reasons.append({
            "english": "Unrealistic reward/prize offer",
            "amharic": "ሐሰተኛ ሽልማት ቃላት",
            "oromo": "Badhaasa sobaa"
        }[lang])

    if features["url_risk_score"] > 2:
        reasons.append({
            "english": "Suspicious/malicious URL detected",
            "amharic": "አደገኛ ሊንክ ተገኝቷል",
            "oromo": "Liinkii shakkisiisaa argame"
        }[lang])

    if features["has_urls"] and features["url_risk_score"] == 0:
        reasons.append({
            "english": "Contains external links",
            "amharic": "የውጭ ሊንኮች አሉ",
            "oromo": "Liinkii alaa qaba"
        }[lang])

    if features["caps_ratio"] > 0.3:
        reasons.append({
            "english": "Excessive capitalization (shouting)",
            "amharic": "ከልክ ያለፈ ትልቅ ፊደል አጠቃቀም",
            "oromo": "Qubee guddaa baay'ee fayyadame"
        }[lang])

    if features["exclamation_count"] > 2:
        reasons.append({
            "english": "Multiple exclamation marks",
            "amharic": "ብዙ የቃለ አጋኖ ምልክቶች",
            "oromo": "Mallattoo dinqisiifannoo baay'ee"
        }[lang])

    if features["amharic_risk_keywords"]:
        reasons.append({
            "english": "Amharic phishing keywords detected",
            "amharic": "የአማርኛ ፊሺንግ ቃላት ተገኝተዋል",
            "oromo": "Jecha phishing Amaariffaa argame"
        }[lang])

    if features["oromo_risk_keywords"]:
        reasons.append({
            "english": "Oromo phishing keywords detected",
            "amharic": "የኦሮምኛ ፊሺንግ ቃላት ተገኝተዋል",
            "oromo": "Jecha phishing Oromoo argame"
        }[lang])

    if not reasons and prediction == "legitimate":
        reasons.append({
            "english": "No phishing indicators found",
            "amharic": "የፊሺንግ ምልክቶች አልተገኙም",
            "oromo": "Mallattoo phishing hin argamne"
        }[lang])

    return reasons
