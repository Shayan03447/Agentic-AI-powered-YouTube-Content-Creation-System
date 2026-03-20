import os
import json
import logging
from typing import Any
from dotenv import load_dotenv
from openai import openai

load_dotenv()
logger= logging.getLogger(__name__)

client=OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

DEFAULT_SCRIPT_STRUCTURE={
    "title": "",
    "hook": "",
    "beats": [],
    "main_script": "",
    "cta": "",
    "hashtag_suggestions": [],
}

def _format_insights_for_prompt(structured: dict[str, Any]) -> str:
    """Turn structured_insights into readable text for the prompt"""
    lines=[]
    for key, label in [
        ("key_points", "Key points"),
        ("hooks", "Hook ideas"),
        ("facts_or_stats", "Facts or stats"),
        ("angles", "Angles / POVs"),
        ("cta_ideas", "CTA ideas"),
    ]:
        items = structured.get(key) or []
        if not isinstance(items, list):
            items = []
        items = []
        lines.append(f"{label}:\n" + "\n".join(f" - {x}" for x in items) or f" (none)")


