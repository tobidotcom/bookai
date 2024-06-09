import streamlit as st
import os
import base64
import io
from fpdf import FPDF
from replicate import Client
from openai import OpenAI
import wave
import contextlib

# Get the Replicate API token from the environment variable
replicate_api_token = os.environ.get("REPLICATE_API_TOKEN")

# Create an instance of Replicate with the API token
client = Client(replicate_api_token)
openai_client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def generate_outline(prompt):
    messages = [
        {"role": "system", "content": "You are an expert book writer with a vast knowledge of different genres, topics, and writing styles. Your role is to help generate outlines, summaries, and chapters for books on any subject matter, from fiction to non-fiction, from self-help to academic works. Approach each task with professionalism and expertise, tailoring your language and style to suit the specific genre and topic at hand."},
        {"role": "user", "content": f"Based on the following book prompt, generate a comprehensive outline for the book: \n\n{prompt}\n\nOutline:"}
    ]

    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=messages,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.7,
        stream=False  # Disable streaming
    )

    outline = response.choices[0].message.content
    return outline

def generate_pre_summary(prompt, outline):
    messages = [
        {"role": "system", "content": "You are an expert book writer with a vast knowledge of different genres, topics, and writing styles. Your role is to help generate outlines, summaries, and chapters for books on any subject matter, from fiction to non-fiction, from self-help to academic works. Approach each task with professionalism and expertise, tailoring your language and style to suit the specific genre and topic at hand."},
        {"role": "user", "content": f"Based on the following book prompt and outline, craft a compelling pre-summary for the book: \n\nPrompt: {prompt}\n\nOutline: {outline}\n\nPre-summary:"}
    ]

    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=messages,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.7,
        stream=False  # Disable streaming
    )

    pre_summary = response.choices[0].message.content
    return pre_summary

def generate_chapters(prompt, outline, pre_summary):
    chapters = []
    previous_chapter_content = ""
    for chapter_title in outline.split("\n"):
        if chapter_title.strip():
            chapter_content = ""
            while len(chapter_content) < 200:  # Adjust the minimum length to 200 characters
                messages = [
                    {"role": "system", "content": "You are an expert book writer with a vast knowledge of different genres, topics, and writing styles. Your role is to help generate outlines, summaries, and chapters for books on any subject matter, from fiction to non-fiction, from self-help to academic works. Approach each task with professionalism and expertise, tailoring your language and style to suit the specific genre and topic at hand."},
                    {"role": "user", "content": f"Based on the following book prompt, outline, pre-summary, and previous chapter content, generate the content for the chapter titled '{chapter_title}': \n\nPrompt: {prompt}\n\nOutline: {outline}\n\nPre-summary: {pre_summary}\n\nPrevious Chapter Content: {previous_chapter_content}\n\nChapter Content: {chapter_content}"}
                ]

                response = openai_client.chat.completions.create(
                    model="gpt-3.5-turbo-0125",
                    messages=messages,
                    max_tokens=1024,
                    n=1,
                    stop=None,
                    temperature=0.7,
                    stream=False  # Disable streaming
                )

                new_content = response.choices[0].message.content
                chapter_content += new_content

            chapters.append(f"Chapter: {chapter_title}\n\n{chapter_content}")
            previous_chapter_content = chapter_content

    return "\n\n".join(chapters)

def generate_pdf(file_content, file_name):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for line in file_content.split("\n"):
        pdf.multi_cell(0, 10, txt=line, align="L")
    
    # Create a BytesIO object to hold the PDF file
    pdf_bytes = io.BytesIO()
    pdf.output(pdf_bytes)
    
    # Get the PDF file content as bytes
    pdf_file = pdf_bytes.getvalue()
    
    # Encode the PDF file content as base64
    b64 = base64.b64encode(pdf_file).decode()
    href = f'<a href="data:application/pdf;base64,{b64}" download="{file_name}.pdf">Download {file_name}.pdf</a>'
    return href

def upload_audio(audio_file):
    if audio_file:
        # Process the uploaded audio file
        if audio_file.type == "audio/wav":
            with contextlib.closing(wave.open(audio_file, 'r')) as wav:
                frames = wav.readframes(wav.getnframes())
                rate = wav.getframerate()
                duration = wav.getnframes() / float(rate)
                st.write(f"Audio file duration: {duration:.2f} seconds")

                # Save the audio file to disk
                audio_file_path = os.path.join("audio_files", "recorded_audio.wav")
                os.makedirs("audio_files", exist_ok=True)
                with open(audio_file_path, "wb") as f:
                    f.write(audio_file.getvalue())
                st.write(f"Audio file saved to: {audio_file_path}")

        elif audio_file.type == "audio/mpeg":
            with contextlib.closing(wave.open(audio_file, 'r')) as wav:
                frames = wav.readframes(wav.getnframes())
                rate = wav.getframerate()
                duration = wav.getnframes() / float(rate)
                st.write(f"Audio file duration: {duration:.2f} seconds")

                # Save the audio file to disk
                audio_file_path = os.path.join("audio_files", "recorded_audio.mp3")
                os.makedirs("audio_files", exist_ok=True)
                with open(audio_file_path, "wb") as f:
                    f.write(audio_file.getvalue())
                st.write(f"Audio file saved to: {audio_file_path}")

        else:
            st.warning("Unsupported audio file format. Please upload a WAV or MP3 file.")
            return

        st.success("Audio file uploaded and processed successfully!")

def app():
    st.title("Book Generation App")

    prompt = st.text_area("Enter the book prompt:", height=200)

    if "outline" not in st.session_state:
        st.session_state.outline = None

    if "pre_summary" not in st.session_state:
        st.session_state.pre_summary = None

    if "full_book" not in st.session_state:
        st.session_state.full_book = None

    if st.button("Generate Outline"):
        with st.spinner("Generating outline..."):
            st.session_state.outline = generate_outline(prompt)
            st.write("Outline:")
            st.write(st.session_state.outline)

    if "outline" in st.session_state and st.session_state.outline is not None and st.button("Generate Pre-Summary"):
        with st.spinner("Generating pre-summary..."):
            st.session_state.pre_summary = generate_pre_summary(prompt, st.session_state.outline)
            st.write("Pre-Summary:")
            st.write(st.session_state.pre_summary)

    if st.button("Generate Chapters"):
        if "outline" not in st.session_state or st.session_state.outline is None or "pre_summary" not in st.session_state or st.session_state.pre_summary is None:
            st.warning("Please generate an outline and pre-summary first.")
        else:
            with st.spinner("Generating chapters..."):
                st.session_state.full_book = generate_chapters(prompt, st.session_state.outline, st.session_state.pre_summary)
                st.write("Chapters:")
                st.write(st.session_state.full_book)

    if st.session_state.full_book is not None:
        st.markdown(generate_pdf(st.session_state.full_book, "book"), unsafe_allow_html=True)

    # Voice Cloning and Text-to-Speech
    text = st.text_area("Enter the text you want to convert to speech:")
    speaker_file = st.file_uploader("Upload the speaker file (WAV or MP3 format):", type=["wav", "mp3"])

    if st.button("Generate Speech from Text"):
        if text and speaker_file:
            with st.spinner("Generating speech..."):
                speaker_url = client.upload_file(speaker_file)
                output_url = generate_speech(text, speaker_url)
                st.audio(output_url, format="audio/wav")
        else:
            st.warning("Please enter text and upload a speaker file.")

    if st.session_state.pre_summary and st.button("Generate Speech from Pre-Summary"):
        with st.spinner("Generating speech..."):
            speaker_url = client.upload_file(speaker_file)
            output_url = generate_speech(st.session_state.pre_summary, speaker_url)
            st.audio(output_url, format="audio/wav")

    # Upload audio file
    uploaded_audio = st.file_uploader("Upload audio file (WAV or MP3):", type=["wav", "mp3"])
    if uploaded_audio:
        upload_audio(uploaded_audio)

if __name__ == "__main__":
    app()
