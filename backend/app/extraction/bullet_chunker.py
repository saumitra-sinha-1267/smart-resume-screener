import re
from typing import List

BULLET_SPLIT_REGEX = r"(?:\r?\n\s*[\u2022\u2023\u25E6\u2043\u2219\u25AA\u25CF\-\u2013\u2014\*]\s*|\r?\n\s*\d+[\.\)]\s*|\r?\n\s*;\s*|\r?\n{2,})"

def split_into_bullets(text: str) -> List[str]:
    if not text or not text.strip():
        return []
    cleaned = text.strip()
    parts = re.split(BULLET_SPLIT_REGEX, cleaned)
    bullets: List[str] = []
    for p in parts:
        p_clean = p.strip()
        p_clean = re.sub(r"^[\u2022\u2023\u25E6\u2043\u2219\u25AA\u25CF\-\u2013\u2014\*\d\.\)\s]+", "", p_clean).strip()
        if len(p_clean) > 12:
            p_clean = " ".join(p_clean.split())
            bullets.append(p_clean)
    if len(bullets) <= 1 and len(cleaned.splitlines()) > 2:
        for line in cleaned.splitlines():
            line_clean = line.strip()
            line_clean = re.sub(r"^[\u2022\u2023\u25E6\u2043\u2219\u25AA\u25CF\-\u2013\u2014\*\d\.\)\s]+", "", line_clean).strip()
            if len(line_clean) > 12:
                bullets.append(line_clean)
    return bullets
