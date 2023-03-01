#modules
import pyrebase #python wrapper of firebase
import streamlit as st
from datetime import datetime
import streamlit as st
from streamlit_chat import message as st_message
from transformers import BlenderbotTokenizer, BlenderbotForConditionalGeneration
# import streamlit_authenticator as stauth
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import os 
from dotenv import load_dotenv
import user

load_dotenv()

#configuration_key 
#configuration_key 
firebaseConfig = {
  "apiKey": os.environ.get("FIREBASE_API_KEY"),
  "authDomain": os.environ.get("FIREBASE_AUTH_DOMAIN"),
  "databaseURL": os.environ.get("FIREBASE_DATABASE_URL"),
  "projectId": os.environ.get("FIREBASE_PROJECT_ID"),
  "storageBucket": os.environ.get("FIREBASE_STORAGE_BUCKET"),
  "messagingSenderId": os.environ.get("FIREBASE_MESSAGING_SENDER_ID"),
  "appId": os.environ.get("FIREBASE_APP")
}


# Initialize Firebase
firebase = pyrebase.initialize_app(firebaseConfig)

# Get a reference to the Firebase Authentication and Realtime Database services
auth = firebase.auth()
db = firebase.database()
st.set_page_config(layout="centered", page_icon="🏥", page_title="Doctor's Dashboard")
#Doctors Homepage !!!
st.write('''<p style="font-size:50px; color:white;">🐧 Calmly</p>''',
unsafe_allow_html=True)
st.write('''<p style="font-size:50px; color:white;">Track your Patients brain health </p>''',
unsafe_allow_html=True)

st.write('''<p style="font-size:26px; color:white;">we’ve developed solid tools via which you can measure your patients mental strength before you.</p>''',
unsafe_allow_html=True)

st.write('''<p style="font-size:25px; color:white;"> Curious about how this happens?</p>''',
unsafe_allow_html=True)
# Sidebar menu
st.sidebar.title("OUR COMMUNITY")
menu = ['Login', 'Sign up']
choice = st.sidebar.selectbox('Login/Signup', menu, key=menu)

# Sign up Block
if choice == 'Sign up':
    handle = st.sidebar.text_input(
        'Please input your app handle name', value='Default')
    email = st.sidebar.text_input('Enter your email address')
    password = st.sidebar.text_input('Enter your password', type='password')
    submit = st.sidebar.button('Create my account')

    if submit:
        # Create a new user account
        user = auth.create_user_with_email_and_password(email, password)
        st.success('Your account has been created successfully!')
        # Save the user's handle and ID to the Realtime Database
        db.child('users').child(user['localId']).set({
            'handle': handle,
            'id': user['localId'],
            'user_type': 'doctor'
        })
        st.title('Welcome, ' + handle + '!')
        st.info('Please log in using the Login dropdown menu.')

# Login Block
if choice == 'Login':
    email = st.sidebar.text_input('Enter your email address')
    password = st.sidebar.text_input('Enter your password', type='password')
    login = st.sidebar.button('Login')

    if login:
        try:
            # Authenticate the user
            user = auth.sign_in_with_email_and_password(email, password)
            # Check if the user is a doctor
            user_type = db.child('users').child(user['localId']).child('user_type').get().val()
            if user_type == 'doctor':
                st.write('Hello, doctor!')
            else:
                st.sidebar.error('Invalid email/password or you might switch to user')
        except:
            st.error('Invalid email or password. Please try again.')

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)