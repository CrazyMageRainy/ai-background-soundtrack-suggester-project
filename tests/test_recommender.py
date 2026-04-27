from src.recommender import Song, Recommender

def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            valence=0.9,
            intensity=0.7,
            stinger=False,
            action_level=0.5,
            setting="Urban",
            tension=0.3,
            dynamic_range=0.6,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Test Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            valence=0.6,
            intensity=0.3,
            stinger=False,
            action_level=0.2,
            setting="Indoor",
            tension=0.1,
            dynamic_range=0.4,
        ),
    ]
    return Recommender(songs)

VISION_PREFS = {
    "genre": "pop",
    "mood": "happy",
    "energy": 0.8,
    "valence": 0.9,
    "intensity": 0.7,
    "tension": 0.3,
    "action_level": 0.5,
    "dynamic_range": 0.6,
    "stinger": False,
    "setting": "Urban",
}

def test_recommend_returns_songs_sorted_by_score():
    rec = make_small_recommender()
    results = rec.recommend(VISION_PREFS, k=2)

    assert len(results) == 2
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(VISION_PREFS, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""
