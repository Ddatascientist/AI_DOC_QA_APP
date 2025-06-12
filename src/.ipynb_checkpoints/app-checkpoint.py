import streamlit as st
from openai import OpenAI



st.title("")

# openai.api_key = DEEPSEEK_API
client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=DEEPSEEK_API,
)

if 'llm_model' not in st.session_state:
    st.session_state['llm_model'] = 'deepseek/deepseek-r1:free'

# chat history
if 'messages' not in st.session_state:
    st.session_state.messages = []

# chat history display
for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

# user input
prompt = st.chat_input("Ask IBOT....")
if prompt:
    with st.chat_message('user'):
        st.markdown(prompt)

        # update message
        st.session_state.messages.append({'role': 'user', 'content': prompt})

    # display bot response in chat
    with st.chat_message('assistant'):
        message_holder = st.empty()
        full_res = ""
        for response in client.chat.completions.create(
            model=st.session_state['llm_model'],
            messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages], stream=True,
        ):
            if response.choices[0].delta.content:
                full_res += response.choices[0].delta.content
                message_holder.markdown(full_res + "| ")
        message_holder.markdown(full_res)
        
    # update message
    st.session_state.messages.append({'role': 'assistant', 'content': full_res})







