import re


def validate_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def sanitize_input(text: str, max_length=None) -> str:
    if not text:
        return ''
    text = text.strip()
    if max_length:
        text = text[:max_length]
    return text
