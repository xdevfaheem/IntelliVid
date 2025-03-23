# Video Intelligence
should i call it intelligent? prob not... after all it's just splitting 1 FPS and adding timestamp feeding those frames/image into the model with prompt. BUT! it is capable of understanding (atleast 1FPS as of now, no native video support (video gets splitted into image/audio/second)) what's going on (by align the frame with it's corresponding audio buffer). Eventhough we know the model internal information flow, and how it propagate, we don't clearly know what's happening inside the learning algorithm when it (architecture+algo+weight) interacts with the data. (for more, refer G. hinton and other AI doomers (who knows their craft)). Anyways... enough yap, getting back to my crappy wrapper app.

# Run it

```bash
git clone https://github.com/xdevfaheem/VidIntel.git
cd VidIntel
uv sync
export GOOGLE_API_KEY='Your Gemini API key'
source .venv/activate/bin
streamlit run ui.py
```
