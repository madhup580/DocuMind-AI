from flask import Flask, render_template, request, jsonify
import os

from utils.document_loader import load_pdf, get_page_count
from utils.text_splitter import split_text
from utils.embeddings import create_embeddings
from utils.vector_store import create_vector_store
from utils.rag_pipeline import (
    retrieve_relevant_chunks,
    generate_answer
)


app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# Store processed document information
document_chunks = None
vector_index = None


# --------------------------------------------------
# Home page
# --------------------------------------------------

@app.route("/")
def home():
    return render_template("index.html")


# --------------------------------------------------
# Upload PDF
# --------------------------------------------------

@app.route("/upload", methods=["POST"])
def upload_file():

    global document_chunks
    global vector_index

    if "file" not in request.files:
        return jsonify({
            "error": "No file uploaded"
        }), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({
            "error": "No file selected"
        }), 400

    if not file.filename.lower().endswith(".pdf"):
        return jsonify({
            "error": "Only PDF files are supported"
        }), 400

    file_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        file.filename
    )

    file.save(file_path)

    try:

        # Extract text
        text = load_pdf(file_path)

        # Get number of pages
        page_count = get_page_count(file_path)

        # Split text into chunks
        document_chunks = split_text(text)

        # Create embeddings
        embeddings = create_embeddings(
            document_chunks
        )

        # Create vector index
        vector_index = create_vector_store(
            embeddings
        )

        return jsonify({
        "message": "PDF uploaded and processed successfully!",
        "filename": file.filename,
        "pages": page_count,
        "chunks": len(document_chunks)
    })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# --------------------------------------------------
# Ask question
# --------------------------------------------------

@app.route("/ask", methods=["POST"])
def ask_question():

    global document_chunks
    global vector_index

    # Check whether a document has been uploaded
    if document_chunks is None or vector_index is None:

        return jsonify({
            "error": "Please upload a PDF first."
        }), 400

    data = request.get_json()

    if not data or "question" not in data:

        return jsonify({
            "error": "Please enter a question."
        }), 400

    query = data["question"].strip()

    if not query:

        return jsonify({
            "error": "Please enter a question."
        }), 400

    try:

        # Retrieve relevant document chunks
        relevant_chunks = retrieve_relevant_chunks(
            query,
            document_chunks,
            vector_index,
            top_k=5
        )

        # Generate answer using local Qwen model
        answer = generate_answer(
            query,
            relevant_chunks
        )

        sources = sorted(
            set(
                chunk["page"]
                for chunk in relevant_chunks
                if "page" in chunk
            )
        )

        return jsonify({
            "answer": answer,
            "sources": sources
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# --------------------------------------------------
# Run application
# --------------------------------------------------

if __name__ == "__main__":
    app.run(
        debug=True
    )