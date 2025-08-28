from dotenv import load_dotenv
from pathlib import Path
# pathlib is used for pdf path
from langchain_community.document_loaders import PyPDFLoader
# used to read PDF
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore 


load_dotenv()

pdf_path = Path(__file__).parent/"dsa.pdf"
# means the file's parent i.e. RAG has dsa.pdf
loader = PyPDFLoader(file_path= pdf_path)

# LOADING
docs = loader.load()  
# read the file ,loads page by page

# CHUNKING
text_splitter = RecursiveCharacterTextSplitter(
     chunk_size = 1000,
     chunk_overlap = 400
    #  chunk overlap is used to get some previous datainto new chunk such as rit|esh in separate 
    # chunk so to get ritesh in a single chunk chunk_overlapis used     
)

split_docs = text_splitter.split_documents(documents=docs) 

# VECTOR EMBEDDINGS
embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-large"
)
# using embedding_model create embeddings of split_docs and store in database

vector_store = QdrantVectorStore.from_documents(
    documents = split_docs,
    url = "http://localhost:6333",
    collection_name = "dsa_try",
    embedding = embedding_model
)
print("indexing of documents done...")