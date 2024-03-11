"""
    Text helper functions
"""


def abbrev(text, length=50):
    """Abbreviate text to a certain length."""
    if len(text) > length:
        return text[:length] + "..."

    return text
