import csv
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class Song:
    """Represents a song and its attributes."""
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
    """Represents a user's taste preferences."""
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


class Recommender:
    """OOP implementation of the recommendation logic."""

    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top k songs ranked by score for the given user profile."""
        scored = [(song, self._score(user, song)) for song in self.songs]
        scored.sort(key=lambda x: x[1], reverse=True)
        return [song for song, _ in scored[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a plain-language explanation of why this song was recommended."""
        reasons = []
        if song.genre == user.favorite_genre:
            reasons.append(f"genre match: {song.genre} (+2.0)")
        if song.mood == user.favorite_mood:
            reasons.append(f"mood match: {song.mood} (+1.5)")
        energy_gap = abs(song.energy - user.target_energy)
        energy_pts = round(1.0 - energy_gap, 2)
        reasons.append(f"energy proximity: gap={energy_gap:.2f} (+{energy_pts})")
        if user.likes_acoustic and song.acousticness > 0.5:
            reasons.append(f"acoustic match (+1.0)")
        return ", ".join(reasons) if reasons else "general catalog match"

    def _score(self, user: UserProfile, song: Song) -> float:
        score = 0.0
        if song.genre == user.favorite_genre:
            score += 2.0
        if song.mood == user.favorite_mood:
            score += 1.5
        score += 1.0 - abs(song.energy - user.target_energy)
        if user.likes_acoustic and song.acousticness > 0.5:
            score += 1.0
        return score


def load_songs(csv_path: str) -> List[Song]:
    """Load songs from a CSV file and return a list of Song objects."""
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append(Song(
                id=int(row["id"]),
                title=row["title"],
                artist=row["artist"],
                genre=row["genre"],
                mood=row["mood"],
                energy=float(row["energy"]),
                tempo_bpm=float(row["tempo_bpm"]),
                valence=float(row["valence"]),
                danceability=float(row["danceability"]),
                acousticness=float(row["acousticness"]),
            ))
    return songs


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, str]:
    """Score a single song against user preferences; returns (score, explanation)."""
    score = 0.0
    reasons = []

    if song["genre"] == user_prefs.get("genre"):
        score += 2.0
        reasons.append(f"genre match: {song['genre']} (+2.0)")

    if song["mood"] == user_prefs.get("mood"):
        score += 1.5
        reasons.append(f"mood match: {song['mood']} (+1.5)")

    target_energy = user_prefs.get("energy", 0.5)
    energy_gap = abs(song["energy"] - target_energy)
    energy_pts = round(1.0 - energy_gap, 2)
    score += energy_pts
    reasons.append(f"energy proximity: gap={energy_gap:.2f} (+{energy_pts})")

    if user_prefs.get("likes_acoustic") and song["acousticness"] > 0.5:
        score += 1.0
        reasons.append(f"acoustic match (+1.0)")

    explanation = ", ".join(reasons) if reasons else "general catalog match"
    return round(score, 2), explanation


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Score all songs for the user, sort by score descending, return top k results."""
    scored = [(*score_song(user_prefs, song), song) for song in songs]
    # reorder to (song, score, explanation)
    results = [(song, score, explanation) for score, explanation, song in scored]
    results.sort(key=lambda x: x[1], reverse=True)
    return results[:k]
