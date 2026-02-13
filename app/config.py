# app/config.py
import os

INTERNAL_API_BASE = "http://192.168.1.107:8000"

HUBSPOT_BASE_URL = "https://api.hubapi.com"

HUBSPOT_TOKEN =os.getenv("HUBSPOT_TOKEN")


REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

SECRET_KEY = os.getenv("SECRET_KEY")
