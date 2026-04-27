"""
Integration tests for the full image-to-music pipeline.
Requires ollama to be running with:
  - qwen3-vl:8b-instruct-q4_K_M  (vision model)
  - qwen3:4b-instruct             (final decider model)

Run with: pytest tests/test_pipeline.py -v
"""

import pytest
from src.vision_ai import analyze_image
from src.recommender import load_songs, recommend_songs
from src.final_decider import decide

CATALOGS = [
    "data/fixed_music_list.csv",
    "data/verified_compiled_music_list.csv",
]

def load_all_songs():
    songs = []
    for path in CATALOGS:
        songs += load_songs(path)
    return songs


# ---------------------------------------------------------------------------
# Image: Final Fantasy XIV – Dawntrail (tranquil fantasy village)
# Vision output:
#   genre: Ambient | mood: serene, mystical | setting: mountain village
#   energy: 0.3 | valence: 0.8 | tension: 0.2 | intensity: 0.4
#   action_level: 0.0 | dynamic_range: 0.3 | stinger: false
# Top candidates (score):
#   #1  Rhubarb (#3) — Aphex Twin  (score ~47)
#   #2  Sweden — C418              (score ~46)
#   #3  Secunda — Jeremy Soule     (score ~45)
# Final decision: Rhubarb (#3) — Aphex Twin
# ---------------------------------------------------------------------------
def test_ffxiv_dawntrail_vision_output():
    profile = analyze_image("assets/test pics/Final-Fantasy-XIV-Dawntrail-Screenshot-014.jpg")
    assert isinstance(profile, dict)
    assert profile["energy"] <= 0.5,      "low energy expected for calm scene"
    assert profile["valence"] >= 0.5,     "positive valence expected for bright scene"
    assert profile["action_level"] <= 0.2, "no action expected"
    assert profile["stinger"] == False

def test_ffxiv_dawntrail_recommends_ambient():
    profile = analyze_image("assets/test pics/Final-Fantasy-XIV-Dawntrail-Screenshot-014.jpg")
    songs = load_all_songs()
    top = recommend_songs(profile, songs, k=10)
    assert len(top) == 10
    genres = [s["genre"].lower() for s, _, _ in top]
    assert any("ambient" in g for g in genres), "ambient songs should rank highly for a calm scene"

def test_ffxiv_dawntrail_full_pipeline():
    profile = analyze_image("assets/test pics/Final-Fantasy-XIV-Dawntrail-Screenshot-014.jpg")
    songs = load_all_songs()
    top = recommend_songs(profile, songs, k=10)
    candidates = [s for s, _, _ in top]
    result = decide(profile, candidates)
    assert "selected_song_id" in result
    assert "runner_up_song_id" in result
    assert "reasoning" in result
    assert result["selected_song_id"] != result["runner_up_song_id"]


# ---------------------------------------------------------------------------
# Image: God of War Ragnarok art (intense fantasy battle)
# Vision output:
#   genre: Orchestral | mood: Intense, Epic | setting: Battlefield
#   energy: 0.9 | valence: 0.7 | tension: 0.8 | intensity: 0.95
#   action_level: 0.95 | dynamic_range: 0.8 | stinger: false
# Top candidates (score):
#   #1  One Final Effort — Martin O'Donnell  (score ~62)
#   #2  BFG Division — Mick Gordon           (score ~60)
#   #3  God of War — Bear McCreary           (score ~59)
# Final decision: One Final Effort — Martin O'Donnell
# ---------------------------------------------------------------------------
def test_god_of_war_vision_output():
    profile = analyze_image("assets/test pics/god-of-war-ragnarok-art.webp")
    assert isinstance(profile, dict)
    assert profile["energy"] >= 0.7,      "high energy expected for battle scene"
    assert profile["intensity"] >= 0.7,   "high intensity expected"
    assert profile["action_level"] >= 0.7, "high action expected"
    assert profile["tension"] >= 0.6

def test_god_of_war_recommends_high_intensity():
    profile = analyze_image("assets/test pics/god-of-war-ragnarok-art.webp")
    songs = load_all_songs()
    top = recommend_songs(profile, songs, k=10)
    scores = [score for _, score, _ in top]
    assert scores[0] >= scores[-1], "results should be sorted descending by score"
    top_avg = sum(float(s.get("intensity", 0)) for s, _, _ in top[:3]) / 3
    assert top_avg >= 0.5, "top songs should lean toward higher intensity"

def test_god_of_war_full_pipeline():
    profile = analyze_image("assets/test pics/god-of-war-ragnarok-art.webp")
    songs = load_all_songs()
    top = recommend_songs(profile, songs, k=10)
    candidates = [s for s, _, _ in top]
    result = decide(profile, candidates)
    assert "selected_song_id" in result
    assert "runner_up_song_id" in result
    assert "reasoning" in result
    assert result["selected_song_id"] != result["runner_up_song_id"]


# ---------------------------------------------------------------------------
# Image: Minecraft rain shader screenshot (mysterious, calm forest)
# Vision output:
#   genre: Ambient | mood: Mysterious, Calm | setting: Rainy Forest
#   energy: 0.2 | valence: 0.6 | tension: 0.3 | intensity: 0.4
#   action_level: 0.1 | dynamic_range: 0.3 | stinger: false
# Top candidates (score):
#   #1  Sweden — C418               (score ~49)
#   #2  Subwoofer Lullaby — C418    (score ~48)
#   #3  Weightless — Marconi Union  (score ~47)
# Final decision: Sweden — C418
# ---------------------------------------------------------------------------
def test_minecraft_rain_vision_output():
    profile = analyze_image("assets/test pics/newb-x-trailer-shader-rain-screenshot.webp")
    assert isinstance(profile, dict)
    assert profile["energy"] <= 0.4,      "low energy expected for quiet rain scene"
    assert profile["action_level"] <= 0.3, "minimal action expected"
    assert profile["stinger"] == False

def test_minecraft_rain_recommends_calm():
    profile = analyze_image("assets/test pics/newb-x-trailer-shader-rain-screenshot.webp")
    songs = load_all_songs()
    top = recommend_songs(profile, songs, k=10)
    assert len(top) == 10
    top_energies = [float(s["energy"]) for s, _, _ in top[:5]]
    assert all(e <= 0.7 for e in top_energies), "top songs should not be high energy"

def test_minecraft_rain_full_pipeline():
    profile = analyze_image("assets/test pics/newb-x-trailer-shader-rain-screenshot.webp")
    songs = load_all_songs()
    top = recommend_songs(profile, songs, k=10)
    candidates = [s for s, _, _ in top]
    result = decide(profile, candidates)
    assert "selected_song_id" in result
    assert "runner_up_song_id" in result
    assert "reasoning" in result
    assert result["selected_song_id"] != result["runner_up_song_id"]
