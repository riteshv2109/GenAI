import os
from pydoc import splitdoc
from dotenv import load_dotenv

'''USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
REQUEST_TIMEOUT=30
REQUEST_DELAY=1'''
load_dotenv()
USER_AGENT = os.getenv("USER_AGENT")
from pathlib import Path
from langchain_core.documents import Document
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from openai import OpenAI


client = OpenAI()


loader = WebBaseLoader(
    web_paths=["https://python.langchain.com/docs/tutorials/rag/"],
    requests_kwargs={
        "headers": {"User-Agent": USER_AGENT}
    }
)
docs = loader.load()

# Step 2: Split documents
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=400
)
split_docs = text_splitter.split_documents(docs)

# Step 3: Add metadata (page_number + source)
split_docs_with_metadata = [
    Document(
        page_content=doc.page_content,
        metadata={
            "source": doc.metadata.get("source", "https://python.langchain.com/docs/tutorials/rag/"),
            "page_number": i + 1
        }
    )
    for i, doc in enumerate(split_docs)
]

# Step 4: Create embeddings + Qdrant store
embedding_model = OpenAIEmbeddings(model="text-embedding-3-large")

vector_store = QdrantVectorStore.from_documents(
    documents=split_docs_with_metadata,
    url="http://localhost:6333",
    collection_name="splitting_webpages",
    embedding=embedding_model
)

print("Indexing of webpage is done...👍")