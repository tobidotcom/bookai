import streamlit as st
from openai import OpenAI
import requests

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
pdfshift_api_key = st.secrets["PDFSHIFT_API_KEY"]

def generate_outline(prompt):
    messages = [
        {"role": "system", "content": "You are an expert book writer with a vast knowledge of different genres, topics, and writing styles. Your role is to help generate outlines, summaries, and chapters for books on any subject matter, from fiction to non-fiction, from self-help to academic works. Approach each task with professionalism and expertise, tailoring your language and style to suit the specific genre and topic at hand."},
        {"role": "user", "content": f"Based on the following book prompt, generate a comprehensive outline for the book: \n\n{prompt}\n\nOutline:"}
    ]

    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=messages,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.7
    )

    outline = response.choices[0].message.content
    return outline

def generate_pre_summary(prompt, outline):
    messages = [
        {"role": "system", "content": "You are an expert book writer with a vast knowledge of different genres, topics, and writing styles. Your role is to help generate outlines, summaries, and chapters for books on any subject matter, from fiction to non-fiction, from self-help to academic works. Approach each task with professionalism and expertise, tailoring your language and style to suit the specific genre and topic at hand."},
        {"role": "user", "content": f"Based on the following book prompt and outline, craft a compelling pre-summary for the book: \n\nPrompt: {prompt}\n\nOutline: {outline}\n\nPre-summary:"}
    ]

    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=messages,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.7
    )

    pre_summary = response.choices[0].message.content
    return pre_summary

def generate_chapters(prompt, outline, pre_summary):
    chapters = []
    previous_chapter_content = ""
    for chapter_title in outline.split("\n"):
        if chapter_title.strip():
            messages = [
                {"role": "system", "content": "You are an expert book writer with a vast knowledge of different genres, topics, and writing styles. Your role is to help generate outlines, summaries, and chapters for books on any subject matter, from fiction to non-fiction, from self-help to academic works. Approach each task with professionalism and expertise, tailoring your language and style to suit the specific genre and topic at hand."},
                {"role": "user", "content": f"Based on the following book prompt, outline, pre-summary, and previous chapter content, generate the content for the chapter titled '{chapter_title}': \n\nPrompt: {prompt}\n\nOutline: {outline}\n\nPre-summary: {pre_summary}\n\nPrevious Chapter Content: {previous_chapter_content}\n\nChapter Content:"}
            ]

            response = client.chat.completions.create(
                model="gpt-3.5-turbo-0125",
                messages=messages,
                max_tokens=1024,
                n=1,
                stop=None,
                temperature=0.7
            )

            chapter_content = response.choices[0].message.content
            chapters.append(f"Chapter: {chapter_title}\n\n{chapter_content}")
            previous_chapter_content = chapter_content

    return "\n\n".join(chapters)

def generate_pdf(content):
    url = "https://api.pdfshift.io/v3/convert/pdf"
    headers = {"Content-Type": "application/json"}
    data = {
        "source": content,
        "landscape": False,
        "use_print": False
    }

    response = requests.post(url, auth=("api", pdfshift_api_key), headers=headers, json=data)
    response.raise_for_status()

    return response.content

def app():
    st.title("Book Generation App")

    prompt = st.text_area("Enter the book prompt:", height=200)

    if "outline" not in st.session_state:
        st.session_state.outline = None

    if "pre_summary" not in st.session_state:
        st.session_state.pre_summary = None

    if "full_book" not in st.session_state:
        st.session_state.full_book = None

    if "pdf_content" not in st.session_state:
        st.session_state.pdf_content = None

    if st.button("Generate Outline"):
        with st.spinner("Generating outline..."):
            st.session_state.outline = generate_outline(prompt)
            st.write("Outline:")
            st.write(st.session_state.outline)

    if st.session_state.outline is not None and st.button("Generate Pre-Summary"):
        with st.spinner("Generating pre-summary..."):
            st.session_state.pre_summary = generate_pre_summary(prompt, st.session_state.outline)
            st.write("Pre-Summary:")
            st.write(st.session_state.pre_summary)

    if st.button("Generate Chapters"):
        if st.session_state.outline is None or st.session_state.pre_summary is None:
            st.warning("Please generate an outline and pre-summary first.")
        else:
            with st.spinner("Generating chapters..."):
                st.session_state.full_book = generate_chapters(prompt, st.session_state.outline, st.session_state.pre_summary)
                st.write("Chapters:")
                st.write(st.session_state.full_book)

    if st.session_state.full_book is not None and st.button("Generate PDF"):
        with st.spinner("Generating PDF..."):
            st.session_state.pdf_content = generate_pdf(st.session_state.full_book)
            st.success("PDF generation successful!")

    if st.session_state.pdf_content is not None:
        st.download_button(
            label="Download PDF",
            data=st.session_state.pdf_content,
            file_name="book.pdf",
            mime="application/pdf",
        )

if __name__ == "__main__":
    app()
