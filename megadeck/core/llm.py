"""Multi-provider LLM client.

Picks the available provider in this order: Anthropic → OpenAI → Google.
Uses `instructor` to guarantee the response is a valid `Deck` instance.
"""
from __future__ import annotations

import os
from typing import Literal, Optional

from megadeck.core.prompts import generation_system_prompt
from megadeck.core.schemas import Deck


Provider = Literal["anthropic", "openai", "google", "auto"]


# Default model per provider. Pinned to ones available in May 2026.
_DEFAULT_MODELS = {
    "anthropic": "claude-sonnet-4-5-20250929",
    "openai": "gpt-4o-2024-11-20",
    "google": "gemini-2.5-pro",
}


def _resolve_provider(requested: Provider) -> str:
    if requested != "auto":
        return requested
    if os.environ.get("ANTHROPIC_API_KEY"):
        return "anthropic"
    if os.environ.get("OPENAI_API_KEY"):
        return "openai"
    if os.environ.get("GOOGLE_API_KEY"):
        return "google"
    raise RuntimeError(
        "No LLM API key found. Set ANTHROPIC_API_KEY, OPENAI_API_KEY, or "
        "GOOGLE_API_KEY in your environment."
    )


def _build_user_prompt(prompt: str, n_slides: int, theme: str) -> str:
    return (
        f"Build a presentation deck.\n\n"
        f"Theme to use: {theme}\n"
        f"Target number of slides: {n_slides}\n\n"
        f"Brief / requirements:\n{prompt.strip()}\n"
    )


def generate_deck(
    prompt: str,
    *,
    n_slides: int = 20,
    theme: str = "default",
    provider: Provider = "auto",
    model: Optional[str] = None,
) -> Deck:
    """Call an LLM with a constrained schema and return a validated Deck."""
    provider_name = _resolve_provider(provider)
    model = model or _DEFAULT_MODELS[provider_name]
    system = generation_system_prompt()
    user = _build_user_prompt(prompt, n_slides, theme)

    if provider_name == "anthropic":
        return _generate_anthropic(system, user, model)
    if provider_name == "openai":
        return _generate_openai(system, user, model)
    if provider_name == "google":
        return _generate_google(system, user, model)
    raise RuntimeError(f"Unknown provider {provider_name!r}")


def _generate_anthropic(system: str, user: str, model: str) -> Deck:
    import instructor
    from anthropic import Anthropic

    client = instructor.from_anthropic(Anthropic())
    return client.messages.create(  # type: ignore[return-value]
        model=model,
        max_tokens=8192,
        system=system,
        messages=[{"role": "user", "content": user}],
        response_model=Deck,
    )


def _generate_openai(system: str, user: str, model: str) -> Deck:
    import instructor
    from openai import OpenAI

    client = instructor.from_openai(OpenAI())
    return client.chat.completions.create(  # type: ignore[return-value]
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        response_model=Deck,
    )


def _generate_google(system: str, user: str, model: str) -> Deck:
    try:
        import google.generativeai as genai
    except ImportError as e:
        raise RuntimeError(
            "Google provider requires `pip install megadeck[google]`."
        ) from e
    import instructor

    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
    client = instructor.from_gemini(
        client=genai.GenerativeModel(model_name=model, system_instruction=system),
        mode=instructor.Mode.GEMINI_JSON,
    )
    return client.create(  # type: ignore[return-value]
        messages=[{"role": "user", "content": user}],
        response_model=Deck,
    )
