import os
import json
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
from tqdm import tqdm
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from PyPDF2 import PdfReader

load_dotenv()

def extract_text_from_pdf(file_path):
    """
    Extracts text from a PDF file.
    
    Args:
        file_path (str): Path to the PDF file.
    
    Returns:
        str: Extracted text content.
    """
    reader = PdfReader(file_path)
    text = []
    for page in reader.pages:
        text.append(page.extract_text())
    return "\n".join(text)

def load_chunks_from_pdf(file_path):
    """
    Loads data from a PDF file, processes it into smaller, meaningful chunks.
    """
    embeddings = OpenAIEmbeddings(
        model='text-embedding-ada-002'
    )
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    
    text_data = extract_text_from_pdf(file_path)
    chunks = text_splitter.split_text(text_data)
    
    vectorstore = Chroma(
        persist_directory="./nadraDB",
        embedding_function=embeddings,
        collection_name="nadra"
    )
    
    vectorstore.add_texts(chunks)

if not os.path.exists("./nadraDB"):
    print("Loading data into the vector store...")
    load_chunks_from_pdf("Nadra_Document.pdf")
else:
    print("Vector store already exists. Skipping data loading.")

def retrieve_response():
    """
    Retrieves the most relevant stored messages based on the query.
    """
    embeddings = OpenAIEmbeddings(
        model='text-embedding-ada-002'
    )
    
    vectorstore = Chroma(
        persist_directory="./nadraDB",
        embedding_function=embeddings,
        collection_name="nadra"
    )
    
    return vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={
            "k": 3
        }
    )

def format_docs(docs):
    """
    Formats the retrieved documents into a single string.
    """
    return "\n\n".join(doc.page_content for doc in docs)

# Updated prompt template with formatting instructions
prompt = ChatPromptTemplate.from_template("""
You are a NADRA (National Database and Registration Authority) Virtual Assistant, designed to help users with their NADRA-related queries and documentation requirements. Structure your responses in a clear, organized format following these guidelines:

1. Start with a warm greeting and acknowledge the query.

2. Format your response using appropriate Markdown:
   - Use # for main headings
   - Use ## for subheadings
   - Use bullet points (*) for lists
   - Use numbered lists (1., 2., etc.) for sequential steps
   - Use bold (**text**) for important information
   - Use horizontal rules (---) to separate major sections if needed

3. Common sections to include when relevant:
   - Overview/Summary
   - Required Documents
   - Process Steps
   - Timeline
   - Fees
   - Additional Information
   - Contact Information

Context from NADRA documentation: {data}

User Query: {query}

Remember to:
- Keep the formatting consistent
- Make information easy to scan
- Highlight crucial details
- Include relevant timelines and fees
- End with an offer for further assistance

If unsure about specific details, acknowledge this and recommend visiting the nearest NADRA office or official website for the most up-to-date information.
""")

# Initialize retriever
retriever = retrieve_response()

# Configure the chain with improved settings
chain = (
    {
        "data": retriever | format_docs,
        "query": RunnablePassthrough()
    }
    | prompt 
    | ChatOpenAI(
        model='gpt-4o-mini',
        temperature=0.7,
        max_tokens=2000
    )
    | StrOutputParser()
)