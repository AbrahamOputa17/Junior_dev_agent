import re
from typing import List, Tuple

# Common regex patterns for secret detection
SECRET_PATTERNS: List[Tuple[str, re.Pattern]] = [
    ("OpenAI API Key", re.compile(r"sk-[a-zA-Z0-9]{32,}", re.IGNORECASE)),
    ("GitHub Token", re.compile(r"gh[pousr]_[a-zA-Z0-9]{36,}", re.IGNORECASE)),
    ("AWS Key ID", re.compile(r"AKIA[0-9A-Z]{16}", re.IGNORECASE)),
    ("AWS Secret Key", re.compile(r"(?i)aws_secret_access_key\s*=\s*['\"]?[A-Za-z0-9/+=]{40}['\"]?")),
    ("Generic Bearer Token", re.compile(r"Bearer\s+[a-zA-Z0-9\-\._~\+\/]+=*", re.IGNORECASE)),
    ("Private Key", re.compile(r"-----BEGIN (RSA|EC|DSA|OPENSSH) PRIVATE KEY-----[\s\S]*?-----END \1 PRIVATE KEY-----")),
    ("Generic Password/Secret Field", re.compile(r"(?i)(password|secret|api_key|access_token)\s*=\s*['\"]([^'\"]+)['\"]"))
]

def scan_and_redact_secrets(content: str) -> str:
    """
    Scans content for sensitive credentials and replaces them with redaction placeholders.
    """
    if not content:
        return content

    redacted = content
    for name, pattern in SECRET_PATTERNS:
        if name == "Generic Password/Secret Field":
            # Redact only the value part
            def redact_val(match):
                prefix = match.group(1)
                return f'{prefix}="[REDACTED_SECRET]"'
            redacted = pattern.sub(redact_val, redacted)
        else:
            redacted = pattern.sub(f"[REDACTED_{name.upper().replace(' ', '_')}]", redacted)
            
    return redacted
