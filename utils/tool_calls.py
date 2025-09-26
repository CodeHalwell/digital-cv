import json
import os
import requests
from utils.logging import setup_logging

logger = setup_logging()

def push(text):
    """Send a Pushover notification.

    Args:
        text: The message text to send.
    """
    try:
        logger.info(f"Sending Pushover notification: {text}")
        requests.post(
            "https://api.pushover.net/1/messages.json",
            data={
                "token": os.getenv("PUSHOVER_TOKEN"),
                "user": os.getenv("PUSHOVER_USER"),
                "message": text,
            },
            timeout=10,
        )
    except Exception as e:
        # Silently ignore notification failures to avoid impacting UX
        logger.error(f"Failed to send Pushover notification: {e}")
        pass


def record_user_details(email, name="Name not provided", notes="not provided"):
    """Record a user's contact details via push notification.

    Args:
        email: The user's email address.
        name: The user's name, if provided.
        notes: Additional context to record.

    Returns:
        A dictionary indicating success, e.g., {"recorded": "ok"}.
    """
    logger.info(f"Recording {name} with email {email} and notes {notes}")
    push(f"Recording {name} with email {email} and notes {notes}")
    return {"recorded": "ok"}

def record_unknown_question(question):
    """Record an unanswered user question via push notification.

    Args:
        question: The question that couldn't be answered.

    Returns:
        A dictionary indicating success, e.g., {"recorded": "ok"}.
    """
    logger.info(f"Recording {question}")
    push(f"Recording {question}")
    return {"recorded": "ok"}