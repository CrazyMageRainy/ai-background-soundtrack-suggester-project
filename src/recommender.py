import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

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
    # tempo_bpm: float
    valence: float
    # danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool
    favorite_artists: set
    target_valence: float
    target_dancebility: float
class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    FLOAT_FIELDS = {"energy", "tempo_bpm", "valence", "danceability", "acousticness"}
    songs = []
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["id"] = int(row["id"])
            for field in FLOAT_FIELDS:
                row[field] = float(row[field])
            songs.append(row)
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences.
    Required by recommend_songs() and src/main.py
    """
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

    # Bonus: both genre AND mood match
    if genre_match and mood_match:
        score += 3.5
        reasons.append("double categorical hit (+3.5)")

    # Penalty: mood clash
    user_mood = user_prefs["favorite_mood"].lower()
    song_mood = song["mood"].lower()
    if MOOD_CLASHES.get(user_mood) == song_mood:
        score -= 4.0
        reasons.append("mood clash (-4.0)")

    # Favorite artist bonus
    if song["artist"] in user_prefs.get("favorite_artists", set()):
        score += 2.0
        reasons.append("favorite artist (+2.0)")

    # --- Numerical features (closeness = 1 - abs(user_pref - song_value)) ---
    energy_closeness = 1 - abs(user_prefs["target_energy"] - song["energy"])
    energy_points = energy_closeness * 9.0
    score += energy_points
    reasons.append(f"energy ({energy_points:+.2f})")

    valence_closeness = 1 - abs(user_prefs["target_valence"] - song["valence"])
    valence_points = valence_closeness * 6.0
    score += valence_points
    reasons.append(f"valence ({valence_points:+.2f})")

    dance_closeness = 1 - abs(user_prefs["target_dancebility"] - song["danceability"])
    dance_points = dance_closeness * 5.0
    score += dance_points
    reasons.append(f"danceability ({dance_points:+.2f})")

    return (score, reasons)

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    """
    scored = [
        (song, score, "; ".join(reasons))
        for song in songs
        for score, reasons in [score_song(user_prefs, song)]
    ]
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:k]
