
import streamlit as st

def clear_history():
    if 'history' in st.session_state:
        del st.session_state['history']

# Initialize or update the history in session state
def update_history(question, response, retrieved_texts):
    if 'history' not in st.session_state:
        st.session_state.history = []
    # Prepend the new entry to keep the most recent at the top
    st.session_state.history.insert(0, {
        'question': question,
        'response': response,
        'retrieved_texts': retrieved_texts
    })

def display_history():
    if 'history' in st.session_state:
        for entry in st.session_state.history:
            st.markdown(f"**Question:** {entry['question']}")
            st.markdown(f"**Response:** {entry['response']}")
            display_retrieved_texts(entry['retrieved_texts'])
            st.markdown("---")

def get_history_text():
    history_text = ""
    for entry in st.session_state.history:
        history_text += f"Question: {entry['question']}\n"
        history_text += f"Response: {entry['response']}\n"
        for text in entry['retrieved_texts']:
            history_text += f"Retrieved Text: {text['text']}\n"
        history_text += "\n---\n\n"
    return history_text

def display_retrieved_texts(retrieved_texts):
    for response in retrieved_texts:
        score = response['score']
        text = response['text']
        st.markdown(f"**Score:** {score}")
        st.markdown(f"**Text:** {text}")
        st.markdown("---") 

def text_area_callback():
    # This function will be called when the text area changes
    # Set a flag to indicate that Enter was pressed
    st.session_state.enter_pressed = True
