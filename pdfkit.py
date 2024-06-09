import streamlit as st
import os
import base64
import pdfkit
from fpdf import FPDF
from replicate import Client
from openai import OpenAI

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
    html_content = f"<pre>{file_content}</pre>"
    pdfkit.from_string(html_content, f"{file_name}.pdf")
    return f"{file_name}.pdf"

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

            # Generate and display the PDF for the outline
            pdf_file = generate_pdf(st.session_state.outline, "book_outline")
            with open(pdf_file, "rb") as f:
                base64_pdf = base64.b64encode(f.read()).decode('utf-8')
            pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="800" height="600" type="application/pdf"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)

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
        pdf_file = generate_pdf(st.session_state.full_book, "book")
        with open(pdf_file, "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode('utf-8')
        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="800" height="600" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)

if __name__ == "__main__":
    app()
