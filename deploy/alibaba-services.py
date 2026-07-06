"""
AutoClaims - Alibaba Cloud Services Integration

This file demonstrates the use of Alibaba Cloud services for the AutoClaims
project, required for Proof of Alibaba Cloud Deployment.

Services Used:
1. Alibaba Cloud ECS - Hosting the backend API server
2. Alibaba Cloud OSS - Storing claim documents and images
3. Alibaba Cloud RDS - PostgreSQL database for production
4. Qwen Cloud API (via Alibaba Cloud Model Studio) - AI model inference

To configure:
  pip install alibabacloud-ecs20140526 alibabacloud-oss2
  Set environment variables:
    ALIBABA_CLOUD_ACCESS_KEY_ID
    ALIBABA_CLOUD_ACCESS_KEY_SECRET
    ALIBABA_CLOUD_REGION (e.g., us-east-1)
"""

import os
import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# ============================================================
# 1. Alibaba Cloud OSS - Document Storage
# ============================================================

try:
    import oss2
except ImportError:
    oss2 = None
    logger.warning("oss2 not installed. Install with: pip install oss2")


class AlibabaOSS:
    """Store claim documents and images in Alibaba Cloud OSS."""

    def __init__(self):
        self.bucket_name = os.getenv("OSS_BUCKET_NAME", "autoclaims-docs")
        self.endpoint = os.getenv("OSS_ENDPOINT", "oss-us-east-1.aliyuncs.com")
        self.access_key_id = os.getenv("ALIBABA_CLOUD_ACCESS_KEY_ID", "")
        self.access_key_secret = os.getenv("ALIBABA_CLOUD_ACCESS_KEY_SECRET", "")

        if oss2 and self.access_key_id:
            auth = oss2.Auth(self.access_key_id, self.access_key_secret)
            self.bucket = oss2.Bucket(auth, self.endpoint, self.bucket_name)
            logger.info(f"OSS initialized: {self.bucket_name}")
        else:
            self.bucket = None
            logger.info("OSS not configured (using local storage fallback)")

    def upload_document(self, claim_id: int, filename: str, data: bytes) -> Optional[str]:
        """Upload a document to OSS. Returns URL or None."""
        if not self.bucket:
            return None
        key = f"claims/{claim_id}/{filename}"
        try:
            self.bucket.put_object(key, data)
            url = f"https://{self.bucket_name}.{self.endpoint}/{key}"
            logger.info(f"Uploaded to OSS: {url}")
            return url
        except Exception as e:
            logger.error(f"OSS upload failed: {e}")
            return None

    def get_document_url(self, claim_id: int, filename: str) -> Optional[str]:
        """Get a presigned URL for a document."""
        if not self.bucket:
            return None
        key = f"claims/{claim_id}/{filename}"
        try:
            return self.bucket.sign_url("GET", key, 3600)
        except Exception as e:
            logger.error(f"OSS get URL failed: {e}")
            return None


# ============================================================
# 2. Alibaba Cloud RDS - Production Database
# ============================================================

class AlibabaRDS:
    """Use Alibaba Cloud RDS PostgreSQL for production data."""

    def __init__(self):
        self.host = os.getenv("RDS_HOST", "")
        self.port = int(os.getenv("RDS_PORT", "5432"))
        self.database = os.getenv("RDS_DATABASE", "autoclaims")
        self.username = os.getenv("RDS_USERNAME", "")
        self.password = os.getenv("RDS_PASSWORD", "")

    @property
    def connection_string(self) -> str:
        """Get SQLAlchemy connection string for RDS."""
        if not self.host:
            return "sqlite:///./autoclaims.db"
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"


# ============================================================
# 3. Qwen Cloud API (via Alibaba Cloud Model Studio)
# ============================================================

class QwenCloudService:
    """
    Qwen Cloud API integration.

    API Base URL: https://dashscope-intl.aliyuncs.com/compatible-mode/v1
    This is an OpenAI-compatible API hosted on Alibaba Cloud infrastructure.
    """

    API_BASE = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"

    def __init__(self, api_key: str):
        self.api_key = api_key
        logger.info(f"Qwen Cloud API configured at {self.API_BASE}")

    def get_model_info(self) -> dict:
        """Return which Qwen models are being used and their purposes."""
        return {
            "models": {
                "qwen3.7-max": {
                    "purpose": "Complex reasoning and decision making",
                    "used_by": ["Validation Agent", "Assessment Agent", "Review Gate"],
                },
                "qwen3.7-plus": {
                    "purpose": "Vision understanding and balanced text generation",
                    "used_by": ["Intake Agent"],
                },
                "qwen3.6-flash": {
                    "purpose": "Fast, cost-effective text generation",
                    "used_by": ["Resolution Agent"],
                },
            },
            "api_base": self.API_BASE,
            "deployment": "Alibaba Cloud Model Studio (Bailian)",
        }


# ============================================================
# Initialization
# ============================================================

def init_alibaba_services():
    """Initialize all Alibaba Cloud services."""
    return {
        "oss": AlibabaOSS(),
        "rds": AlibabaRDS(),
        "qwen": QwenCloudService(api_key=os.getenv("QWEN_API_KEY", "")),
        "region": os.getenv("ALIBABA_CLOUD_REGION", "us-east-1"),
    }


if __name__ == "__main__":
    services = init_alibaba_services()
    print(json.dumps({
        "alibaba_services": {
            "oss_configured": services["oss"].bucket is not None,
            "rds_configured": bool(services["rds"].host),
            "qwen_configured": bool(services["qwen"].api_key),
            "region": services["region"],
        },
        "qwen_models": services["qwen"].get_model_info(),
        "note": "This demonstrates Alibaba Cloud service integration for Proof of Deployment.",
    }, indent=2))
