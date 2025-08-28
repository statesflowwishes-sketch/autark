import re

SENSITIVE_PATTERNS = [
    r'API_KEY\s*=\s*["\'][A-Za-z0-9_\-]{16,}["\']',
    r'(?i)password\s*=\s*["\'].*?["\']',
    r'(?i)secret'
]

CODE_BLOCK = re.compile(r'```.*?```', re.DOTALL)

def sanitize_for_asset(prompt: str) -> str:
    # Entfernt Code-Blöcke komplett (keine Quellcode-Leaks)
    p = CODE_BLOCK.sub("[CODE_REMOVED]", prompt)
    for pat in SENSITIVE_PATTERNS:
        p = re.sub(pat, "[REDACTED]", p)
    return p[:4000]  # Hard Limit