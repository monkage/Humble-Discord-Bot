"""Small text helpers shared by the services and commands."""


def trim(s: str, n: int) -> str:
    s = (s or "").strip()
    return s[:n] if len(s) > n else s


def format_sources(items: list[dict]) -> str:
    # Makes a numbered source list
    lines = []
    for i, it in enumerate(items, 1):
        t = trim(it.get("title") or it.get("url") or f"Source {i}", 90)
        u = it.get("url", "")
        lines.append(f"[{i}] {t} – {u}")
    return "\n".join(lines)
