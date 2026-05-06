"""Demo / seed data generator.

Generates realistic synthetic entities for testing the full stack without
needing live API access.  Enable with: ENABLED_SOURCES=mock

Set MOCK_ENTITY_COUNT (default 100) to control how many entities are generated.
"""
import datetime as dt
import hashlib
import os
import random

from . import register
from .base import NewEntity

_NAMES = [
    "NovaPay", "CloudStack", "GreenLeaf Energy", "MindBridge AI",
    "HealthPulse", "SecureEdge", "PropLink", "FitForge", "EduPath",
    "Swiftly Commerce", "QuantumSoft", "TerraShield", "MedAssist",
    "DataVault", "MarketNest", "SolarMind", "CyberGate", "YogaFlow",
    "CoachNow", "ReaLink", "WalletX", "BrainAI", "FitHub", "CloudBase",
    "LendBridge", "AgriTech", "SafePass", "NestProp", "CodeCraft",
    "InfraNode", "MedLoop", "TradePoint", "ShopGrid", "CourseWave",
    "SmartHome", "ClearSky", "GrowthAI", "PaySwift", "BioGen",
    "CyberShield", "SpaceStack", "EcoGrid", "PetCare", "FreshMind",
    "TurboShip", "OpenFinance", "LearnFast", "RentWise", "SunPower",
    "PulseHealth",
]

_SUFFIXES = ["LLC", "Inc", "Corp", "Technologies LLC", "Solutions Inc", "Group LLC",
             "AI Inc", "Tech LLC", "Services LLC", "Holdings Corp"]

_DESCRIPTIONS = [
    "Fintech payment processing platform",
    "AI-powered analytics software",
    "Digital health monitoring system",
    "Cybersecurity endpoint protection",
    "Cloud infrastructure management",
    "E-commerce marketplace solution",
    "Real estate technology platform",
    "Clean energy management system",
    "Fitness coaching application",
    "Online education platform",
    "Machine learning data pipeline",
    "SaaS business automation tool",
    "Blockchain payment gateway",
    "Telemedicine consultation service",
    "Solar panel management software",
    "Property rental management",
    "Supplement e-commerce store",
    "Yoga and wellness coaching",
    "Corporate training academy",
    "Cyber threat intelligence",
]

_NAICS_CODES = [
    "541511", "541512", "519130", "524210", "522190",
    "621111", "531210", "236118", "713940", "611710",
    "336111", "221114", "517311", "541690", "454110",
]

_JURISDICTIONS = ["HI", "CT", "CA", "WY", "NY", "TX", "FL", "WA", "CO", "IL"]

_SOURCE = "mock://demo-data-generator"


def _seed_random(seed_str: str) -> random.Random:
    seed = int(hashlib.md5(seed_str.encode()).hexdigest()[:8], 16)
    return random.Random(seed)


@register("mock")
def fetch_from_mock(limit: int = 100) -> list[NewEntity]:
    count = int(os.environ.get("MOCK_ENTITY_COUNT", limit))
    today = dt.date.today()
    entities: list[NewEntity] = []

    for i in range(count):
        rng = _seed_random(f"{today.isoformat()}-{i}")

        # Spread filings over the last 45 days, cluster heavily on last 3
        age_weights = [40, 30, 20] + [1] * 42  # last 3 days get most weight
        age = rng.choices(range(45), weights=age_weights[:45], k=1)[0]
        date = (today - dt.timedelta(days=age)).isoformat()

        name = f"{rng.choice(_NAMES)} {rng.choice(_SUFFIXES)}"
        description = rng.choice(_DESCRIPTIONS)
        jurisdiction = rng.choice(_JURISDICTIONS)
        raw_sector = rng.choice(_NAICS_CODES)

        entities.append(
            NewEntity(
                name=name,
                description=description,
                date=date,
                jurisdiction=jurisdiction,
                raw_sector=raw_sector,
                source=_SOURCE,
                entity_type=rng.choice(["LLC", "Corporation", "S-Corp", "Sole Prop"]),
            )
        )

    return entities
