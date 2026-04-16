"""
Music Recommender AI — Streamlit UI
"""

import sys
import os
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

import streamlit as st
from recommender import load_songs, Recommender, UserProfile
from ai_explainer import validate_user_profile, explain_recommendations
from logger_setup import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "songs.csv")


@st.cache_data
def get_songs():
    return load_songs(DATA_PATH)


def main():
    st.set_page_config(page_title="Music Recommender AI", page_icon="🎵", layout="wide")
    st.title("🎵 Music Recommender AI")
    st.write("Tell us your vibe and we'll find your next favorite songs — then explain why.")

    st.sidebar.header("Your Music Profile")

    genre = st.sidebar.selectbox(
        "Favorite Genre",
        ["pop", "rock", "lofi", "jazz", "electronic", "ambient", "classical", "hiphop"],
    )
    mood = st.sidebar.selectbox(
        "Current Mood",
        ["happy", "chill", "intense", "sad", "romantic", "energetic"],
    )
    energy = st.sidebar.slider("Energy Level", min_value=0.0, max_value=1.0, value=0.6, step=0.05)
    likes_acoustic = st.sidebar.checkbox("I like acoustic songs")
    k = st.sidebar.slider("Number of recommendations", min_value=1, max_value=10, value=5)

    if st.sidebar.button("Get Recommendations", type="primary"):
        logger.info("User requested recommendations: genre=%s mood=%s energy=%.2f", genre, mood, energy)

        with st.spinner("Checking your profile..."):
            is_valid, validation_msg = validate_user_profile(genre, mood, energy)

        if not is_valid:
            st.error(f"Profile issue: {validation_msg}")
            logger.warning("Invalid profile rejected: %s", validation_msg)
            return

        st.success(f"Profile valid: {validation_msg}")

        songs = get_songs()
        user = UserProfile(
            favorite_genre=genre,
            favorite_mood=mood,
            target_energy=energy,
            likes_acoustic=likes_acoustic,
        )
        recommender = Recommender(songs)
        top_songs = recommender.recommend(user, k=k)

        rec_dicts = [
            {
                "title": s.title,
                "artist": s.artist,
                "genre": s.genre,
                "mood": s.mood,
                "energy": s.energy,
                "score": recommender._score(user, s),
            }
            for s in top_songs
        ]

        st.subheader("Your Recommendations")
        for i, rec in enumerate(rec_dicts, 1):
            with st.container():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**{i}. {rec['title']}** by {rec['artist']}")
                    st.caption(f"Genre: {rec['genre']} | Mood: {rec['mood']} | Energy: {rec['energy']:.2f}")
                with col2:
                    st.metric("Score", f"{rec['score']:.2f}")

        st.divider()

        with st.spinner("Generating AI explanation..."):
            explanation = explain_recommendations(genre, mood, energy, rec_dicts)

        st.subheader("Why These Songs?")
        st.info(explanation)

        logger.info("Recommendations delivered successfully for genre=%s mood=%s", genre, mood)


if __name__ == "__main__":
    main()
