import csv
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class Song:
    """A single song and its audio feature attributes."""
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float


@dataclass
class UserProfile:
    """A user's explicit music taste preferences used for content-based matching."""
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score one song against user preferences; return (score, reasons) where reasons explain each contribution."""
    score = 0.0
    reasons: List[str] = []

    # Genre match — highest weight (0.30); binary, no partial credit
    if song["genre"] == user_prefs.get("genre", ""):
        pts = 0.30
        score += pts
        reasons.append(f"genre match: '{song['genre']}' (+{pts:.2f})")

    # Energy proximity — second highest (0.25); rewards closeness to user target
    target_energy = user_prefs.get("energy", 0.5)
    energy_pts = round((1.0 - abs(target_energy - song["energy"])) * 0.25, 3)
    score += energy_pts
    reasons.append(
        f"energy {song['energy']:.2f} vs target {target_energy:.2f} (+{energy_pts:.2f})"
    )

    # Mood match — third highest (0.20); binary
    if song["mood"] == user_prefs.get("mood", ""):
        pts = 0.20
        score += pts
        reasons.append(f"mood match: '{song['mood']}' (+{pts:.2f})")

    # Valence — raw positivity signal (0.10); no user target, higher is happier
    valence_pts = round(song["valence"] * 0.10, 3)
    score += valence_pts

    # Acousticness proximity — (0.10); user expresses preference as a boolean
    acoustic_target = 0.8 if user_prefs.get("likes_acoustic", False) else 0.2
    acousticness_pts = round((1.0 - abs(acoustic_target - song["acousticness"])) * 0.10, 3)
    score += acousticness_pts

    # Danceability — minor activity signal (0.05); raw value
    score += round(song["danceability"] * 0.05, 3)

    return round(score, 3), reasons


class Recommender:
    """OOP wrapper around the scoring logic; operates on typed Song and UserProfile objects."""

    def __init__(self, songs: List[Song]):
        self.songs = songs

    def _score_song(self, user: UserProfile, song: Song) -> float:
        """Return the weighted 0–1 score for a Song against a UserProfile."""
        genre_score = 1.0 if song.genre == user.favorite_genre else 0.0
        mood_score = 1.0 if song.mood == user.favorite_mood else 0.0
        energy_score = 1.0 - abs(user.target_energy - song.energy)
        acoustic_target = 0.8 if user.likes_acoustic else 0.2
        acousticness_score = 1.0 - abs(acoustic_target - song.acousticness)
        return (
            0.30 * genre_score
            + 0.25 * energy_score
            + 0.20 * mood_score
            + 0.10 * song.valence
            + 0.10 * acousticness_score
            + 0.05 * song.danceability
        )

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top-k songs ranked highest to lowest by weighted score."""
        return sorted(self.songs, key=lambda s: self._score_song(user, s), reverse=True)[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a human-readable sentence explaining why song was recommended."""
        reasons = []
        if song.genre == user.favorite_genre:
            reasons.append(f"genre matches '{user.favorite_genre}'")
        if song.mood == user.favorite_mood:
            reasons.append(f"mood matches '{user.favorite_mood}'")
        if abs(user.target_energy - song.energy) <= 0.15:
            reasons.append(f"energy {song.energy:.2f} close to target {user.target_energy:.2f}")
        if not reasons:
            reasons.append("best available match on overall profile")
        return "Recommended because: " + ", ".join(reasons)


def load_songs(csv_path: str) -> List[Dict]:
    """Read songs.csv and return a list of dicts with numeric fields cast to float."""
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            row["energy"] = float(row["energy"])
            row["tempo_bpm"] = float(row["tempo_bpm"])
            row["valence"] = float(row["valence"])
            row["danceability"] = float(row["danceability"])
            row["acousticness"] = float(row["acousticness"])
            songs.append(row)
    return songs


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, List[str]]]:
    """Score every song for user_prefs and return the top-k as (song, score, reasons) tuples."""
    scored = [(song, *score_song(user_prefs, song)) for song in songs]
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:k]
