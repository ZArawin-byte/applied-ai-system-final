"""
AI-powered explanation and guardrail layer using the Google Gemini API.
"""

import logging
import os
from google import genai
from typing import List, Dict

logger = logging.getLogger(__name__)

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    return _client


def validate_user_profile(genre: str, mood: str, energy: float) -> tuple[bool, str]:
    """
    Use Gemini to check if the user profile values are reasonable.
    Returns (is_valid, message).
    """
    prompt = (
        f"A user entered this music preference profile:\n"
        f"- Genre: {genre}\n"
        f"- Mood: {mood}\n"
        f"- Energy level: {energy} (scale 0.0 to 1.0)\n\n"
        f"Valid genres are: pop, rock, lofi, jazz, electronic, ambient, classical, hiphop.\n"
        f"Valid moods are: happy, chill, intense, sad, romantic, energetic.\n"
        f"Energy must be between 0.0 and 1.0.\n\n"
        f"Reply with exactly one line: either 'VALID' or 'INVALID: <reason>'."
    )

    try:
        client = _get_client()
        logger.info("Validating user profile via Gemini: genre=%s mood=%s energy=%s", genre, mood, energy)
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
        )
        result = response.text.strip()
        logger.info("Profile validation result: %s", result)

        if result.startswith("VALID"):
            return True, "Profile looks good!"
        else:
            reason = result.replace("INVALID:", "").strip()
            return False, reason

    except Exception as e:
        logger.error("Gemini validation failed: %s", e)
        return True, "Validation unavailable — proceeding anyway."


def _fallback_explanation(genre: str, mood: str, energy: float, recommendations: List[Dict]) -> str:
    """Generate a rule-based explanation when the AI API is unavailable."""
    energy_desc = "high-energy" if energy > 0.6 else "mellow" if energy < 0.4 else "mid-tempo"
    top = recommendations[0] if recommendations else None
    opening = (
        f"Based on your love of {genre} and {mood} vibes, we found songs that match your "
        f"{energy_desc} preference (energy {energy:.2f}). "
        f"These tracks scored highest against your taste profile."
    )
    lines = [opening, ""]
    for r in recommendations:
        match_reasons = []
        if r["genre"] == genre:
            match_reasons.append(f"genre match ({r['genre']})")
        if r["mood"] == mood:
            match_reasons.append(f"mood match ({r['mood']})")
        energy_gap = abs(r["energy"] - energy)
        if energy_gap < 0.2:
            match_reasons.append(f"energy is very close to your target ({r['energy']:.2f})")
        reason = ", ".join(match_reasons) if match_reasons else f"solid overall score ({r['score']:.2f})"
        lines.append(f"• {r['title']}: {reason}.")
    return "\n".join(lines)


def explain_recommendations(
    genre: str,
    mood: str,
    energy: float,
    recommendations: List[Dict],
) -> str:
    """
    Use Gemini to generate a detailed natural-language explanation
    of why these songs were recommended for this user.
    """
    song_list = "\n".join(
        f"- {r['title']} by {r['artist']} (genre: {r['genre']}, mood: {r['mood']}, energy: {r['energy']:.2f}, score: {r['score']:.2f})"
        for r in recommendations
    )

    prompt = (
        f"You are a friendly music curator. A listener has these preferences:\n"
        f"- Favorite genre: {genre}\n"
        f"- Preferred mood: {mood}\n"
        f"- Energy level: {energy} (0.0 = very calm, 1.0 = very intense)\n\n"
        f"Our recommender system selected these songs for them:\n"
        f"{song_list}\n\n"
        f"Write a response with two parts:\n"
        f"1. A warm 2-sentence opening explaining overall why this playlist fits the listener's vibe.\n"
        f"2. For each song, one sentence explaining specifically why it was picked — mention its genre, mood, energy score, and how it matches the listener's preferences.\n"
        f"Format the per-song explanations as: '• Song Title: reason'.\n"
        f"Be conversational and specific, not generic."
    )

    try:
        client = _get_client()
        logger.info("Requesting AI explanation for %d recommendations", len(recommendations))
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
        )
        explanation = response.text.strip()
        logger.info("AI explanation generated successfully")
        return explanation

    except Exception as e:
        logger.error("Gemini explanation failed: %s", e)
        return _fallback_explanation(genre, mood, energy, recommendations)
