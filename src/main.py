"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from tabulate import tabulate

from src.recommender import SCORING_MODES, load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    profiles = [
        ("High-Energy Pop", {
            "favorite_genre": "pop",
            "favorite_mood": "happy",
            "target_energy": 0.9,
            "likes_acoustic": False,
        }, "default"),
        ("Chill Lofi", {
            "favorite_genre": "lofi",
            "favorite_mood": "chill",
            "target_energy": 0.35,
            "likes_acoustic": True,
        }, "mood-first"),
        ("Deep Intense Rock", {
            "favorite_genre": "rock",
            "favorite_mood": "intense",
            "target_energy": 0.9,
            "likes_acoustic": False,
        }, "energy-focused"),
        ("Sad Rave", {
            "favorite_genre": "metal",
            "favorite_mood": "melancholic",
            "target_energy": 0.95,
            "likes_acoustic": True,
        }, "energy-focused"),
        ("Genre/Mood Ghost", {
            "favorite_genre": "reggae",
            "favorite_mood": "euphoric",
            "target_energy": 0.6,
            "likes_acoustic": False,
        }, "mood-first"),
        ("Zero Energy Absolutist", {
            "favorite_genre": "ambient",
            "favorite_mood": "chill",
            "target_energy": 0.0,
            "likes_acoustic": True,
        }, "default"),
    ]

    for name, user_prefs, mode_name in profiles:
        print(f"\n=== {name} ({mode_name}) ===\n")
        weights = SCORING_MODES[mode_name]
        recommendations = recommend_songs(user_prefs, songs, k=5, weights=weights)

        print("Top recommendations:\n")
        for rec in recommendations:
            # You decide the structure of each returned item.
            # A common pattern is: (song, score, explanation)
            song, score, reasons = rec
            print(f"{song['title']} - Score: {score:.2f}")
            print(f"Because: {', '.join(reasons)}")
            print()

        table_rows = [
            [song["title"], score, ", ".join(reasons)]
            for song, score, reasons in recommendations
        ]
        print(
            tabulate(
                table_rows,
                headers=["Title", "Score", "Reasons"],
                tablefmt="grid",
                maxcolwidths=[20, None, 50],
                floatfmt=".2f",
            )
        )
        print()


if __name__ == "__main__":
    main()
