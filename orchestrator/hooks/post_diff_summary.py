import logging
from integration.leap_client import LeapClient
log = logging.getLogger("post_diff_summary")

def summarize_diff(diff_text: str, leap_client: LeapClient, max_len: int = 6000) -> str:
    snippet = diff_text[:max_len]
    return leap_client.summarize(
        f"Provide a concise developer facing summary of this diff focusing on key architectural or functional changes:\n{snippet}"
    )