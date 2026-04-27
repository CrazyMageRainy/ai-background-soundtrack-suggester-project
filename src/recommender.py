import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    valence: float
    intensity: float
    stinger: bool
    action_level: float
    setting: str
    tension: float
    dynamic_range: float

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def _song_to_dict(self, s: Song) -> Dict:
        return {
            "id": s.id, "title": s.title, "artist": s.artist,
            "genre": s.genre, "mood": s.mood, "energy": s.energy,
            "valence": s.valence, "intensity": s.intensity,
            "stinger": s.stinger, "action_level": s.action_level,
            "setting": s.setting, "tension": s.tension,
            "dynamic_range": s.dynamic_range,
        }

    def recommend(self, vision_prefs: Dict, k: int = 5) -> List[Song]:
        scored = [(s, score_song(vision_prefs, self._song_to_dict(s))[0]) for s in self.songs]
        scored.sort(key=lambda x: x[1], reverse=True)
        return [s for s, _ in scored[:k]]

    def explain_recommendation(self, vision_prefs: Dict, song: Song) -> str:
        _, reasons = score_song(vision_prefs, self._song_to_dict(song))
        return "; ".join(reasons)



def load_songs(csv_path: str) -> List[Dict]:
    """Load songs from a CSV file and return a list of song dictionaries. Required by src/main.py."""
    FLOAT_FIELDS = {"energy", "valence", "intensity", "action_level", "tension", "dynamic_range"}
    songs = []
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["id"] = int(row["id"])
            # Normalize column names with spaces/capitals from the CSV
            for src, dst in [("Action Level", "action_level"), ("Stinger", "stinger"),
                              ("Setting", "setting"), ("Tension", "tension")]:
                if src in row:
                    row[dst] = row.pop(src)
            for field_name in FLOAT_FIELDS:
                if field_name in row:
                    row[field_name] = float(row[field_name])
            if "stinger" in row and isinstance(row["stinger"], str):
                row["stinger"] = row["stinger"].strip().lower() == "true"
            songs.append(row)
    return songs


def score_song(vision_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score a single song against vision profile features and return the score with reasons."""
    score = 0.0
    reasons = []

    MOOD_CLASHES = {
        "chill": "aggressive",
        "aggressive": "chill",
        "peaceful": "intense",
        "intense": "peaceful",
    }

    # --- Categorical features ---
    genre_match = vision_prefs.get("genre", "").lower() == song["genre"].lower()
    mood_match = vision_prefs.get("mood", "").lower() == song["mood"].lower()

    if genre_match:
        score += 26.0
        reasons.append("genre match (+26.0)")

    if mood_match:
        score += 12.0
        reasons.append("mood match (+12.0)")

    if genre_match and mood_match:
        score += 3.5
        reasons.append("double categorical hit (+3.5)")

    scene_mood = vision_prefs.get("mood", "").lower()
    song_mood = song["mood"].lower()
    if MOOD_CLASHES.get(scene_mood) == song_mood:
        score -= 4.0
        reasons.append("mood clash (-4.0)")

    scene_setting = vision_prefs.get("setting", "")
    if scene_setting and scene_setting.lower() == song.get("setting", "").lower():
        score += 8.0
        reasons.append("setting match (+8.0)")

    if vision_prefs.get("stinger") and song.get("stinger"):
        score += 2.0
        reasons.append("stinger match (+2.0)")

    # --- Numerical features (closeness = 1 - abs(target - song_value)) ---
    energy_closeness = 1 - abs(vision_prefs.get("energy", 0.5) - song["energy"])
    energy_points = energy_closeness * 9.0
    score += energy_points
    reasons.append(f"energy ({energy_points:+.2f})")

    valence_closeness = 1 - abs(vision_prefs.get("valence", 0.5) - song["valence"])
    valence_points = valence_closeness * 6.0
    score += valence_points
    reasons.append(f"valence ({valence_points:+.2f})")

    intensity_closeness = 1 - abs(vision_prefs.get("intensity", 0.5) - song.get("intensity", 0.5))
    intensity_points = intensity_closeness * 7.0
    score += intensity_points
    reasons.append(f"intensity ({intensity_points:+.2f})")

    tension_closeness = 1 - abs(vision_prefs.get("tension", 0.5) - song.get("tension", 0.5))
    tension_points = tension_closeness * 6.0
    score += tension_points
    reasons.append(f"tension ({tension_points:+.2f})")

    action_closeness = 1 - abs(vision_prefs.get("action_level", 0.5) - song.get("action_level", 0.5))
    action_points = action_closeness * 5.0
    score += action_points
    reasons.append(f"action_level ({action_points:+.2f})")

    dynamic_closeness = 1 - abs(vision_prefs.get("dynamic_range", 0.5) - song.get("dynamic_range", 0.5))
    dynamic_points = dynamic_closeness * 4.0
    score += dynamic_points
    reasons.append(f"dynamic_range ({dynamic_points:+.2f})")

    return (score, reasons)

def recommend_songs(vision_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Return the top-k scored songs for a scene's vision profile."""
    scored = [
        (song, score, "; ".join(reasons))
        for song in songs
        for score, reasons in [score_song(vision_prefs, song)]
    ]
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:k]
