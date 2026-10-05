"""Exa search client + highlight fetching for /web.

If the key or the package is missing, the client is None so the bot still runs.
"""
import re

from mybot import config
from mybot.utils import trim

try:
    from exa_py import Exa
except Exception as e:
    print(f"[Exa import error] {type(e).__name__}: {e}")
    Exa = None  # so references below don't crash

try:
    exa = Exa(api_key=config.EXA_API_KEY) if (Exa and config.EXA_API_KEY) else None
except Exception as e:
    print(f"[Exa init error] {type(e).__name__}: {e}")
    exa = None


def fetch_highlights(query: str, k: int, per_url: int) -> tuple[list[dict], str]:
    if exa is None:
        return [], "Exa is not configured. Set EXA_API_KEY in .env."

    q = trim(query, 300)

    try:
        # 1) Search
        s = exa.search(q, num_results=k, use_autoprompt=True)
        results = getattr(s, "results", None) or getattr(s, "documents", None) or []
        ids, index = [], {}
        for doc in results:
            # support attr- and dict-style
            did   = getattr(doc, "id", None) or (doc.get("id") if isinstance(doc, dict) else None)
            title = getattr(doc, "title", None) or (doc.get("title") if isinstance(doc, dict) else None)
            url   = getattr(doc, "url", None)   or (doc.get("url") if isinstance(doc, dict) else None)
            if did and url:
                ids.append(did)
                index[did] = {"title": title or url, "url": url, "clips": []}
        if not ids:
            return [], "No results."

        # 2) Try to fetch highlights (shape varies by version)
        try:
            c = exa.get_contents(
                ids,
                highlights={
                    "highlights_per_url": per_url,
                    "highlight_character_limit": config.EXA_HIGHLIGHT_CHAR_CAP,
                },
            )
            c_docs = getattr(c, "results", None) or getattr(c, "documents", None) or []
            for d in c_docs:
                did = getattr(d, "id", None) or (d.get("id") if isinstance(d, dict) else None)
                hl  = getattr(d, "highlights", None) or (d.get("highlights") if isinstance(d, dict) else None)
                if did in index and isinstance(hl, list):
                    clips = []
                    for h in hl[:per_url]:
                        snippet = (
                            getattr(h, "snippet", None)
                            or getattr(h, "text", None)
                            or (h.get("snippet") if isinstance(h, dict) else None)
                            or (h.get("text") if isinstance(h, dict) else None)
                        )
                        if snippet:
                            clips.append(trim(snippet, config.EXA_HIGHLIGHT_CHAR_CAP))
                    index[did]["clips"] = clips

        except Exception:
            # 3) Fallback: fetch raw text and make simple clips
            try:
                c = exa.get_contents(ids, text=True)
            except Exception:
                c = None
            c_docs = getattr(c, "results", None) or getattr(c, "documents", None) or []
            for d in c_docs:
                did = getattr(d, "id", None) or (d.get("id") if isinstance(d, dict) else None)
                txt = getattr(d, "text", None) or (d.get("text") if isinstance(d, dict) else "")
                if did in index and txt:
                    # naive sentence clips
                    sents = re.split(r'(?<=[.!?])\s+', txt)
                    index[did]["clips"] = [trim(s, config.EXA_HIGHLIGHT_CHAR_CAP) for s in sents[:per_url]]

        items = list(index.values())
        return items, ""

    except Exception as e:
        return [], f"Exa error: {type(e).__name__}: {e}"
