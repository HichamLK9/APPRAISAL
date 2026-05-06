"""Sector classification via keyword matching."""
from typing import Dict, List

SECTOR_KEYWORDS: Dict[str, List[str]] = {
    "fintech": [
        "fintech", "payment", "payments", "wallet", "remittance",
        "insurtech", "trading", "broker", "neo-bank", "neobank",
        "lending", "mortgage", "credit", "loan", "invest", "wealthtech",
    ],
    "artificial_intelligence": [
        "artificial intelligence", "machine learning", "deep learning",
        "computer vision", "llm", "genai", "generative ai", "chatbot",
        "nlp", "neural", "predictive", " ai ", " ai,", "ai-",
    ],
    "digital_health_biotech": [
        "healthtech", "digital health", "telemedicine", "medtech",
        "biotech", "clinic", "medical", "pharma", "therapeutics",
        "genomics", "life science", "telehealth", "mental health",
    ],
    "cybersecurity": [
        "cyber", "cybersecurity", "infosec", "threat", "endpoint",
        "zero trust", "siem", "soc ", "identity", "authentication",
        "firewall", "vulnerability",
    ],
    "saas_cloud_infra": [
        "saas", "software as a service", "cloud", "kubernetes",
        "devops", "infrastructure", "data platform", "microservice",
        "api platform", "backend", "serverless",
    ],
    "ecommerce_marketplaces": [
        "e-commerce", "ecommerce", "marketplace", "online store",
        "dropship", "shop", "retail", "fulfillment", "d2c", "dtc",
    ],
    "real_estate_proptech": [
        "proptech", "real estate", "realtor", "property", "rental",
        "leasing", "mortgage tech", "reit", "realty",
    ],
    "cleantech_energy": [
        "cleantech", "solar", "wind", "battery", "electric vehicle",
        " ev ", "renewable", "climate", "carbon", "sustainability",
        "greentech", "energy storage",
    ],
    "fitness_wellness": [
        "fitness", "gym", "workout", "yoga", "wellness", "nutrition",
        "supplement", "athleisure", "sports", "crossfit", "pilates",
    ],
    "education_creator": [
        "edtech", "education", "e-learning", "elearning", "online course",
        "coaching", "creator", "content", "academy", "bootcamp",
        "curriculum", "tutoring",
    ],
}


def classify_sector(name: str, description: str, raw_sector: str) -> str:
    text = " ".join([name or "", description or "", raw_sector or ""]).lower()
    for sector, keywords in SECTOR_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                return sector
    return "other"
