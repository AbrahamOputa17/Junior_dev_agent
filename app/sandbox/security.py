import os
from typing import Dict
from app.sandbox.limits import SENSITIVE_ENV_KEYS

def get_sanitized_env() -> Dict[str, str]:
    """
    Returns a copy of environment variables with sensitive tokens and keys masked.
    """
    clean_env = os.environ.copy()
    for key in list(clean_env.keys()):
        if any(sens in key.upper() for sens in SENSITIVE_ENV_KEYS):
            clean_env[key] = "[MASKED_IN_SANDBOX]"
    return clean_env
