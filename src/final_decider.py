import json
import re
from typing import Dict, List

import ollama

DECIDER_MODEL = "qwen3:4b-instruct"

_SYSTEM_PROMPT = """You are an elite Music Supervisor. Your job is to select the absolute best background track for a specific scene from a pre-filtered list of 5 candidate songs.

Instructions:
You will receive two pieces of JSON data:

Image_Profile: The visual and emotional data extracted from the scene.

Candidate_Songs: A list of 5 songs, complete with their metadata.

Evaluate the candidates against the image profile. You must strictly apply the following scoring rules during your evaluation:

Rule 1: The Epic Scale Bonus
If the Image_Profile has an intensity > 0.8 AND an action_level < 0.3, you must heavily prioritize songs that have tags indicating "Epic", "Trailer", "Heavy Brass", "Choral", or "Slow Tempo". This combination indicates a massive but slow-moving scene (e.g., a giant structure or creature).

Rule 2: The Mismatched Era Penalty (Critical)
If the Image_Profile has a visual_style, genre, or setting that indicates a historical era (e.g., "Period Drama", "Historical", "Medieval", "1800s"), you must strictly penalize and avoid any song containing tags like "Electronic", "Synth", "EDM", or "Modern Pop".

Output Requirements:
Return your final decision STRICTLY as a JSON object matching the exact structure below. Do not output any markdown formatting, conversational text, or explanations outside of the JSON structure.

{
  "selected_song_id": "string",
  "runner_up_song_id": "string",
  "applied_rules": [
    "List any specific rules like 'Epic Scale Bonus' or 'Mismatched Era Penalty' that influenced the decision, or 'None'."
  ],
  "reasoning": "A concise, 2-sentence professional explanation of why the selected song is the perfect fit for the image's specific tension, energy, and visual style."
}"""


def decide(image_profile: Dict, candidate_songs: List[Dict]) -> Dict:
    """
    Send the image profile and top candidate songs to the final AI decider.

    Args:
        image_profile: Output from vision_ai.analyze_image().
        candidate_songs: List of song dicts (up to 10) from recommend_songs().

    Returns:
        Dict with keys: selected_song_id, runner_up_song_id, applied_rules, reasoning.

    Raises:
        ValueError: If the model returns output that cannot be parsed as JSON.
    """
    user_message = json.dumps(
        {
            "Image_Profile": image_profile,
            "Candidate_Songs": candidate_songs,
        },
        indent=2,
    )

    response = ollama.chat(
        model=DECIDER_MODEL,
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
    )

    raw = response["message"]["content"].strip()

    # Strip markdown code fences if the model wrapped the JSON
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        raise ValueError(f"Model did not return valid JSON.\nRaw output:\n{raw}")

    return json.loads(match.group())
