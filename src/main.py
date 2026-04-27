"""
Image-to-music pipeline runner.

Usage:
    python -m src.main path/to/image.jpg
    python -m src.main path/to/image.jpg --top 10
"""

import argparse
import json

from src.vision_ai import analyze_image
from src.recommender import load_songs, recommend_songs
from src.final_decider import decide


CATALOGS = [
    "data/fixed_music_list.csv",
    "data/verified_compiled_music_list.csv",
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Recommend background music for a scene image.")
    parser.add_argument("image", help="Path to the scene image file (JPEG, PNG, WEBP, …)")
    parser.add_argument("--top", type=int, default=10, help="Number of candidates to pass to the final AI (default: 10)")
    args = parser.parse_args()

    print(f"\n[1/3] Analyzing image: {args.image}")
    image_profile = analyze_image(args.image)
    print("      Vision AI output:")
    for key, value in image_profile.items():
        if key != "reasoning":
            print(f"        {key}: {value}")
    print(f"      Reasoning: {image_profile.get('reasoning', '')}")

    print(f"\n[2/3] Scoring song catalog …")
    songs = []
    for path in CATALOGS:
        loaded = load_songs(path)
        songs += loaded
        print(f"      Loaded {len(loaded)} songs from {path}")
    print(f"      Total: {len(songs)} songs")

    top_songs = recommend_songs(image_profile, songs, k=args.top)

    print(f"\n      Top {args.top} candidates:")
    for rank, (song, score, _) in enumerate(top_songs, 1):
        print(f"        #{rank:2d}  {song['title']} — {song['artist']}  (score: {score:.1f})")

    print(f"\n[3/3] Final AI selecting best match …")
    candidates = [song for song, _score, _ in top_songs]
    score_lookup = {str(song["id"]): score for song, score, _ in top_songs}
    result = decide(image_profile, candidates)

    def song_label(song_id: str) -> str:
        song = next((s for s in candidates if str(s["id"]) == song_id), None)
        if not song:
            return song_id
        score = score_lookup.get(song_id, 0.0)
        return f"{song['title']} — {song['artist']}  (score: {score:.1f})"

    print("\n" + "=" * 60)
    print("  RECOMMENDATION")
    print("=" * 60)
    print(f"  Selected:  {song_label(str(result.get('selected_song_id', '')))}")
    print(f"  Runner-up: {song_label(str(result.get('runner_up_song_id', '')))}")
    rules = result.get("applied_rules", [])
    if rules and rules != ["None"]:
        print(f"  Rules applied: {', '.join(rules)}")
    print(f"\n  {result.get('reasoning', '')}")
    print("=" * 60)


if __name__ == "__main__":
    main()
