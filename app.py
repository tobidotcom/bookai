import streamlit as st
import openai

# Set up OpenAI API key
openai.api_key = st.secrets["OPENAI_API_KEY"]

def generate_outline(prompt):
    messages = [
        {"role": "system", "content": "You are an expert book writer with a vast knowledge of different genres, topics, and writing styles. Your role is to help generate outlines, summaries, and chapters for books on any subject matter, from fiction to non-fiction, from self-help to academic works. Approach each task with professionalism and expertise, tailoring your language and style to suit the specific genre and topic at hand."},
        {"role": "user", "content": f"Based on the following book prompt, generate a comprehensive outline for the book: \n\n{prompt}\n\nOutline:"}
    ]
    
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.7,
    )

    outline = response.choices[0].message.content.strip()
    return outline

def generate_pre_summary(prompt, outline):
    messages = [
        {"role": "system", "content": "You are an expert book writer with a vast knowledge of different genres, topics, and writing styles. Your role is to help generate outlines, summaries, and chapters for books on any subject matter, from fiction to non-fiction, from self-help to academic works. Approach each task with professionalism and expertise, tailoring your language and style to suit the specific genre and topic at hand."},
        {"role": "user", "content": f"Based on the following book prompt and outline, craft a compelling pre-summary for the book: \n\nPrompt: {prompt}\n\nOutline: {outline}\n\nPre-summary:"}
    ]
    
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.7,
    )

    pre_summary = response.choices[0].message.content.strip()
    return pre_summary

def check_pre_summary(pre_summary):
    messages = [
        {"role": "system", "content": "You are an expert book writer with a vast knowledge of different genres, topics, and writing styles. Your role is to help generate outlines, summaries, and chapters for books on any subject matter, from fiction to non-fiction, from self-help to academic works. Approach each task with professionalism and expertise, tailoring your language and style to suit the specific genre and topic at hand."},
        {"role": "user", "content": f"Evaluate the following pre-summary for a book and provide feedback on its quality, coherence, and potential improvements: \n\n{pre_summary}"}
    ]
    
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.7,
    )

    feedback = response.choices[0].message.content.strip()
    return feedback

def generate_chapters(prompt, outline, pre_summary):
    chapters = []
    previous_chapter_content = ""
    for chapter_title in outline.split("\n"):
        if chapter_title.strip():
            chapter_content = ""
            while len(chapter_content) < 1000:  # Adjust the desired minimum length
                messages = [
                    {"role": "system", "content": "You are an expert book writer with a vast knowledge of different genres, topics, and writing styles. Your role is to help generate outlines, summaries, and chapters for books on any subject matter, from fiction to non-fiction, from self-help to academic works. Approach each task with professionalism and expertise, tailoring your language and style to suit the specific genre and topic at hand."},
                    {"role": "user", "content": f"Based on the following book prompt, outline, pre-summary, and previous chapter content, generate the content for the chapter titled '{chapter_title}': \n\nPrompt: {prompt}\n\nOutline: {outline}\n\nPre-summary: {pre_summary}\n\nPrevious Chapter Content: {previous_chapter_content}\n\nChapter Content: {chapter_content}"}
                ]
                
                response = openai.ChatCompletion.create(
                    model="gpt-4o",
                    messages=messages,
                    max_tokens=1024,
                    n=1,
                    stop=None,
                    temperature=0.7,
                )
                
                chapter_content += response.choices[0].message.content.strip()

            chapters.append(f"Chapter: {chapter_title}\n\n{chapter_content}")
            previous_chapter_content = chapter_content

    return "\n\n".join(chapters)

def main():
    st.title("Book Generation App")

    prompt = st.text_area("Enter the book prompt:", height=200)

    if st.button("Generate Outline"):
        outline = generate_outline(prompt)
        st.write("Outline:")
        st.write(outline)

    if st.button("Generate Pre-Summary"):
        pre_summary = generate_pre_summary(prompt, outline)
        st.write("Pre-Summary:")
        st.write(pre_summary)

    if st.button("Check Pre-Summary"):
        feedback = check_pre_summary(pre_summary)
        st.write("Feedback on Pre-Summary:")
        st.write(feedback)

    if st.button("Generate Chapters"):
        chapters = generate_chapters(prompt, outline, pre_summary)
        st.write("Chapters:")
        st.write(chapters)

if __name__ == "__main__":
    main()
