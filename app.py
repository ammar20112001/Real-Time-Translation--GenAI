import threading
import time
import streamlit as st
from model import TranslatorModel
import io
from tempfile import NamedTemporaryFile

# Set up the Streamlit app title
st.title("Healthcare Translation App")

# Create a two-column layout: left side for controls, right side for transcripts and other outputs
col1, col2 = st.columns([1, 2])  # Left side is smaller (1), right side is larger (2)

# Buttons and file upload on the left side (column 1)
with col1:
    record_but = st.button("Start Real Time Recording")
    stop_but = st.button("Stop Real Time Recording")
    tran_but = st.button("Change Translate")
    clear_but = st.button("Clear")
    play_audio = st.button("Play Audio")
    audio = st.file_uploader("Upload an audio file", type=["mp3"])

# Initialize model in Streamlit session state
if 'model' not in st.session_state:
    st.session_state.model = TranslatorModel()

if 'record' not in st.session_state:
    st.session_state.record = False

with col2:
    if 'source_placeholder' not in st.session_state:
        st.session_state.source_placeholder = st.empty()

    if 'target_placeholder' not in st.session_state:
        st.session_state.target_placeholder = st.empty()

# Access the model stored in session state
model = st.session_state.model
record = st.session_state.record
source_placeholder = st.session_state.source_placeholder
target_placeholder = st.session_state.target_placeholder

# Function to handle speech-to-text conversion
def speech_to_text():
    model.SpeechToTranscript()

# Function to handle continuous translation
def translate(run_once=False):
    if not run_once:
        model.TranscriptTranslator()
    else:
        model.TranscriptTranslator(run_once=True)

# Placeholder elements for updating the transcripts
with col2:
    source_placeholder.write(f"Source transcript: {' '.join(model.src_transcript)}")
    target_placeholder.write(f"Target transcript: {model.tgt_transcript}")

# Handling buttons' actions
if record_but:
    model.STOP_LISTENING = False
    record = True

    # Start speech-to-text and translation in background threads
    t1 = threading.Thread(target=speech_to_text)
    t2 = threading.Thread(target=translate)
    t1.start()
    t2.start()

    # Update the transcripts in the main loop
    while record:
        source_text = " ".join(model.src_transcript)
        target_text = model.tgt_transcript
        with col2:
            # Display updated transcripts
            source_placeholder.write(f"Source transcript: {source_text}")
            target_placeholder.write(f"Target transcript: {target_text}")
        
        time.sleep(1)  # Update every second

if stop_but:
    model.STOP_LISTENING = True
    record = False  # Stopping the recording

if tran_but:
    model.STOP_LISTENING = False
    translate(run_once=True)
    source_placeholder.write(f"Source transcript: {' '.join(model.src_transcript)}")
    target_placeholder.write(f"Target transcript: {model.tgt_transcript}")
    model.STOP_LISTENING = True

if clear_but:
    model.src_transcript = []
    model.tgt_transcript = ""
    source_placeholder.write("Source transcript: ")
    target_placeholder.write("Target transcript: ")

if play_audio:
    try:
        # Step 2: Text-to-Speech
        audio_content = model.TranscriptToSpeech()
        
        # Step 3: Play Translated Audio
        st.audio(audio_content, format="audio/mp3")
    except:
        pass

# Handling audio file upload
if audio is not None:
    # Save the uploaded file to a temporary file on disk
    with NamedTemporaryFile(suffix=".mp3", delete=False) as temp:
        temp.write(audio.getvalue())  # Write the audio content to the temporary file
        temp.seek(0)
        
        # Get the path of the temporary file
        temp_file_path = temp.name
        
        # Pass the file path to the model function (assumes `SpeechToTranscript` expects a file path)
        result = model.SpeechToTranscript(audio_sm=temp_file_path)

    # Display the transcription result on the right side
    with col2:
        st.write(f"Source sentence: {" ".join(model.src_transcript)}")
        st.write(f"Target sentence: {model.TranscriptTranslator(run_once=True)}")
