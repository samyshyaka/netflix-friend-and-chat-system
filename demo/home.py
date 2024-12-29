# home.py
import streamlit as st
from pymongo import MongoClient
from urllib.parse import quote


def display_movies_grid(movies):
    st.title("Welcome to Netflix!")
    st.write("### Featured Titles")
    
    movies_per_row = 4
    dummy_image_path = "moviecover.jpg"
    for i in range(0, len(movies), movies_per_row):
        cols = st.columns(movies_per_row)
        for col, movie in zip(cols, movies[i:i + movies_per_row]):
            # Display movie poster and title
            with col:
                st.image(dummy_image_path, use_container_width=True)
                if st.button(f"{movie['title']} ({movie['release_year']})"):
                    st.session_state['selected_movie'] = movie['_id']  # Store selected movie ID


def display_movie_details():
    movie_id = st.session_state.get('selected_movie', None)
    if movie_id:
        connection_string = st.secrets["mongodb"]["connection_string"]
        db_name = st.secrets["mongodb"]["database_name"]
        client = MongoClient(connection_string)
        db = client[db_name]
        movies_collection = db['Movies']
        movie = movies_collection.find_one({"_id": movie_id})
        if movie:
            st.title(movie['title'])
            st.image("moviecover.jpg", use_container_width=True)
            st.write(f"**Release Year:** {movie['release_year']}")
            st.write(f"**Genre:** {', '.join(movie['genre'])}")
            st.write(f"**Duration:** {movie['duration']}")
            st.write(f"**Cast:** {', '.join(movie['cast'])}")
            st.write(f"**Description:** {movie['description']}")
            st.markdown(
                f"""
                <div style="text-align: right; margin-top: 20px;">
                    <a href="https://www.netflix.com/watch/{quote(movie['title'])}" target="_blank" style="color: white;font-size: 16px; text-decoration: none; color: blue;">
                        🍿 Watch on Netflix
                    </a>
                </div>
                """,
                unsafe_allow_html=True,
            )
    if st.button("Back to Homepage"):
            st.session_state["selected_movie"] = None  # Reset selected movie


def load_homepage():
    connection_string = st.secrets["mongodb"]["connection_string"]
    db_name = st.secrets["mongodb"]["database_name"]
    client = MongoClient(connection_string)
    db = client[db_name]
    movies_collection = db['Movies']

    movies = list(movies_collection.find({}, {"_id": 1, "title": 1, "release_year": 1, "genre": 1}).limit(20))  # Limit to 20 movies for demo
    
    if "selected_movie" not in st.session_state:
        st.session_state["selected_movie"] = None

    if st.session_state["selected_movie"]:
        display_movie_details()
    else:
        display_movies_grid(movies)
