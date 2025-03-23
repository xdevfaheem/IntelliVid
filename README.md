# IntelliVid🎥🧠

An MLLM-powered video analysis application that transforms how you interact with video content. Leveraging Google's latest Gemini 2.0 series model, this application aims to provides intelligent video analysis, visual qa, highlight generation, and moment identification capabilities.

## ✨ Features

### 🔍 Video Question Answering (VQA)
Ask natural language questions about any video and receive detailed, contextually-aware answers. The system understands visual content, actions, and context within the video to provide accurate responses.

Examples:
- "What is the main topic of this tutorial?"
- "How many people appear in this video?"
- "What happens after the car turns left?"

### 🔆 Highlight Generation
Automatically identify and extract the most significant moments from any video. Perfect for:
- Creating summaries of lengthy content
- Extracting key points from lectures or presentations
- Identifying exciting moments from events or sports videos

### 🎯 Visual Grounding
Describe a specific moment, object, or action, and the app will locate and extract exactly that portion of the video. Simply describe what you're looking for in natural language.

Examples:
- "Show me the part where the cat jumps onto the table"
- "Find the moment when the speaker discusses climate change"
- "Extract the scene with the sunset view"


## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- FFmpeg installed on your system
- uv (if not already, you must. it's good)

### Installation

1. Clone this repository:
```bash
git clone https://github.com/xdevfaheem/IntelliVid.git
cd IntelliVid
```

2. Install required dependencies:
```bash
uv sync
```

3. Run the application:
```bash
uv python -m streamlit run ui.py
```

## 📖 How to Use

1. **Select Input Method**:
   - YouTube URL: Paste any YouTube video link
   - Upload Video: Upload a video file from your device
   - Video URL: Enter a public/direct URL to a video file.

2. **Process the Video**:
   - Click "Process Video" to analyze the content
   - Wait for the processing to complete (time varies based on video length)

3. **Interact with Your Video**:
   - **Video Analysis**: Ask questions about the video content
   - **Highlight Generation**: Extract key moments automatically
   - **Visual Grounding**: Find specific moments by describing them
   
## 🛠️ Tech Stack

- Python + Google's Gemini 2.0 Flash(001) model (as i find it more suitabe for video understanding usecases)
- Streamlit for intuitive UI/UX
- FFmpeg for high-quality video manipulation
- Pydantic for robust data validation (structured output schema)
- [pytubefix](https://github.com/JuanBindez/pytubefix) (pytube unmaintained :/) for YouTube integration

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributions

Contributions, issues, and feature requests are always welcome! 
