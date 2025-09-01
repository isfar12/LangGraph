import streamlit as st
from langgraph_backend import chatbot
from langchain_core.messages import AIMessage,HumanMessage,SystemMessage

CONFIG={
    "configurable":
        {
            "thread_id":"thread_1"
        }
}
if "message_history" not in st.session_state:
    st.session_state["message_history"]=[]

for message in st.session_state["message_history"]:
    with st.chat_message(message["role"]):
        st.text(message["content"])

user_input=st.chat_input("Ask Anything")
if user_input:
    st.session_state["message_history"].append({"role":"user","content":user_input})
    with st.chat_message("user"):
        st.text(user_input)

    response=chatbot.invoke({"messages":[HumanMessage(content=user_input)]},config=CONFIG)
    st.session_state["message_history"].append({"role":"assistant","content":response["messages"][-1].content})
    with st.chat_message("assistant"):
        st.text(response["messages"][-1].content)
