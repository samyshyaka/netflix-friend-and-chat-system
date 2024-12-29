import streamlit as st
from streamlit_option_menu import option_menu
import numpy as np
from login_config import login_in,init_login,login_out
from home import load_homepage
from friends import load_friend_page
from watch_together import load_watch_together
from accounts import load_account_page
init_login ()
login_code = login_in ()
# print(st.session_state [ 'user_info' ])


if st.session_state [ 'user_info' ]:
    if st.session_state [ 'user_info' ]== "demo":
        options = [ "Homepage", 'Friends' ,'Watch Together', 'Account' ,'Log out' ]
    with st.sidebar:
        selected = option_menu ( f'Hi, {st.session_state [ "user_info" ]}\n Welcome to Netflix!' ,options ,default_index = 0 )


    if selected == 'Homepage':
        load_homepage()
    elif selected == 'Friends':
        try:
            load_friend_page()
        except:
            pass
    elif selected == 'Watch Together':
        try:
            load_watch_together()
        except:
            pass
    elif selected == 'Account':
        try:
            load_account_page()
        except:
            pass
    
    elif selected == 'Log out':
        login_out ()
        st.rerun ()
