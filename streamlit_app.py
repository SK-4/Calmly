import streamlit as st
from streamlit_chat import message as st_message
from transformers import BlenderbotTokenizer, BlenderbotForConditionalGeneration
# import streamlit_authenticator as stauth
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


if 'count' not in st.session_state or 'list_ans' not in st.session_state or 'sentiment_count' not in st.session_state or 'positive_risk_percentage' not in st.session_state or 'negative_risk_percentage' not in st.session_state or 'neutral_risk_percentage' not in st.session_state or 'flag' not in st.session_state:
    st.session_state['count'] = 0
    st.session_state['list_ans'] = []
    st.session_state['sentiment_count'] = 0
    st.session_state['positive_risk_percentage'] = 0
    st.session_state['negative_risk_percentage'] = 0
    st.session_state['neutral_risk_percentage'] = 0
    st.session_state['flag'] = False

@st.cache_resource
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
        # if (st.session_state.positive_risk_percentage/5)*100 >=60:
            st.write(f"Low risk of mental health issues. Keep up the good work!!!{(st.session_state.positive_risk_percentage/5)*100}")
        elif sentiment_dict['compound']<=-0.05:
        # elif (st.session_state.negative_risk_percentage/5)*100 >=60:
            st.write(f"High risk of mental health issues. Please seek professional help immediately.{(st.session_state.negative_risk_percentage/5)*100}")
        else:
            st.write(f"Moderate risk of mental health issues. Please seek help if necessary.{(st.session_state.neutral_risk_percentage/5)*100}")

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