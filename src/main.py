"""
Command line runner for the Music Recommender Simulation.

Run from the project root:
    python -m src.main
"""

from src.recommender import load_songs, recommend_songs


def print_recommendations(label: str, user_prefs: dict, songs: list, k: int = 5) -> None:
    """Print a formatted recommendation block for one user profile."""
    print(f"\n{'='*54}")
    print(f"  Profile : {label}")
    print(f"  Prefs   : {user_prefs}")
    print(f"{'='*54}")
    for rank, (song, score, reasons) in enumerate(recommend_songs(user_prefs, songs, k=k), 1):
        print(f"  {rank}. {song['title']}  ({song['genre']} / {song['mood']})")
        print(f"     Score: {score:.3f}")
        for reason in reasons:
            print(f"       • {reason}")
        print()


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded {len(songs)} songs from catalog.")

    # Profile A: upbeat pop listener
    print_recommendations(
        "Pop / Happy / High Energy",
        {"genre": "pop", "mood": "happy", "energy": 0.8},
        songs,
    )

    # Profile B: intense rock — should surface Storm Runner and Shatter Glass
    print_recommendations(
        "Rock / Intense / Very High Energy",
        {"genre": "rock", "mood": "intense", "energy": 0.92, "likes_acoustic": False},
        songs,
    )

    # Profile C: chill lofi — should surface Library Rain and Midnight Coding
    print_recommendations(
        "Lofi / Chill / Low Energy (acoustic)",
        {"genre": "lofi", "mood": "chill", "energy": 0.38, "likes_acoustic": True},
        songs,
    )


if __name__ == "__main__":
    main()
