#loading necessary libraries
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage,HumanMessage
from typing import TypedDict,Annotated
from langgraph.graph import StateGraph,START,END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
from dotenv import load_dotenv
import os
import sqlite3

#loading files from env folder
load_dotenv()

#llm requirements
MODEL2_API=os.getenv("OPENROUTER_MODEL2_KEY")
MODEL2_NAME=os.getenv("OPENROUTER_MODEL2_NAME")
MODEL2_URL=os.getenv("OPENROUTER_BASE_URL2")

#llm call
model=ChatOpenAI(api_key=MODEL2_API,
                  model=MODEL2_NAME,
                  base_url=MODEL2_URL)

#define state
class ChatState(TypedDict):
    messages:Annotated[list[BaseMessage],add_messages]

#define node-Function
def chat_node(state:ChatState):
    messages=state['messages']
    #pass to llm
    response=model.invoke(messages)
    #return to state
    return {'messages':[response]}

#creating a connection
conn=sqlite3.connect(database="chats.db",check_same_thread=False)
# Checkpointer
checkpointer = SqliteSaver(conn=conn)

#define graph object
graph=StateGraph(ChatState)
#define nodes
graph.add_node('chat_node',chat_node)
#define edges
graph.add_edge(START,'chat_node')
graph.add_edge('chat_node',END)
#compile
chatbot=graph.compile(checkpointer=checkpointer)

#for loading thread history saved in db
def retrieve_all_threads():
    
    all_threads=set()
    for item in checkpointer.list(None):
        all_threads.add(item.config['configurable']['thread_id'])
    return list(all_threads)
    

    