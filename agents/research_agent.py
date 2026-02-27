import os
import json
from openai import OpenAI
from tools.tavily_tool import tavily_search
from dotenv import load_dotenv
load_dotenv()

client=OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def expand_query(user_query: str)-> list[str]:
    "LLM expend user query into 1-2 search query"
    r = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role":"user",
            "content":f"for youtube video research , expend this into 1-3 short search queries (one per line):\n {user_query}"
        }],  
    )
    text=r.choices[0].message.content or ""
    queries=[]
    for q in text.strip().split("\n"):
        q=q.strip().lstrip("-•0123456789.").strip()
        if q:
            queries.append(q)
    #queries=[q.strip() for q in text.strip().split("\n") if q.strip()][:3]
    return queries[:3] if queries else [user_query]

def filter_sources(results: list, max_sources: int=10)-> list[dict]:
    """Keep top results: each has title, url, content (tavily shape)"""
    out=[]
    seen=set()
    for r in results:
        url = (r or {}).get("url") or (r or {}).get("link")
        if not url:
            continue
        
        if any(bad in url for bad in ["youtube.com", "reddit.com"]):
            continue
        if url and url not in seen and len(out)<max_sources:
            seen.add(url)
            out.append({
                "title": (r or {}).get("title") or "",
                "url":url,
                "content": (r or {}).get("content") or (r or {}).get("snippet") or "",  
            })
    return out


def research_agent(user_query: str)-> dict:
    expanded=expand_query(user_query)
    all_results=[]
    for q in expanded:
        out=tavily_search(query=q, max_results=5)
        if not out.get("error") and out.get("results"):
            all_results.extend(out["results"])
    sources = filter_sources(all_results, max_sources=10)
    
    return {
        "query": user_query,
        "expanded_queries": expanded,
        "sources":sources,
        "project": "ai-powered-multi-agent-youtube-content-creation",    
    }
if __name__=="__main__":
    test_query="best practices for youtube video scripting 2024"
    result= research_agent(test_query)
    print(json.dumps(result, indent=2, default=str))

