from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/reviews", tags=["reviews"])

CATEGORIES = [
    "Positive",
    "Delayed Delivery",
    "Rider Behavior",
    "Damaged Goods",
    "Wrong Address",
    "Other"
]

class ReviewRequest(BaseModel):
    review: str
    order_id: Optional[int] = None

@router.post("/categorise")
async def categorise_review(body: ReviewRequest):
    if not os.getenv("GROQ_API_KEY"):
        raise HTTPException(status_code=500, detail="Groq API key not configured")
    if not body.review.strip():
        raise HTTPException(status_code=400, detail="Review text is empty")

    try:
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": """You are a customer feedback analyser for a hyperlocal delivery platform.
Categorise customer reviews into EXACTLY ONE of these categories:
- Positive
- Delayed Delivery
- Rider Behavior
- Damaged Goods
- Wrong Address
- Other

Reply with ONLY the category name. No punctuation, no explanation, no extra words."""
                },
                {
                    "role": "user",
                    "content": f'Categorise this review: "{body.review}"'
                }
            ],
            temperature=0,
            max_tokens=20,
        )

        category = response.choices[0].message.content.strip()

        if category not in CATEGORIES:
            category = "Other"

        return {
            "review":   body.review,
            "category": category,
            "order_id": body.order_id,
            "icon":     _icon(category)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Categorisation failed: {str(e)}")

def _icon(category: str) -> str:
    return {
        "Positive":         "✅",
        "Delayed Delivery": "⏰",
        "Rider Behavior":   "🏍",
        "Damaged Goods":    "📦",
        "Wrong Address":    "❌",
        "Other":            "🔁"
    }.get(category, "🔁")