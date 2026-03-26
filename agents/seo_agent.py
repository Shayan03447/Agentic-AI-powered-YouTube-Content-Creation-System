import json
import logging
import os
import re
from collection import Counter
from typing import Any
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
logger=logging.getLogger(__name__)
client= OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

DEFAULT_SEO_STRUCTURE={
    "title_variants":[],
    "best_title":"",
    "description":"",
    "keywords":[],
    "tags":[],
    "hashtags":[],
    "pinned_comment":"",
    "thumbnail_text_options": [],
    "filename_suggestions":[],
    "metadata_checks":[],
}

STOPWORDS= {
    "the", "a", "an", "and", "or", "to", "of", "in" , "on", "for", "with",
    "from", "be", "under", "is", "are", "this", "that", "it", "as", "at", "by",
    "you", "your", "we", "our", "about", "into", "over", "under"

}
def _safe_tex(value: Any) -> str:
    return str(value or "").strip()

def _slugify(text: str) -> str:
    slug=re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug or "youtube-short"

def _tokenize(text: str)-> list[str]:
    words = re.findall(r"[a-zA-Z0-9']+", (text or "").lower())
    return [w for w in words if len(w) > 2 and w not in STOPWORDS]

def _dedup_str_list(values: list[Any], max_items: int) -> list[str]:
    out: list[str] = []
    seen= set()
    for items in values or []:
        if not isinstance(items, str):
            continue
        s = items.strip()
        if not s:
            continue
        low = s.lower()
        if low in seen:
            continue
        seen.add(low)
        out.append(s)
        if len(out) >= max_items:
            break
    return out