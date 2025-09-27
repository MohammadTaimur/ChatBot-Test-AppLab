## 📄🧠 PDF Chatbot
Chat with your PDF using FastAPI (backend), FAISS (retrieval), Groq LLM (chat), and a Streamlit frontend.
Upload any PDF, the system will:
- Extract text from it.
- Split it into chunks.
- Build FAISS embeddings index.
- Let you ask questions conversationally, with responses grounded in your document.

## 🚀 Features
- PDF upload + parsing (via pdfplumber)
- Chunking & embeddings (langchain, sentence-transformers)
- Vector search with FAISS
- Chat with Groq LLM (mixtral-8x7b)
- Conversational memory
- Streamlit UI
- Dockerized (single container running backend + frontend)

## 📦 Tech Stack
- Backend: FastAPI + Uvicorn
- Frontend: Streamlit
- Vector DB: FAISS
- LLM API: Groq
- PDF Parsing: pdfplumber
- Embeddings: Sentence Transformers

## Folder Structure:
```
├── backend/
│   ├── main.py
│   └── utils.py
├── frontend/
│   └── streamlit_app.py
├── requirements.txt
├── Dockerfile
└── .env        👈 NOT included in repo (you must create this)
```
## Step by Step Setup:

### Clone the repository
```
   git clone https://github.com/MohammadTaimur/ChatBot-Test.git
   cd Chatbot-Test
```
### Create a Virtual Environment and Install the dependencies
```
python -m venv venv
source venv/bin/activate   # on mac/linux
venv\Scripts\activate      # on windows

#If you don't wish to create a virtual environment(not recommended), you may simply run the following line:
pip install -r requirements.txt
```
### Create .env
Create a file named .env in the project root and add the following line with your own api key:
```
   GROQ_API_KEY=your_groq_api_key_here
```
### Run Backend: Open a terminal and run this code
```
uvicorn backend.main:app --reload --port 8000
```
> Runs on 👉 http://127.0.0.1:8000
### Run FrontEnd: Open another terminal and run this code
```
streamlit run frontend/streamlit_app.py --server.port=8501
```
> Runs on 👉 http://127.0.0.1:8501

## 🐳 Run with Docker

### Build image
```
docker build -t pdf-chatbot .
```
### Run container with .env
```
docker run -p 8000:8000 -p 8501:8501 --env-file .env yourdockername
```
> Backend 👉 http://localhost:8000

> Frontend 👉 http://localhost:8501

## Usage
- Open Streamlit UI (http://localhost:8501). Make sure the FastAPI backend is also running
- Upload a PDF.
- Ask questions in the chat box.
- Get contextual answers from your PDF.