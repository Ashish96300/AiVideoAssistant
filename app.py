import streamlit as st
from main import run_pipeline
import tempfile
import os

st.set_page_config(
    page_title="MeetingAI",
    page_icon="🎙️",
    layout="wide",
)

# ---------- SESSION STATE ----------

if "processed" not in st.session_state:
    st.session_state.processed = False

if "result" not in st.session_state:
    st.session_state.result = None


# ---------- SIDEBAR ----------

with st.sidebar:
    st.title("🎙️ MeetingAI")
    st.caption("AI-powered meeting assistant")

    st.divider()

    if st.button("＋ New Meeting", use_container_width=True):
        st.session_state.processed = False
        st.session_state.result = None
        st.rerun()

    st.divider()

    st.subheader("Meeting")

    if st.session_state.result:
        st.success("Current meeting")
        st.write(st.session_state.result["title"])
    else:
        st.caption("No meeting loaded")


# ---------- MAIN UI ----------

st.title("Your AI Meeting Assistant")
st.write(
    "Upload a meeting recording or provide a YouTube URL "
    "to generate insights automatically."
)

st.divider()


# ---------- INPUT ----------

input_type = st.radio(
    "Choose input",
    ["Upload audio", "YouTube URL"],
    horizontal=True,
)

source = None

if input_type == "Upload audio":

    uploaded_file = st.file_uploader(
        "Upload meeting recording",
        type=["wav", "mp3", "m4a", "mp4", "webm"],
    )

    if uploaded_file:
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=os.path.splitext(uploaded_file.name)[1]
        ) as temp_file:

            temp_file.write(uploaded_file.getbuffer())
            source = temp_file.name

else:

    source = st.text_input(
        "YouTube URL",
        placeholder="https://youtube.com/watch?v=..."
    )


language = st.selectbox(
    "Meeting language",
    ["English", "Hindi"],
)


# ---------- PROCESS ----------

if st.button(
    "🚀 Process Meeting",
    type="primary",
    use_container_width=True,
):

    if not source:
        st.warning("Please provide a meeting recording or YouTube URL.")
        st.stop()

    with st.status("Processing meeting...", expanded=True) as status:

        st.write("🎵 Processing audio...")
        
        result = run_pipeline(
            source,
            language.lower()
        )

        st.session_state.result = result
        st.session_state.processed = True

        status.update(
            label="Meeting processed successfully!",
            state="complete",
        )

    st.rerun()
    
# ---------- RESULTS ----------

if st.session_state.processed:

    result = st.session_state.result

    st.divider()

    st.header(result["title"])

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "📋 Summary",
            "✅ Action Items",
            "🎯 Decisions",
            "❓ Open Questions",
            "💬 Chat",
        ]
    )

    with tab1:
        st.subheader("Meeting Summary")
        st.markdown(result["summary"])

    with tab2:
        st.subheader("Action Items")
        st.markdown(result["action_items"])

    with tab3:
        st.subheader("Key Decisions")
        st.markdown(result["key_decisions"])

    with tab4:
        st.subheader("Open Questions")
        st.markdown(result["open_questions"])

    with tab5:
        st.subheader("Chat with your meeting")

        question = st.chat_input(
            "Ask something about this meeting..."
        )

        if question:
            with st.chat_message("user"):
                st.write(question)

            with st.chat_message("assistant"):
                st.write(
                    "Your RAG chain will answer this question here."
                )