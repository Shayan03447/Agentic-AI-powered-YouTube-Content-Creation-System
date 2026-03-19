import os
import json
import logging
from typing import Any
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

client=OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# ------Output shape for script agent --
DEFAULT_STRUCTURED_INSIGHTS = {
    "key_points": [],
    "hooks": [],
    "facts_or_stats": [],
    "angles": [],
    "cta_ideas": [],
}
def _build_sources_text(sources: list[dict]) -> str:
    """Turn research sources into one text block for the LLM"""
    parts = []
    for i, s in enumerate(sources or [], 1):
        title= (s or {}).get("title") or ""
        url= (s or {}).get("url") or ""
        content= (s or {}).get("content") or ""
        parts.append(f"[Source {i}] {title}\nURL: {url}\n{content}")
    return "\n\n---\n\n".join(parts)
def summarize_agent(research_result: dict[str, Any]) -> dict[str, Any]:
    """
    Consume research_agent output: return summary + structured insights for script agent.
    Input: dict with 'query' and 'sources' (list of {title, url, content}).
    """
    query= (research_result or {}).get("query") or ""
    sources= (research_result or {}).get("sources") or []
    sources_text = _build_sources_text(sources)
    sources_used=[s.get("url") or "" for s in sources if  s.get("url")]
    if not sources_text.strip():
        return {
            "query": query,
            "summary": "No source content available to summarize.",
            "structured_insights": dict(DEFAULT_STRUCTURED_INSIGHTS),
            "sources_used": sources_used,
        }
    system = """You are summarizing web research for a YouTube script writer.
Output valid JSON only, no markdown or extra text, with this exact structure:
{
  "summary": "2-4 sentence narrative summary of the research",
  "structured_insights": {
    "key_points": ["takeaway 1", "takeaway 2", ...],
    "hooks": ["opening/hook idea 1", ...],
    "facts_or_stats": ["fact or statistic 1", ...],
    "angles": ["story angle or POV 1", ...],
    "cta_ideas": ["call-to-action idea 1", ...]
  }
}
All list fields must be arrays of strings; use empty arrays if not applicable."""
    user_contet= f"Topic: {query}\n\nResearch content:\n{sources_text}"

    try:
        r=client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system","content":system},
                {"role": "user","content": user_contet},
            ],
            response_format={"type": "json_object"}
        )
        raw = (r.choices[0].message.content or "").strip()
        data= json.loads(raw) if raw else {}
    except Exception as e:
        logger.exception("Summarize LLM or JSON parse failed: %s", e)
        return {
            "query":query,
            "summary": f"Summarization failed: {e}",
            "structured_insights": dict(DEFAULT_STRUCTURED_INSIGHTS),
            "sources_used": sources_used,
        }
    summary = data.get("summary") or "No summary generated."
    si = data.get("structured_insights") or {}
    for k in DEFAULT_STRUCTURED_INSIGHTS:
        if k not in si or not isinstance(si[k], list):
            si[k]= DEFAULT_STRUCTURED_INSIGHTS[k]
    return {
        "query":query,
        "summary":summary,
        "structured_insights": si,
        "sources_used": sources_used,
    }       
if __name__ == "__main__":
    from agents.research_agent import research_agent
    test_query = "best practices for youtube video scripting 2024 "
    research_result= research_agent(test_query)
    out=summarize_agent(research_result)
    print(json.dumps(out, indent=2, default=str))







