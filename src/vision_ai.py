import json
import re
import base64
from pathlib import Path
from typing import Dict

import ollama

VISION_MODEL = "qwen3-vl:8b-instruct-q4_K_M"

_PROMPT = """You are an expert music supervisor and visual analyst. Analyze the provided image and determine the ideal background music characteristics to accompany this scene.

Output your response STRICTLY as a JSON object with the following keys and constraints. Do not include any text outside of the JSON structure.

- "genre": (string) The musical genre best suited for this scene (e.g., "Ambient", "Orchestral", "Synthwave", "Post-Rock").
- "mood": (string) One or two words describing the emotional feel.
- "visual_genre": (string) The literal visual genre or aesthetic of the image itself (e.g., "Sci-Fi", "Fantasy", "Cyberpunk", "Period Drama", "Modern Realism").
- "setting": (string) One or two words describing the environment.
- "energy": (float, 0.0 to 1.0) 0 is lethargic/still, 1 is fast/frantic visual movement.
- "valence": (float, 0.0 to 1.0) 0 is negative/fearful/dark, 1 is positive/joyful/bright.
- "tension": (float, 0.0 to 1.0) 0 is peaceful/resolved, 1 is high suspense/anxiety.
- "intensity": (float, 0.0 to 1.0) 0 is soft/light visual weight, 1 is heavy/massive force.
- "action_level": (float, 0.0 to 1.0) 0 is no action, 1 is intense combat or rapid motion.
- "dynamic_range": (float, 0.0 to 1.0) 0 means the image focuses on a broad background (requiring consistent music), 1 means the focus is heavily on a specific subject or character (requiring highly varied music).
- "stinger": (boolean) Set to true ONLY if the image depicts a sudden visual impact, jump scare, or shock requiring a sudden musical hit.
- "reasoning": (string) A brief explanation of why you selected these specific values based on the visual cues in the image."""


def analyze_image(image_path: str) -> Dict:
    """
    Send an image to the vision model and return music parameter suggestions as a dict.

    Args:
        image_path: Path to the image file (JPEG, PNG, etc.)

    Returns:
        Dict with keys: genre, mood, visual_genre, setting, energy, valence,
        tension, intensity, action_level, dynamic_range, stinger, reasoning.

    Raises:
        FileNotFoundError: If the image path does not exist.
        ValueError: If the model returns output that cannot be parsed as JSON.
    """
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    with open(path, "rb") as f:
        image_b64 = base64.b64encode(f.read()).decode("utf-8")

    response = ollama.chat(
        model=VISION_MODEL,
        messages=[
            {
                "role": "user",
                "content": _PROMPT,
                "images": [image_b64],
            }
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
