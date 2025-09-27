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

    # Search in FAISS
    k = 3 # How many relevant search results we want.
    retrieved_chunks = retrieve_relevant_text(query=query, top_k = k)

    system_prompt = f"""
You are a helpful assistant. Use the following PDF context to answer questions if relevant.
If the query is unrelated to the PDF, just chat normally.

Context from PDF:
{retrieved_chunks}
"""

    # Append to chat history
    chat_history.append({"role": "user", "content": query})

    # Send to Groq
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
    chat_history.append({"role": "assistant", "content": output})
    return output
