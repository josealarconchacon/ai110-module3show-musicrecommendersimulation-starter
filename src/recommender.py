import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict

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
    tempo_bpm: float
    valence: float
    danceability: float
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

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        user_dict = asdict(user)
        song_dicts = [asdict(song) for song in self.songs]
        results = recommend_songs(user_dict, song_dicts, k)

        songs_by_id = {song.id: song for song in self.songs}
        return [songs_by_id[scored_song["id"]] for scored_song, _score, _reasons in results]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        user_dict = asdict(user)
        song_dict = asdict(song)
        _score, reasons = score_song(user_dict, song_dict)
        return ", ".join(reasons)

def load_songs(csv_path: str) -> List[Dict]:
    """Reads a CSV file of songs and returns each row as a dict with numeric fields converted."""
    songs = []
    with open(csv_path, newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            row["id"] = int(row["id"])
            for field in ("energy", "tempo_bpm", "valence", "danceability", "acousticness"):
                row[field] = float(row[field])
            songs.append(row)
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Computes a match score and list of reasons for a song against a user's preferences."""
    total_score = 0.0
    reasons = []

    if song["genre"] == user_prefs["favorite_genre"]:
        total_score += 2.0
        reasons.append("genre match (+2.0)")

    if song["mood"] == user_prefs["favorite_mood"]:
        total_score += 1.0
        reasons.append("mood match (+1.0)")

    energy_points = (1 - abs(user_prefs["target_energy"] - song["energy"])) * 2.0
    if energy_points > 0:
        total_score += energy_points
        reasons.append(f"energy closeness (+{energy_points:.2f})")

    if user_prefs["likes_acoustic"] == (song["acousticness"] > 0.5):
        total_score += 0.5
        reasons.append("acousticness match (+0.5)")

    return (total_score, reasons)

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Scores every song against user preferences and returns the top k, sorted highest first."""
    scored = [(song, *score_song(user_prefs, song)) for song in songs]
    return sorted(scored, key=lambda result: result[1], reverse=True)[:k]
