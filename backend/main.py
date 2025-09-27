from groq import Groq
import os, pdfplumber, faiss
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from utils import chunking_text, build_faiss_index, retrieve_relevant_text

# Load API key
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

app = FastAPI()

@app.post("/Upload-PDF")
async def upload_pdf(
    file: UploadFile = File(...)
):
    """
    Upload a PDF file, extract its text, chunk it, and store embeddings in a FAISS index.

    Args:
        file (UploadFile): The uploaded PDF file.

    Returns:
        dict: A message indicating success and the number of chunks processed.

    Raises:
        HTTPException (400): If there is an error reading or parsing the PDF.
    """
    try:
        pdf_text = ""
        with pdfplumber.open(file.file) as pdf:
            for page in pdf.pages:              #Looping through each page in the PDF
                page_text = page.extract_text()
                if page_text:
                    pdf_text += page_text + "\n"

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error Reading PDF: {e}")
    
    # Split into chunks
    doc_chunks = chunking_text(text=pdf_text)

    # Build FAISS index
    build_faiss_index(doc_chunks)
    print("Stored Document Embeddings in Faiss.")

chat_history = []

@app.post("/Chatbot")
async def chatbot(
    query: str = Form(...)
) -> str:
    """
    Query the chatbot with a user question. Retrieves relevant PDF chunks
    from FAISS and generates a response using the LLM.

    Args:
        query (str): The user's input query.

    Returns:
        str: The assistant's response.
    """
    # Number of relevant chunks to retrieve from FAISS
    k = 3 # How many relevant search results we want.
    retrieved_chunks = retrieve_relevant_text(query=query, top_k = k)

    system_prompt = f"""
You are a helpful assistant. Use the following PDF context to answer questions if relevant.
If the query is unrelated to the PDF, just chat normally.

Context from PDF:
{retrieved_chunks}
"""

    # Append user query to conversation history
    chat_history.append({"role": "user", "content": query})

    # Send chat history + context to Groq LLM
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            *chat_history
        ],
        temperature=0.5,
        max_tokens=1024,
    )

    output = response.choices[0].message.content
    
    # Append assistant response to conversation history
    chat_history.append({"role": "assistant", "content": output})
    return output
