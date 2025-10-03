import streamlit as st
from langgraph_backend import chatbot
from langchain_core.messages import HumanMessage,AIMessage

CONFIG = {'configurable': {'thread_id': 'thread-1'}}

#appending user input to session state
if 'message_history' not in st.session_state:
    st.session_state['message_history']=[]

#showing conversation history
for messages in st.session_state['message_history']:
    with st.chat_message(messages['role']):
        st.text(messages['content'])

user_input=st.chat_input("Type here....")

if user_input:
    #add to session history first
    st.session_state['message_history'].append({'role':'user','content':user_input}) 
    with st.chat_message('user'):
        st.text(user_input)
        
    
    response=chatbot.invoke({'messages':[HumanMessage(content=user_input)]},config=CONFIG)
    ai_message=response['messages'][-1].content

    #add to session history first
    st.session_state['message_history'].append({'role':'ai','content':ai_message})
    with st.chat_message('ai'):
        st.text(ai_message)