import streamlit as st
import pymysql
from datetime import datetime

def change_date(str):
    datetimedate = datetime.strptime(str, '%d-%m-%y')
    return datetimedate.strftime('%b %d, %Y')

def load_account_page():
    st.title("Your Account Information")
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
    # assume demo user ID is 1
    user_id = 1

    def fetch_user_data():
        query = "SELECT * FROM netflix_userbase WHERE `user_id` = %s"
        with conn.cursor() as cursor:
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            if result:
                columns = [col[0] for col in cursor.description]
                return dict(zip(columns, result))
            return None

    user_data = fetch_user_data()
    # change date format
    user_data['join_date'] = change_date(user_data['join_date'])
    user_data['last_payment_date'] = change_date(user_data['last_payment_date'])
    if user_data:
        with st.container():
            st.markdown(
                f"""
                <div style="background-color: #141414; padding: 20px; border-radius: 10px;">
                    <h2 style="color: white;">{user_data['subscription_type']} Plan</h2>
                    <p style="color: #E50914; font-size: 24px;"><strong>${user_data['monthly_revenue']}/month</strong></p>
                </div>
                """,
                unsafe_allow_html=True
            )

        with st.container():
            st.markdown(
                f"""
                <div style="background-color: #222; padding: 20px; border-radius: 10px; margin-top: 20px;">
                    <h3 style="color: white;">Account Details</h3>
                    <ul style="color: white; font-size: 16px; list-style-type: none; padding: 0;">
                        <li><strong>Join Date:</strong> {user_data['join_date']}</li>
                        <li><strong>Last Payment Date:</strong> {user_data['last_payment_date']}</li>
                        <li><strong>Country:</strong> {user_data['country']}</li>
                        <li><strong>Age:</strong> {user_data['age']} years</li>
                        <li><strong>Gender:</strong> {user_data['gender']}</li>
                        <li><strong>Device:</strong> {user_data['device']}</li>
                        <li><strong>Plan Duration:</strong> {user_data['plan_duration']}</li>
                    </ul>
                </div>
                """,
                unsafe_allow_html=True
            )
        # divider
        st.markdown("---")
        st.subheader("Update Your Information")
        new_subscription = st.selectbox(
            "Update Subscription Type",
            options=["Basic", "Standard", "Premium"],
            index=["Basic", "Standard", "Premium"].index(user_data["subscription_type"])
        )

        if st.button("Update"):
            # url to netflix subscription page
            st.markdown(
                f"""
                <div style="text-align: right; margin-top: 20px; color: white;">
                    <a href="https://www.netflix.com/youraccount" target="_blank" style="color: white;font-size: 16px; text-decoration: none; color: blue;">
                        🛠️ Update on Netflix
                    </a>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.error("User not found.")