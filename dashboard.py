import streamlit as st
import openai
import pinecone
import utils
from streamlit_utils import *
import os


st.title(":high_brightness: nanobot")
st.write("**I find the details**")


# Set OpenAI and Pinecone API keys
openai.api_key = os.getenv('OPENAI_API_KEY')#
pinecone.init(api_key=os.getenv('PINECONE_API_KEY'), environment='gcp-starter')#

openai_embedding_model='text-embedding-ada-002'
openai_completion_model='gpt-3.5-turbo'
index = pinecone.Index('utech-manual')


with st.sidebar:
    # use text_input to bring in your OpenAI API key 

    api_key = st.text_input('OpenAI API Key:', type='password')
    if api_key:
        os.environ['OPENAI_API_KEY'] = api_key
        # openai.api_key = os.environ['OPENAI_API_KEY']

    st.sidebar.markdown("---")

    st.subheader("Retrieval Parameters:")

    # input the top-k number, k increase the search effectiveness, but is more expensive
    k = st.number_input('top-k most salient embeds', min_value=1, max_value=50, value=3, on_change=clear_history)

    st.sidebar.markdown("---")

    st.subheader(":file_folder: Import Question List:")
    # sidebar - file uploader widget, drag and drop, browse button works on windows not on mac
    question_file = st.file_uploader('Drop files below', type=['json'])
    st.sidebar.markdown("---")

    st.subheader(":file_folder: Add Retrieval Data:")
    # sidebar - file uploader widget, drag and drop, browse button works on windows not on mac
    data_file = st.file_uploader('Drop files below', type=['pdf'])

    # call the chunk size mehtod that sets the number
    chunk_size = st.number_input('Chunk size:', min_value=100, max_value=2048, value=512, on_change=clear_history)

    # click this sidebard button to add data
    add_data = st.button('Embed & Add Data', on_click=clear_history)

# Initialize the enter_pressed state if it doesn't exist
if 'enter_pressed' not in st.session_state:
    st.session_state.enter_pressed = False

# Create a dropdown menu
indexes = pinecone.list_indexes()
selected_index = st.selectbox('Select a Pinecone Index', indexes)

# Text area with a callback
user_message = st.text_area("Enter your question here:", key="user_message", on_change=text_area_callback)
retrieved_texts = utils.pinecone_prompt_and_retrieve(user_message, k=k)

# Button click or Enter press triggers the response
if st.button("Get Response") or st.session_state.enter_pressed:
    if user_message:
        with st.spinner('Retriving results ...'):
            try:
                retrieved_texts = utils.pinecone_prompt_and_retrieve(user_message, k=k)
                system_message_pinecone = utils.get_system_message(retrieved_texts)
                messages = [
                    {'role': 'system', 'content': system_message_pinecone},
                    {'role': 'user', 'content': f"{utils.delimiter}{user_message}{utils.delimiter}"}
                ]
                result = utils.get_completion_from_messages(messages)

                # Once processing is done, display results
                st.write("Result:")
                st.write(f"**Result:** {result}")
                st.markdown("---")
                # display_retrieved_texts(retrieved_texts)
     
            except Exception as e:
                st.write(f"Error: {e}")

            update_history(user_message, result, retrieved_texts)

            # Reset the flag
            st.session_state.enter_pressed = False

    else:
        st.write("Please provide an API Key and a prompt")

if 'history' in st.session_state and st.session_state.history:
    history_text = get_history_text()
    st.download_button(
        label="Download History",
        data=history_text,
        file_name="query_history.txt",
        mime="text/plain"
    )
# Call this function where you want to display the history
display_history()

