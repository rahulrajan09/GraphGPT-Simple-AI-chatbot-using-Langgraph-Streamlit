import streamlit as st
from langgraph_sqllitedb_backend import chatbot,retrieve_all_threads
from langchain_core.messages import HumanMessage,AIMessage
import uuid



#--------------------------------------------Utility Functions ------------------------------------------#

def generate_thread_id():
    thread_id=uuid.uuid4()
    return thread_id

def reset_chat():
    thread_id=generate_thread_id()
    st.session_state['thread_id']=thread_id
    add_thread(st.session_state['thread_id'])
    st.session_state['message_history']=[]

def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)
        
def load_conversation(thread_id):
    state=chatbot.get_state(config={'configurable': {'thread_id': thread_id}})
    #if state present return it or else reurn an empty list
    return state.values.get('messages',[])

#--------------------------------------------Session Setup ----------------------------------------------#

#appending user input to session state
if 'message_history' not in st.session_state:
    st.session_state['message_history']=[]
    
if 'thread_id' not in st.session_state:
    st.session_state['thread_id']=generate_thread_id()

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads']=retrieve_all_threads()
    
add_thread(st.session_state['thread_id'])

#--------------------------------------------Sidebar UI--------------------------------------------------#

st.sidebar.title("GraphGPT")

if st.sidebar.button("New Chat"):
    reset_chat()

st.sidebar.header("My Conversation")

for thread_id in st.session_state['chat_threads'][::-1]:
    if st.sidebar.button(str(thread_id)):
        
        st.session_state['thread_id']=thread_id
        messages=load_conversation(thread_id)
        
        #converting our messages in humanmessage and aimessage form to role and content form
        temp_messages=[]
        
        for msg in messages:
            if isinstance(msg,HumanMessage):
                role="user"
            else:
                role="ai"
            temp_messages.append({"role":role,"content":msg.content})
            
        st.session_state['message_history']=temp_messages


#--------------------------------------------Main  UI----------------------------------------------------#

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
        
    CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']}}
    #add to session history first
    with st.chat_message('ai'):
        
        def ai_only_stream():
            for message_chunk,metadata in chatbot.stream(
                {'messages':[HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode='messages'
            ):
                if isinstance(message_chunk,AIMessage):
                    #yield only required tokens
                    yield message_chunk.content
            
        ai_message=st.write_stream(ai_only_stream)
        
    st.session_state['message_history'].append({'role':'ai','content':ai_message})
       