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
import streamlit.components.v1 as components


load_dotenv()

firebaseConfig = {
  "apiKey": os.environ.get("FIREBASE_API_KEY"),
  "authDomain": os.environ.get("FIREBASE_AUTH_DOMAIN"),
  "databaseURL": os.environ.get("FIREBASE_DATABASE_URL"),
  "projectId": os.environ.get("FIREBASE_PROJECT_ID"),
  "storageBucket": os.environ.get("FIREBASE_STORAGE_BUCKET"),
  "messagingSenderId": os.environ.get("FIREBASE_MESSAGING_SENDER_ID"),
  "appId": os.environ.get("FIREBASE_APP")
}

#firebase authentication
firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()

#Database
db = firebase.database()
storage = firebase.storage()
st.set_page_config(layout="centered", page_icon="🏥", page_title="Calmly")
st.write('''<p style="font-size:50px; color:black;">🐧Calmly </p>''',
unsafe_allow_html=True)
st.write('''<p style="font-size:50px; color:black;">This Is For Curious Minds</p>''',
unsafe_allow_html=True)

st.write('''<p style="font-size:26px; color:black;">It's 2023: Still doubting yourself?</p>''',
unsafe_allow_html=True)

st.write('''<p style="font-size:26px; color:black;">Measure & discover your mental strengths today </p>''',
unsafe_allow_html=True)

st.sidebar.title("OUR COMMUNITY")
menu = ['Login', 'Sign up']
#Authentication
choice = st.sidebar.selectbox('Login/Signup',menu,key=menu)

email = st.sidebar.text_input('Email')
password = st.sidebar.text_input('Password',type = 'password')

# Sign up Block
if choice == 'Sign up':
    handle = st.sidebar.text_input(
        'Please input your app handle name', value='Default')
    submit = st.sidebar.button('Create my account')

    if submit:
        # Create a new user account
        user = auth.create_user_with_email_and_password(email, password)
        st.success('Your account has been created successfully!')
        # Save the user's handle and ID to the Realtime Database
        db.child('users').child(user['localId']).set({
            'handle': handle,
            'id': user['localId'],
            'user_type': 'user'
        })
        st.title('Welcome, ' + handle + '!')
        st.info('Please log in using the Login dropdown menu.')

# Login Block
if choice == 'Login':
    login = st.sidebar.button('Login')
    try:
        if login:
            user = auth.sign_in_with_email_and_password(email,password)
            user_type = db.child('users').child(user['localId']).child('user_type').get().val()
            if user_type=='user':
                st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)
                bio = st.radio('Jump to',['Relax','Dashboard','Home','Settings '])
                st.experimental_rerun()
                if bio=='Relax':
                    st.write("Relax !!!")
                    components.html('<iframe style="border-radius:20px" src="https://open.spotify.com/embed/playlist/79CdkHFoF0VYvHEzFFXokr?utm_source=generator" width="100%" height="352" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>', height=400, scrolling=True)

                elif bio == 'Home':
                    if 'count' not in st.session_state or 'list_ans' not in st.session_state or 'sentiment_count' not in st.session_state or 'positive_risk_percentage' not in st.session_state or 'negative_risk_percentage' not in st.session_state or 'neutral_risk_percentage' not in st.session_state or 'flag' not in st.session_state:
                        st.session_state['count'] = 0
                        st.session_state['list_ans'] = []
                        st.session_state['sentiment_count'] = 0
                        st.session_state['positive_risk_percentage'] = 0
                        st.session_state['negative_risk_percentage'] = 0
                        st.session_state['neutral_risk_percentage'] = 0
                        st.session_state['flag'] = False

                    @st.cache_data
                    def get_models():
                        # it may be necessary for other frameworks to cache the model
                        # seems pytorch keeps an internal state of the conversation
                        model_name = "facebook/blenderbot-400M-distill"
                        tokenizer = BlenderbotTokenizer.from_pretrained(model_name)
                        model = BlenderbotForConditionalGeneration.from_pretrained(model_name)
                        return tokenizer, model

                    if "history" not in st.session_state:
                        st.session_state.history = []

                    st.title("Calmly 🐧")
                    st.write('Small Conversations, Peaceful Output')

                    def sentiment_scores(sentence):
                        sid_obj = SentimentIntensityAnalyzer()
                        # if "st.session_state.sentiment_dict" not in st.session_state:
                        #     st.session_state.sentiment_dict = sid_obj.polarity_scores(sentence)
                        sentiment_dict = sid_obj.polarity_scores(sentence)
                        st.session_state.sentiment_count+=1
                        st.session_state.negative_risk_percentage+=sentiment_dict['neg']
                        st.session_state.neutral_risk_percentage+=sentiment_dict['neu']
                        st.session_state.positive_risk_percentage+=sentiment_dict['pos']
                        # print(st.session_state.sentiment_dict['compound'])
                        if st.session_state.sentiment_count>2:
                            if sentiment_dict['compound']>=0.05:
                            
                                st.write(f"The Current Patient is Doing Great !!!{(st.session_state.positive_risk_percentage/5)*100}")
                            elif sentiment_dict['compound']<=-0.05:
                            
                                st.write(f"He would Need Help {(st.session_state.negative_risk_percentage/5)*100}")
                            else:
                                st.write(f"Moderate risk of mental health issues.{(st.session_state.neutral_risk_percentage/5)*100}")

                    def generate_answer():
                        tokenizer, model = get_models()
                        user_message = st.session_state.input_text
                        inputs = tokenizer(st.session_state.input_text, return_tensors="pt")
                        st.session_state.count+=1
                        st.session_state.list_ans.append(user_message)
                        if st.session_state.count>2:
                            st.session_state.flag=True
                        while st.session_state.flag:
                            for i in st.session_state.list_ans:
                                sentiment_scores(i)
                            st.session_state.flag = False
                            st.session_state.count = 0
                        result = model.generate(**inputs)
                        message_bot = tokenizer.decode(
                            result[0], skip_special_tokens=True
                        )  # .replace("<s>", "").replace("</s>", "")

                        st.session_state.history.append({"message": user_message, "is_user": True})
                        st.session_state.history.append({"message": message_bot, "is_user": False})


                    st.text_input("Share what you feel !!!", key="input_text", on_change=generate_answer)

                    for chat in st.session_state.history:
                        st_message(**chat)  # unpacking

                    hide_streamlit_style = """
                                <style>
                                footer {visibility: hidden;}
                                </style>
                                """
                    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

                    # st.markdown("""
                    # <style>
                    # body {
                    #   background: #ff0099; 
                    #   background: -webkit-linear-gradient(to right, #ff0099, #493240); 
                    #   background: linear-gradient(to right, #ff0099, #493240); 
                    # }
                    # </style>
                    #     """, unsafe_allow_html=True)


    except:
        st.sidebar.error('incorrect email and password !')

# st.markdown(
#     f"""
#     <style>
#     .reportview-container {{
#         background-color: #f6efe6
#     }}
#    .sidebar .sidebar-content {{
#         background-color: #4e4e4e;
#         color: #ffffff;
#     }}
#     </style>
#     """,
#     unsafe_allow_html=True
# )

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)