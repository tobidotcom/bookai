import streamlit as st
from openai import OpenAI

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
import re
import base64
from fpdf import FPDF


def generate_outline(prompt):
    messages = [
        {"role": "system", "content": "You are an expert book writer with a vast knowledge of different genres, topics, and writing styles. Your role is to help generate outlines, summaries, and chapters for books on any subject matter, from fiction to non-fiction, from self-help to academic works. Approach each task with professionalism and expertise, tailoring your language and style to suit the specific genre and topic at hand."},
        {"role": "user", "content": f"Based on the following book prompt, generate a very concise outline for a short ebook of around 10-15 pages: \n\n{prompt}\n\nOutline:"}
    ]

    response = client.chat.completions.create(model="gpt-3.5-turbo",
    messages=messages,
    max_tokens=256,
    n=1,
    stop=None,
    temperature=0.7)

    outline = response.choices[0].message.content
    return outline

def generate_pre_summary(prompt, outline):
    messages = [
        {"role": "system", "content": "You are an expert book writer with a vast knowledge of different genres, topics, and writing styles. Your role is to help generate outlines, summaries, and chapters for books on any subject matter, from fiction to non-fiction, from self-help to academic works. Approach each task with professionalism and expertise, tailoring your language and style to suit the specific genre and topic at hand."},
        {"role": "user", "content": f"Based on the following book prompt and outline, craft a very concise pre-summary for a short ebook of around 10-15 pages: \n\nPrompt: {prompt}\n\nOutline: {outline}\n\nPre-summary:"}
    ]

    response = client.chat.completions.create(model="gpt-3.5-turbo",
    messages=messages,
    max_tokens=256,
    n=1,
    stop=None,
    temperature=0.7)

    pre_summary = response.choices[0].message.content
    return pre_summary

def generate_chapters(prompt, outline, pre_summary):
    chapters = []
    previous_chapter_content = ""
    chapter_titles = re.split(r'Chapter\s*\d*:\s*', outline)

    for chapter_title in chapter_titles:
        if chapter_title.strip():
            chapter_title = chapter_title.strip()
            messages = [
                {"role": "system", "content": "You are an expert book writer..."},
                {"role": "user", "content": f"Based on the following book prompt, outline, pre-summary, and previous chapter content, generate a very concise chapter for a short ebook of around 10-15 pages titled '{chapter_title}': \n\nPrompt: {prompt}\n\nOutline: {outline}\n\nPre-summary: {pre_summary}\n\nPrevious Chapter Content: {previous_chapter_content}\n\nChapter Content:"}
            ]

            response = client.chat.completions.create(model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=256,
            n=1,
            stop=None,
            temperature=0.7)

            chapter_content = response.choices[0].message.content
            chapters.append(f"Chapter Title: {chapter_title}\n\n{chapter_content}")
            previous_chapter_content = chapter_content

    return "\n\n".join(chapters)

def generate_pdf(file_content, file_name):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for line in file_content.split("\n"):
        pdf.multi_cell(0, 10, txt=line, align="L")
    pdf_file = pdf.output(f"{file_name}.pdf", "S").encode("latin-1")
    b64 = base64.b64encode(pdf_file).decode()
    href = f'<a href="data:application/pdf;base64,{b64}" download="{file_name}.pdf">Download {file_name}.pdf</a>'
    return href

def app():
    st.title("Short Ebook Generation App")

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

    if st.session_state.full_book is not None:
        st.markdown(generate_pdf(st.session_state.full_book, "short_ebook"), unsafe_allow_html=True)

if __name__ == "__main__":
    app()
