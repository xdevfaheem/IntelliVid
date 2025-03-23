import streamlit as st

from core.main import VideoIntelligence

# Set page configuration
st.set_page_config(
    page_title="IntelliVid",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown(
    """
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
        color: #1E88E5;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        color: #42A5F5;
    }
    .info-text {
        font-size: 1rem;
        color: #424242;
    }
    .highlight-text {
        background-color: #E3F2FD;
        padding: 0.5rem;
        border-radius: 0.3rem;
        border-left: 3px solid #1E88E5;
    }
    .success-message {
        background-color: #E8F5E9;
        color: #2E7D32;
        padding: 0.5rem;
        border-radius: 0.3rem;
        border-left: 3px solid #2E7D32;
    }
    .error-message {
        background-color: #FFEBEE;
        color: #C62828;
        padding: 0.5rem;
        border-radius: 0.3rem;
        border-left: 3px solid #C62828;
    }
    .stButton>button {
        background-color: #1E88E5;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 0.3rem;
        font-weight: 600;
    }
    .stButton>button:hover {
        background-color: #1565C0;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Initialize session state
if "video_processor" not in st.session_state:
    st.session_state.video_processor = None
if "video_path" not in st.session_state:
    st.session_state.video_path = None
if "processing_complete" not in st.session_state:
    st.session_state.processing_complete = False
if "highlight_video" not in st.session_state:
    st.session_state.highlight_video = None
if "moment_video" not in st.session_state:
    st.session_state.moment_video = None
if "token_count" not in st.session_state:
    st.session_state.token_count = {"input": 0, "output": 0, "total": 0}


# Helper functions
def process_video(video_source):
    try:
        with st.spinner("Processing video... This may take a moment."):
            st.session_state.video_processor = VideoIntelligence(video_source)
            st.session_state.video_path = st.session_state.video_processor.video_path
            st.session_state.token_count = st.session_state.video_processor.token_count
            st.session_state.processing_complete = True
            return True
    except Exception as e:
        st.error(f"Error processing video: {str(e)}")
        return False


def display_video(video_path):
    if video_path:
        st.video(video_path)
    else:
        st.warning("No video available to display.")


# Main app header
st.markdown(
    "<div class='main-header'>AI-powered Video Analysis Application 🎥🧠</div>",
    unsafe_allow_html=True,
)
st.markdown(
    "<div class='info-text'>Analyze, question, and extract highlights/moments from your videos using AI.</div>",
    unsafe_allow_html=True,
)

# Sidebar
with st.sidebar:
    st.markdown("<div class='sub-header'>Video Input</div>", unsafe_allow_html=True)

    input_method = st.radio(
        "Select input method:", ["YouTube URL", "Upload Video", "Video URL"]
    )

    if input_method == "YouTube URL":
        youtube_url = st.text_input("Enter YouTube URL:")
        if st.button("Process Video") and youtube_url:
            if process_video(youtube_url):
                st.success("Video processed successfully!")

    elif input_method == "Upload Video":
        uploaded_file = st.file_uploader(
            "Choose a video file:", type=["mp4", "avi", "mov", "mkv"]
        )
        if uploaded_file and st.button("Process Video"):
            if process_video(uploaded_file.name):
                st.success("Video processed successfully!")

    elif input_method == "Video URL":
        video_url = st.text_input("Enter video URL (must end with .mp4):")
        if st.button("Process Video") and video_url:
            if video_url.endswith(".mp4"):
                if process_video(video_url):
                    st.success("Video processed successfully!")
            else:
                st.error("URL must end with .mp4")

    # Token usage information
    if st.session_state.processing_complete:
        st.markdown("<div class='sub-header'>Token Usage</div>", unsafe_allow_html=True)
        st.markdown(
            f"""
        <div class='highlight-text'>
        Input tokens: {st.session_state.token_count["input"]}<br>
        Output tokens: {st.session_state.token_count["output"]}<br>
        Total tokens: {st.session_state.token_count["total"]}
        </div>
        """,
            unsafe_allow_html=True,
        )

# Main content
if st.session_state.processing_complete:
    tabs = st.tabs(["Chat with Video", "Highlight Generator", "Find in Video"])

    # Video Analysis Tab
    with tabs[0]:
        st.markdown(
            "<div class='sub-header'>Video Question Answering</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<div class='info-text'>Ask questions about the video content.</div>",
            unsafe_allow_html=True,
        )

        if st.session_state.video_processor:
            display_video(st.session_state.video_processor.video_path)

            user_question = st.text_input("Ask a question about the video:")
            if st.button("Get Answer") and user_question:
                with st.spinner("Analyzing video..."):
                    answer = st.session_state.video_processor.chat(user_question)
                    st.session_state.token_count = (
                        st.session_state.video_processor.token_count
                    )

                st.markdown(
                    f"<div class='highlight-text'>{answer}</div>",
                    unsafe_allow_html=True,
                )

    # Highlight Generation Tab
    with tabs[1]:
        st.markdown(
            "<div class='sub-header'>Highlight Generation</div>", unsafe_allow_html=True
        )
        st.markdown(
            "<div class='info-text'>Extract key moments from the video.</div>",
            unsafe_allow_html=True,
        )

        if st.session_state.video_processor:
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Original Video**")
                display_video(st.session_state.video_processor.video_path)

            with col2:
                st.markdown("**Highlights**")
                if st.session_state.highlight_video:
                    display_video(st.session_state.highlight_video)
                else:
                    st.info("Generate highlights to view them here")

            if st.button("Generate Highlights"):
                with st.spinner("Generating highlights..."):
                    highlight_path, message = (
                        st.session_state.video_processor.generate_highlight()
                    )
                    st.session_state.token_count = (
                        st.session_state.video_processor.token_count
                    )

                    if highlight_path:
                        st.session_state.highlight_video = highlight_path
                        st.success(message)
                    else:
                        st.info(message)

    # Visual Grounding Tab
    with tabs[2]:
        st.markdown(
            "<div class='sub-header'>Visual Grounding</div>", unsafe_allow_html=True
        )
        st.markdown(
            "<div class='info-text'>Find specific moments in the video.</div>",
            unsafe_allow_html=True,
        )

        if st.session_state.video_processor:
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Original Video**")
                display_video(st.session_state.video_processor.video_path)

            with col2:
                st.markdown("**Identified Moment**")
                if st.session_state.moment_video:
                    display_video(st.session_state.moment_video)
                else:
                    st.info("Identify a moment to view it here")

            moment_query = st.text_input("Describe the moment you're looking for:")
            if st.button("Find Moment") and moment_query:
                with st.spinner("Searching for moment..."):
                    moment_path, message = (
                        st.session_state.video_processor.identify_moment(moment_query)
                    )
                    st.session_state.token_count = (
                        st.session_state.video_processor.token_count
                    )

                    if moment_path:
                        st.session_state.moment_video = moment_path
                        st.success(message)
                    else:
                        st.info(message)
else:
    # Display instructions when no video is processed
    st.markdown(
        """
    <div class='highlight-text'>
    <b>Getting Started:</b><br>
    1. Choose an input method from the sidebar (YouTube URL, Upload Video, or Video URL)<br>
    2. Process the video<br>
    3. Use the tabs to analyze, generate highlights, or find specific moments
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Display sample use cases
    st.markdown("<div class='sub-header'>Features</div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
        <div class='highlight-text'>
        <b>Video Question Answering</b><br>
        Ask natural language questions about the video content and get detailed answers.
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
        <div class='highlight-text'>
        <b>Highlight Generator</b><br>
        Automatically extract and summarize key moments from the video.
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            """
        <div class='highlight-text'>
        <b>Find in Video</b><br>
        Identify/Find specific moments based on your descriptions.
        </div>
        """,
            unsafe_allow_html=True,
        )
