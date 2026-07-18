"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from src.recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    profiles = [
        ("High-Energy Pop", {
            "favorite_genre": "pop",
            "favorite_mood": "happy",
            "target_energy": 0.9,
            "likes_acoustic": False,
        }),
        ("Chill Lofi", {
            "favorite_genre": "lofi",
            "favorite_mood": "chill",
            "target_energy": 0.35,
            "likes_acoustic": True,
        }),
        ("Deep Intense Rock", {
            "favorite_genre": "rock",
            "favorite_mood": "intense",
            "target_energy": 0.9,
            "likes_acoustic": False,
        }),
        ("Sad Rave", {
            "favorite_genre": "metal",
            "favorite_mood": "melancholic",
            "target_energy": 0.95,
            "likes_acoustic": True,
        }),
        ("Genre/Mood Ghost", {
            "favorite_genre": "reggae",
            "favorite_mood": "euphoric",
            "target_energy": 0.6,
            "likes_acoustic": False,
        }),
        ("Zero Energy Absolutist", {
            "favorite_genre": "ambient",
            "favorite_mood": "chill",
            "target_energy": 0.0,
            "likes_acoustic": True,
        }),
    ]

    for name, user_prefs in profiles:
        print(f"\n=== {name} ===\n")
        recommendations = recommend_songs(user_prefs, songs, k=5)

        print("Top recommendations:\n")
        for rec in recommendations:
            # You decide the structure of each returned item.
            # A common pattern is: (song, score, explanation)
            song, score, reasons = rec
            print(f"{song['title']} - Score: {score:.2f}")
            print(f"Because: {', '.join(reasons)}")
            print()


if __name__ == "__main__":
    main()
