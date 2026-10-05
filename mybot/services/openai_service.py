"""OpenAI client + the two prompts the bot uses (/ask answers and /web summaries).

If the key or the package is missing, the client is None so the bot still runs.
"""
from mybot import config
from mybot.utils import trim, format_sources

try:
    from openai import OpenAI
    oa = OpenAI(api_key=config.OPENAI_API_KEY) if config.OPENAI_API_KEY else None
except Exception:
    oa = None


def ai_concise(question: str) -> str:
    """Call OpenAI once with our 'concise' house style and safe limits."""
    if oa is None:
        return "OpenAI API not configured. Set OPENAI_API_KEY in your .env."

    q = (question or "").strip()
    if not q:
        return "Please ask a non-empty question."

    q = q[:config.MAX_INPUT_CHARS]  # cheap & fast
    try:
        resp = oa.chat.completions.create(
            model=config.MODEL,
            messages=[
                {"role": "system", "content": config.SYSTEM_CONCISE},
                {"role": "user",   "content": q},
            ],
            max_tokens=config.MAX_OUTPUT_TOKENS,
            temperature=0.4,
            timeout=20,  # seconds: guard against hanging calls
        )
        if not resp.choices or not getattr(resp.choices[0], "message", None) \
            or resp.choices[0].message.content is None:
            return "Sorry, I couldn’t generate a response."
        return resp.choices[0].message.content.strip() or "Sorry, the response was empty."
    except Exception:
        return "The AI is unavailable right now. Please try again in a moment."


def summarize_with_citations(question: str, items: list[dict]) -> str:
    """
    Build a compact context from highlights and ask OpenAI to summarize with [n] citations.
    """
    if oa is None:
        return "OpenAI not configured. Set OPENAI_API_KEY."

    # Build a numbered context like: [1] clip… [2] clip…
    ctx_parts = []
    for i, it in enumerate(items, 1):
        clips = it.get("clips") or []
        if not clips:
            continue
        joined = " ".join(clips)
        ctx_parts.append(f"[{i}] {joined}")
    context = " ".join(ctx_parts)
    context = trim(context, config.EXA_TOTAL_CLIP_CHAR_CAP)

    sources_block = format_sources(items) if items else "(No sources found)"

    prompt = (
        "You are a research assistant for a study group. "
        "You are given multiple source snippets with numbered tags like [1], [2], etc. "
        "Write a concise answer (4–7 sentences) that *only* uses information from those snippets. "
        "Use bracket citations inline, e.g., “X is true [2].” If sources disagree, note it briefly. "
        "Then add 3–5 bullet notes (actionable facts) and a short 'Why it matters' sentence. "
        "Do not invent facts; if evidence is weak, say so briefly."
    )

    user = (
        f"Question:\n{trim(question, 500)}\n\n"
        f"Snippets (keep their numbers when citing):\n{context}\n\n"
        f"Sources:\n{sources_block}"
    )

    try:
        resp = oa.chat.completions.create(
            model=config.MODEL,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user},
            ],
            temperature=0.3,
            max_tokens=config.SUMMARIZER_MAX_TOKENS,
            timeout=25,
        )
        msg = getattr(resp.choices[0], "message", None)
        return (msg.content or "").strip() if msg and msg.content else "Couldn’t generate a summary."
    except Exception:
        return "Summarizer is unavailable right now."
