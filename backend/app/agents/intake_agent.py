import json
import os
import base64
from . import BaseAgent
from app.config import settings
from app.services.qwen_client import chat, get_client

SYSTEM_PROMPT = """You are an Intake Agent for an insurance claims processing system.
Your job is to extract structured information from a raw claim submission.

Given a claim submission with free-text description and optional details, extract:
1. claimant_name: Full name of the claimant
2. claimant_email: Email address
3. claimant_phone: Phone number (if available)
4. policy_number: The policy number referenced
5. claim_type: One of: auto, home, health, travel, property, liability, other
6. description: A clean, structured summary of the incident
7. incident_date: When the incident occurred (YYYY-MM-DD format)
8. location: Where the incident occurred (if available)
9. estimated_loss: Estimated financial loss amount (number, or null if unclear)
10. confidence: Your confidence score (0.0-1.0) in the extraction
11. missing_fields: List of fields that are missing or unclear
12. flags: Any concerns (e.g., "ambiguous description", "missing policy number")

Output as JSON with these exact field names."""

VISION_PROMPT = """You are an AI insurance claims assessor analyzing damage photos.
Examine the image(s) carefully and extract:

1. damage_type: Type of damage visible (e.g., "collision", "fire", "water", "storm", "break-in", "none visible")
2. damage_severity: Estimated severity (minor, moderate, severe, total_loss)
3. visible_parts: List of damaged parts/components visible (e.g., "bumper", "windshield", "roof", "wall", "window")
4. estimated_repair_cost: Rough estimate of repair cost based on visible damage
5. weather_indicators: Any weather-related evidence (rain, hail, snow, etc.)
6. fraud_indicators: Any signs of potential fraud (e.g., "pre-existing damage", "inconsistent damage patterns")
7. confidence: Your confidence score in the visual analysis (0.0-1.0)
8. summary: One-sentence summary of what the image shows

Output as JSON with these exact field names."""


class IntakeAgent(BaseAgent):
    name = "intake"
    model = settings.qwen_model_plus

    def __init__(self):
        super().__init__()
        self.system_prompt = SYSTEM_PROMPT

    def analyze_images(self, image_paths: list[str]) -> dict:
        if not image_paths:
            return {"photos_analyzed": 0, "photo_analysis": None}

        results = []
        UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")

        for path in image_paths:
            filename = path.replace("/uploads/", "")
            filepath = os.path.join(UPLOAD_DIR, filename)
            if not os.path.exists(filepath):
                continue
            try:
                with open(filepath, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode("utf-8")

                ext = os.path.splitext(filename)[1].lower()
                mime = "image/jpeg"
                if ext == ".png":
                    mime = "image/png"
                elif ext == ".webp":
                    mime = "image/webp"

                data_url = f"data:{mime};base64,{b64}"

                client = get_client()
                response = client.chat.completions.create(
                    model=self.model,
                    messages=[{
                        "role": "user",
                        "content": [
                            {"type": "text", "text": VISION_PROMPT},
                            {"type": "image_url", "image_url": {"url": data_url}},
                        ],
                    }],
                    response_format={"type": "json_object"},
                )
                analysis = json.loads(response.choices[0].message.content)
                analysis["filename"] = filename
                results.append(analysis)
            except Exception as e:
                results.append({"filename": filename, "error": str(e)})

        if not results:
            return {"photos_analyzed": 0, "photo_analysis": None}

        merged = {
            "photos_analyzed": len(results),
            "photo_analysis": results,
            "all_confidence": min(r.get("confidence", 0) for r in results if "error" not in r) if results else 0,
        }
        return merged

    async def run(self, context: dict) -> dict:
        claim = context.get("claim", {})
        messages = self.build_messages(context)

        parsed = chat_json(self.model, messages, temperature=0.2)

        raw_paths = claim.get("image_paths", "[]")
        if isinstance(raw_paths, str):
            image_paths = json.loads(raw_paths)
        elif isinstance(raw_paths, list):
            image_paths = raw_paths
        else:
            image_paths = []

        if image_paths:
            photo_data = self.analyze_images(image_paths)
            parsed["photo_analysis"] = photo_data["photo_analysis"]
            parsed["photos_analyzed"] = photo_data["photos_analyzed"]
            if photo_data.get("all_confidence"):
                parsed["confidence"] = min(parsed.get("confidence", 1.0), photo_data["all_confidence"])

        return parsed
