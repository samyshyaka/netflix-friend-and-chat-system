import streamlit as st
"""
Login to Netflix
"""
def login_in():
    """
    login page
    :return: login status
    """
    empty = st.empty ()
    with empty:
        if st.session_state [ 'user_info' ] is None:
            with st.form ( "login_form" ):
                st.title ( 'Login' )
                username = st.text_input ( "Account" )
                password = st.text_input ( "Password" ,type = "password" )
                submitted = st.form_submit_button ( "login" )
                try:
                    real_password = '123456'
                    # user_info['user_name'] = user_name
                    if submitted is True and password == real_password:
                        st.session_state [ 'user_info' ] = 'demo'
                        empty.empty ()
                        return True
                    elif submitted is True and password != real_password:
                        st.error ( 'Account or password error' )
                        return False

                except:
                    pass

def init_login():
    """
    initialize session_state
    :return: None
    """
    if 'user_info' not in st.session_state:
        st.session_state [ 'user_info' ] = None


def login_out():
    """
    log out
    :return: True indicates successful, False indicates failure
    """
    try:
        # reset session_state
        st.session_state [ 'user_info' ] = None
        return True

    except KeyError as e:
        return f"{e}"
    except Exception as e:
        return f"{e}"



