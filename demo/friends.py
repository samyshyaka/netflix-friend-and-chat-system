import streamlit as st
from pymongo import MongoClient

def load_friend_page():
    st.title("Your Friends on Netflix")
    
    connection_string = st.secrets["mongodb"]["connection_string"]
    db_name = st.secrets["mongodb"]["database_name"]
    client = MongoClient(connection_string)
    db = client[db_name]
    friends_collection = db['Friends']

    # assume demo user ID is 1
    user_id = 1  # Example user ID for testing
    
    # Fetch the user's friends list
    user_friends = friends_collection.find_one({"UserID": user_id})
    friends_list = user_friends.get("Friends", []) if user_friends else []

    # display friends in a scrollable container
    st.subheader("Your Friends")

    if friends_list:
            with st.container(height=200):
                for friend_id in friends_list:
                    st.write(f"Friend ID: {friend_id}") 
    else:
        st.write("You have no friends added yet.")

    # add friends
    st.subheader("Add a Friend")
    new_friend_id = st.number_input("Enter Friend ID", min_value=0, step=1)
    if st.button("Add Friend"):
        if not user_friends:
            friends_collection.insert_one({"UserID": user_id, "Friends": [new_friend_id]})
        else:
            # add to existing friends list
            friends_collection.update_one({"UserID": user_id}, {"$addToSet": {"Friends": new_friend_id}})
        st.success(f"Friend {new_friend_id} added!")
        st.rerun()  # refresh

    st.subheader("Remove a Friend")
    if friends_list:
        friend_to_remove = st.selectbox("Select Friend to Remove", options=friends_list)
        if st.button("Remove Friend"):
            friends_collection.update_one({"UserID": user_id}, {"$pull": {"Friends": friend_to_remove}})
            st.success(f"Friend {friend_to_remove} removed!")
            st.rerun() # refresh
