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

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool = False
    favorite_artists: set = field(default_factory=set)
    target_valence: float = 0.5
    target_intensity: float = 0.5
    target_tension: float = 0.5
    target_dynamic_range: float = 0.5
    target_action_level: float = 0.5
    wants_stinger: bool = False
    favorite_setting: str = ""

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

    def _profile_to_dict(self, user: UserProfile) -> Dict:
        return {
            "favorite_genre": user.favorite_genre,
            "favorite_mood": user.favorite_mood,
            "target_energy": user.target_energy,
            "target_valence": user.target_valence,
            "target_intensity": user.target_intensity,
            "target_tension": user.target_tension,
            "target_dynamic_range": user.target_dynamic_range,
            "target_action_level": user.target_action_level,
            "wants_stinger": user.wants_stinger,
            "favorite_setting": user.favorite_setting,
            "favorite_artists": user.favorite_artists,
        }

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        user_dict = self._profile_to_dict(user)
        scored = [(s, score_song(user_dict, self._song_to_dict(s))[0]) for s in self.songs]
        scored.sort(key=lambda x: x[1], reverse=True)
        return [s for s, _ in scored[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        _, reasons = score_song(self._profile_to_dict(user), self._song_to_dict(song))
        return "; ".join(reasons)


def vision_prefs_to_user_prefs(vision: Dict) -> Dict:
    """Convert vision_ai.analyze_image() output to a user_prefs dict for score_song(). Required by src/main.py."""
    return {
        "favorite_genre": vision.get("genre", ""),
        "favorite_mood": vision.get("mood", ""),
        "target_energy": float(vision.get("energy", 0.5)),
        "target_valence": float(vision.get("valence", 0.5)),
        "target_intensity": float(vision.get("intensity", 0.5)),
        "target_tension": float(vision.get("tension", 0.5)),
        "target_action_level": float(vision.get("action_level", 0.5)),
        "target_dynamic_range": float(vision.get("dynamic_range", 0.5)),
        "wants_stinger": bool(vision.get("stinger", False)),
        "favorite_setting": vision.get("setting", ""),
        "favorite_artists": set(),
    }


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


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score a single song against user preferences and return the score with reasons. Required by recommend_songs() and src/main.py."""
    score = 0.0
    reasons = []

    MOOD_CLASHES = {
        "chill": "aggressive",
        "aggressive": "chill",
        "peaceful": "intense",
        "intense": "peaceful",
    }

    # --- Categorical features ---
    genre_match = user_prefs["favorite_genre"].lower() == song["genre"].lower()
    mood_match = user_prefs["favorite_mood"].lower() == song["mood"].lower()

    if genre_match:
        score += 26.0
        reasons.append("genre match (+26.0)")

    if mood_match:
        score += 12.0
        reasons.append("mood match (+12.0)")

    if genre_match and mood_match:
        score += 3.5
        reasons.append("double categorical hit (+3.5)")

    user_mood = user_prefs["favorite_mood"].lower()
    song_mood = song["mood"].lower()
    if MOOD_CLASHES.get(user_mood) == song_mood:
        score -= 4.0
        reasons.append("mood clash (-4.0)")

    fav_setting = user_prefs.get("favorite_setting", "")
    if fav_setting and fav_setting.lower() == song.get("setting", "").lower():
        score += 8.0
        reasons.append("setting match (+8.0)")

    if song["artist"] in user_prefs.get("favorite_artists", set()):
        score += 2.0
        reasons.append("favorite artist (+2.0)")

    if user_prefs.get("wants_stinger") and song.get("stinger"):
        score += 2.0
        reasons.append("stinger match (+2.0)")

    # --- Numerical features (closeness = 1 - abs(target - song_value)) ---
    energy_closeness = 1 - abs(user_prefs["target_energy"] - song["energy"])
    energy_points = energy_closeness * 9.0
    score += energy_points
    reasons.append(f"energy ({energy_points:+.2f})")

    valence_closeness = 1 - abs(user_prefs.get("target_valence", 0.5) - song["valence"])
    valence_points = valence_closeness * 6.0
    score += valence_points
    reasons.append(f"valence ({valence_points:+.2f})")

    intensity_closeness = 1 - abs(user_prefs.get("target_intensity", 0.5) - song.get("intensity", 0.5))
    intensity_points = intensity_closeness * 7.0
    score += intensity_points
    reasons.append(f"intensity ({intensity_points:+.2f})")

    tension_closeness = 1 - abs(user_prefs.get("target_tension", 0.5) - song.get("tension", 0.5))
    tension_points = tension_closeness * 6.0
    score += tension_points
    reasons.append(f"tension ({tension_points:+.2f})")

    action_closeness = 1 - abs(user_prefs.get("target_action_level", 0.5) - song.get("action_level", 0.5))
    action_points = action_closeness * 5.0
    score += action_points
    reasons.append(f"action_level ({action_points:+.2f})")

    dynamic_closeness = 1 - abs(user_prefs.get("target_dynamic_range", 0.5) - song.get("dynamic_range", 0.5))
    dynamic_points = dynamic_closeness * 4.0
    score += dynamic_points
    reasons.append(f"dynamic_range ({dynamic_points:+.2f})")

    return (score, reasons)

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Return the top-k scored songs for a user's preferences. Required by src/main.py."""
    scored = [
        (song, score, "; ".join(reasons))
        for song in songs
        for score, reasons in [score_song(user_prefs, song)]
    ]
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:k]
