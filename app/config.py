# app/config.py
import os

INTERNAL_API_BASE = os.getenv("INTERNAL_API_BASE", "http://127.0.0.1:5000")

HUBSPOT_BASE_URL = "https://api.hubapi.com"

HUBSPOT_TOKEN = os.getenv("HUBSPOT_TOKEN")

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")