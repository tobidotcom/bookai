import streamlit as st
from openai import OpenAI
import base64

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def generate_outline(prompt):
    messages = [
        {"role": "system", "content": "You are an expert book writer with a vast knowledge of different genres, topics, and writing styles. Your role is to help generate outlines, summaries, and chapters for books on any subject matter, from fiction to non-fiction, from self-help to academic works. Approach each task with professionalism and expertise, tailoring your language and style to suit the specific genre and topic at hand."},
        {"role": "user", "content": f"Based on the following book prompt, generate a comprehensive outline for the book: \n\n{prompt}\n\nOutline:"}
    ]

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.7
    )

    outline = response.choices[0].message.content.strip()
    return outline

def generate_pre_summary(prompt, outline):
    messages = [
        {"role": "system", "content": "You are an expert book writer with a vast knowledge of different genres, topics, and writing styles. Your role is to help generate outlines, summaries, and chapters for books on any subject matter, from fiction to non-fiction, from self-help to academic works. Approach each task with professionalism and expertise, tailoring your language and style to suit the specific genre and topic at hand."},
        {"role": "user", "content": f"Based on the following book prompt and outline, craft a compelling pre-summary for the book: \n\nPrompt: {prompt}\n\nOutline: {outline}\n\nPre-summary:"}
    ]

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.7
    )

    pre_summary = response.choices[0].message.content.strip()
    return pre_summary

# ... (rest of the code remains the same) ...

def main():
    st.title("Book Generation App")

    prompt = st.text_area("Enter the book prompt:", height=200)

    outline = None
    pre_summary = None
    full_book = None

    if st.button("Generate Outline"):
        outline = generate_outline(prompt)
        st.write("Outline:")
        st.write(outline)

    if st.button("Generate Pre-Summary", disabled=outline is None):
        pre_summary = generate_pre_summary(prompt, outline)
        st.write("Pre-Summary:")
        st.write(pre_summary)

    # ... (rest of the code remains the same) ...

if __name__ == "__main__":
    main()
