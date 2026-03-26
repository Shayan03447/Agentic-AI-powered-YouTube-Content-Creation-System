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
    beats should be 4-8 short items; main_script should flow naturally when read aloud
    """
        user=f"""Topic : {query}
    
    summary:
    {summary}

    structured insights
    {insights_text}

    source URLs (for your awareness only; do not read the web):
    {json.dumps(sources_used, ensure_ascii=False)}
    """

    try:
         r=client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system","content": system},
                {"role": "user", "content": user},
            ],
            response_format={"type": "json_object"},
        )
        raw=(r.choice[0].message.content or "").strip()
        data=json.loads(raw) if raw else {}
    except Exception as e:
        logger.exception("Script LLM or JSON parse failed: %s")
        return {
            "query":query,
            "error": str(e),
            "script_json": dict(DEFAULT_SCRIPT_STRUCTURE),
            "sources_used": sources_used,
        }
    out = dict(DEFAULT_SCRIPT_STRUCTURE)
    for k in out:
        if k in data and data[k] is not None:
            out[k]= data[k]
    if not isinstance(out["beats"], list):
        out["beats"]=[]

    return {
        "query":query,
        "script_json": out,
        "main_script": out.get("main_script") or "",
        "sources_used": sources_used,
    }

if __name__ == "__main__":
    from agents.research_agent import research_agent
    from agents.summerize_agent import summarize_agent

    q= "best practice for youtube video scripting 2024"
    research= research_agent(q)
    summarized= summarize_agent(research)
    script = script_agent(summarized)
    print(json.dump(script, indent=2, ensure_ascii=False))


