from app.core.state_store import state_store


def start_greeting() -> dict:
    return state_store.start_greeting()