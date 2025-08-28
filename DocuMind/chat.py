import streamlit as st
from dotenv import load_dotenv
from langchain_qdrant import QdrantVectorStore
from langchain_openai import OpenAIEmbeddings
from openai import OpenAI


load_dotenv()


client = OpenAI()

embedding_model = OpenAIEmbeddings(model="text-embedding-3-large")

# Connecting to Qdrant DB
vector_db = QdrantVectorStore.from_existing_collection(
    url="http://localhost:6333",
    collection_name="dsa_try",
    embedding=embedding_model
)

# Streamlit UI
st.set_page_config(page_title="DocuQuery AI", layout="centered")
st.title("🤖 DocuQuery AI")

# Input box
query = st.text_input("🔍 Ask your question:")

if st.button("Submit") and query.strip():
    # Search from vector DB
    search_results = vector_db.similarity_search(query=query)

    # Create context from retrieved results
    context = "\n\n".join([
        f"📄 **Page Content:** {result.page_content}\n"
        f"📑 **Page Number:** {result.metadata['page_label']}\n"
        f"📂 **File Location:** {result.metadata['source']}"
        for result in search_results
    ])

    SYSTEM_PROMPT = f"""
    You are a helpful AI Assistant who answers user queries based on the available context
    retrieved from a PDF file along with page_contents and page numbers.

    You should only answer the user based on the following context and guide them
    to the right page number if they want to know more.

    Context:
    {context}
    """

    # Get AI answer
    chat_completion = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": query},
        ],
    )

    answer = chat_completion.choices[0].message.content

    # Display answer
    st.subheader("🤖 Recommended Answer")
    st.markdown(f"""
    <div style="background-color:transparent; padding:15px; border-radius:10px; border:1px solid #ddd;">
        {answer}
    </div>
    """, unsafe_allow_html=True)
