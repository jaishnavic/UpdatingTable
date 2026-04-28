from dotenv import load_dotenv
import os

load_dotenv(override=True)  # 👈 add this

FUSION_BASE_URL = os.getenv("FUSION_BASE_URL")
FUSION_USERNAME = os.getenv("FUSION_USERNAME")
FUSION_PASSWORD = os.getenv("FUSION_PASSWORD")