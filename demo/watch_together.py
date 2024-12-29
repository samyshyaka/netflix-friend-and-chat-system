import streamlit as st
import pymysql
from datetime import datetime
import uuid
from pymongo import MongoClient


def display_movies_grid(movies):
    st.title("Select a Movie to Watch Together")
    st.write("### Featured Titles")
    
    movies_per_row = 4
    dummy_image_path = "moviecover.jpg"
    for i in range(0, len(movies), movies_per_row):
        cols = st.columns(movies_per_row)
        for col, movie in zip(cols, movies[i:i + movies_per_row]):
            with col:
                st.image(dummy_image_path, use_container_width=True)
                if st.button(f"{movie['title']} ({movie['release_year']})"):
                    st.session_state['selected_movie'] = movie['_id']


# show the watch together page when the user clicks on a movie
def watch_together_page():
    movie_id = st.session_state.get('selected_movie', None)
    if movie_id:
        connection_string = st.secrets["mongodb"]["connection_string"]
        db_name = st.secrets["mongodb"]["database_name"]
        client = MongoClient(connection_string)
        db = client[db_name]
        movies_collection = db['Movies']
        movie = movies_collection.find_one({"_id": movie_id})
        if movie:
            movie_selected = f"{movie['title']} ({movie['release_year']})"
        st.title("Watch Together with Friends")
        # rds
        db_host = st.secrets["rds"]["db_host"]
        db_user = st.secrets["rds"]["db_user"]
        db_password = st.secrets["rds"]["db_password"]
        db_name = st.secrets["rds"]["db_name"]

        conn = pymysql.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name
        )

        # assume user_id is 1 for demo
        room_id = movie_id
        user_id = 1

        friends_collection = db['Friends']

        def fetch_friends():
            user_friends = friends_collection.find_one({"UserID": user_id})
            return user_friends.get("Friends", []) if user_friends else []

        friends_list = fetch_friends()

        st.session_state.chat_history = []

        def fetch_chat_messages():
            if not friends_list:
                return []
            placeholders = ", ".join(["%s"] * len(friends_list))
            query = f"""
            SELECT all_authors, messages, time 
            FROM chats 
            WHERE show_id = %s AND user_id IN ({placeholders})
            ORDER BY time ASC
            """
            try:
                with conn.cursor() as cursor:
                    cursor.execute(query, [room_id] + friends_list)
                    results = cursor.fetchall()
                    # Store messages in session_state
                    st.session_state.chat_history = [
                        {"author": row[0], "message": row[1], "timestamp": row[2]} for row in results
                    ]
            except Exception as e:
                st.error(f"Failed to fetch chat messages: {e}")
            
        if not st.session_state.chat_history:
            fetch_chat_messages()

        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader(movie_selected)
            st.video("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

        with col2:
            st.subheader("Live Chat")
            messages = st.container(height=400)
            with messages:
                for chat in st.session_state.chat_history:
                    st.write(f"[{chat['timestamp']}] **{chat['author']}**: {chat['message']}")
            if prompt := st.chat_input("Say something"):
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.session_state.chat_history.append({
                    "author": "You",
                    "message": prompt,
                    "timestamp": timestamp
                })
                with messages:
                    for chat in st.session_state.chat_history:
                        # display only the latest message
                        if chat == st.session_state.chat_history[-1]:
                            st.write(f"[{chat['timestamp']}] **{chat['author']}**: {chat['message']}")
                # backend operation to store the message in RDS
                unique_id = str(uuid.uuid4())[:8]
                insert_query = """
                INSERT INTO chats (unique_id, messages, all_authors, timestamps, show_id, time, user_id) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                try:
                    with conn.cursor() as cursor:
                        cursor.execute(insert_query, (
                            unique_id, prompt, "You", "-1:00", room_id, timestamp, user_id
                        ))
                        conn.commit()
                except Exception as e:
                    st.error(f"An error occurred while sending the message: {e}")
        if st.button("Back to Movie Selection"):
            st.session_state["selected_movie"] = None  # Reset selected movie


def load_watch_together():
    connection_string = st.secrets["mongodb"]["connection_string"]
    db_name = st.secrets["mongodb"]["database_name"]
    client = MongoClient(connection_string)
    db = client[db_name]
    movies_collection = db['Movies']

    movies = list(movies_collection.find({}, {"_id": 1, "title": 1, "release_year": 1, "genre": 1}).limit(20))  # Limit to 20 movies for demo
    
    if "selected_movie" not in st.session_state:
        st.session_state["selected_movie"] = None

    if st.session_state["selected_movie"]:
        watch_together_page()
    else:
        display_movies_grid(movies)
