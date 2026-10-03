import streamlit as st
from agent import run_agent

st.set_page_config(page_title="Research Paper Assistant", page_icon="📄")
st.title("📄 Research Paper Assistant")
st.write(
    "Ask a research question. The agent searches arXiv, reads the full papers, "
    "and answers with citations."
)

question = st.text_input("Your question")

if st.button("Ask") and question.strip():
    with st.spinner("Searching papers, reading them, and writing the answer..."):
        try:
            answer = run_agent(question)
            st.markdown(answer)
        except Exception as e:
            st.error(
                "Something went wrong. If the message mentions 429 or quota, "
                "the free API limit was reached; wait a minute and try again."
            )
            st.caption(str(e))