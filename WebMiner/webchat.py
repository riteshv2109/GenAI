import streamlit as st
from dotenv import load_dotenv
from langchain_qdrant import QdrantVectorStore
from langchain_openai import OpenAIEmbeddings
from openai import OpenAI
import os


load_dotenv()

# setting page
st.set_page_config(
    page_title="AI Webpage Insight Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS 
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .query-box {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .response-box {
        background-color: rgba(255, 255, 255, 0.8);
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin-top: 20px;
    }
    .stTextInput > div > div > input {
        font-size: 18px;
        padding: 15px;
    }
</style>
""", unsafe_allow_html=True)

# App title and description
st.markdown('<h1 class="main-header">🤖 AI Webpage Insight Assistant</h1>', unsafe_allow_html=True)
st.markdown("""
Welcome to the AI Webpage Insight Assistant! This tool allows you to ask questions about content 
from webpages that have been processed and indexed. Simply type your question below and press Enter 
to get insights from the analyzed web content.
""")


@st.cache_resource
def initialize_models():
    try:
        client = OpenAI()
        embedding_model = OpenAIEmbeddings(model="text-embedding-3-large")
        return client, embedding_model
    except Exception as e:
        st.error(f"Error initializing models: {str(e)}")
        return None, None

client, embedding_model = initialize_models()

# Connect to vector database
@st.cache_resource
def get_vector_db():
    try:
        vector_db = QdrantVectorStore.from_existing_collection(
            url="http://localhost:6333",
            collection_name="splitting webpages",
            embedding=embedding_model
        )
        return vector_db
    except Exception as e:
        st.error(f"Error connecting to vector database: {str(e)}")
        return None

vector_db = get_vector_db()

# Create query input
with st.container():
    st.markdown('<div class="query-box">', unsafe_allow_html=True)
    query = st.text_input(
        "Ask a question about the webpage content:",
        placeholder="Type your question here and press Enter...",
        key="query_input",
        label_visibility="collapsed"
    )
    st.markdown('</div>', unsafe_allow_html=True)

# Process query when user presses Enter
if query:
    with st.spinner("Searching for relevant information..."):
        try:
            # Vector similarity search in database
            search_results = vector_db.similarity_search(query=query)
            
            # Prepare context from search results
            context = "\n\n".join([
                f"Content: {result.page_content}\n"
                f"Source: {result.metadata.get('source', 'Unknown')}"
                for result in search_results
            ])

            
            SYSTEM_PROMPT = f"""
            You are a helpful AI Assistant who answers user queries based on the available context
            retrieved from webpage content. Provide clear, concise answers based only on the context below.

            Context:
            {context}
            
            If the context doesn't contain relevant information, politely state that you cannot answer 
            based on the available information.
            """

            # to get response from openAI
            chat_completion = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": query},
                ],
            )

            
            response = chat_completion.choices[0].message.content
            st.markdown('<div class="response-box">', unsafe_allow_html=True)
            st.markdown(f"**Question:** {query}")
            st.markdown(f"**Answer:** {response}")
            
            # Show sources
            with st.expander("View sources used for this answer"):
                for i, result in enumerate(search_results):
                    st.markdown(f"**Source {i+1}:** {result.metadata.get('source', 'Unknown')}")
                    st.markdown(f"**Content snippet:** {result.page_content[:200]}...")
            
            st.markdown('</div>', unsafe_allow_html=True)

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

# Add sidebar with information
with st.sidebar:
    st.header("About")
    st.markdown("""
    This AI Webpage Insight Assistant uses:
    - **Qdrant** for vector storage and similarity search
    - **OpenAI** for embeddings and response generation
    - **LangChain** for document processing
    
    Questions are answered based on content from webpages that have been previously indexed.
    """)
    
    st.header("How to Use")
    st.markdown("""
    1. Type your question in the input box
    2. Press Enter to submit
    3. View the AI-generated response
    4. Expand the sources section to see where the information came from
    """)