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
        lines.append(f"{label}:\n" + "\n".join(f" - {x}" for x in items) or f" (none)")
    return "\n\n".join(lines)

def script_agent_langchain(summarize_output: dict[str, Any]) -> dict[str,Any]:
    query=(summarize_output or {}).get("query") or ""
    summary=(summarize_output or {}).get("summary") or ""
    structured=(summarize_output or {}).get("structured_insights") or {}
    sources_used=(summarize_output or {}).get("sources_used") or []
    insights_text=_format_insights_for_prompt(structured)

    system="""You write tight, engaging SHORT-FOAM  youtube scripts (roughly 60-90 seconds spoken).
    USe only the provided summary and structured insights; do not invent new factual claims..
    if a fact is missing, speak in general terms or skip it .

    Return valid json only, no markdown, with this shape:
    {
    "title":"catchy working title",
    "hook":"first 5-15 seconds, spoken",
    "beats":["beat 1 line", "beat 2 line", "....."],
    "main_script":"full continuous script the host reads",
    "cta":"subscribe/comment/link line",
    "hashtag_suggestions":["#tag1", "#tag2"]
    }

    """

