from utils.embeddings import create_embeddings
from utils.vector_store import search_vector_store
import os
import requests


# --------------------------------------------------
# 1. Retrieve relevant document chunks
# --------------------------------------------------

def retrieve_relevant_chunks(query, chunks, index, top_k=5):
    """
    Retrieve the most relevant chunks for a query.
    """

    query_embedding = create_embeddings([query])

    distances, indices = search_vector_store(
        index,
        query_embedding,
        top_k=top_k
    )

    relevant_chunks = []

    for i in indices[0]:

        if i < len(chunks):
            relevant_chunks.append(chunks[i])

    return relevant_chunks


# --------------------------------------------------
# 2. Generate answer using Hugging Face
# --------------------------------------------------

def generate_answer(query, relevant_chunks):
    """
    Generate an answer using only the retrieved
    document content.
    """

    if not relevant_chunks:
        return "I couldn't find that information in the uploaded document."

    context = "\n\n".join(
        chunk["text"]
        for chunk in relevant_chunks
    )

    prompt = f"""You answer questions about documents.

Use ONLY the document context provided below.

Rules:
- Do not use outside knowledge.
- Do not repeat the question.
- Do not explain your reasoning.
- Do not invent information.
- Give a clear and concise answer.
- If the answer is not present in the document context, say:
I couldn't find that information in the uploaded document.

DOCUMENT CONTEXT:

{context}

QUESTION:

{query}

ANSWER:
"""

    token = os.environ.get("HF_TOKEN")

    if not token:
        return "Hugging Face token is not configured."

    API_URL = "https://router.huggingface.co/hf-inference/models/HuggingFaceTB/SmolLM2-135M-Instruct"

    headers = {
        "Authorization": f"Bearer {token}"
    }

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 100,
            "return_full_text": False
        }
    }

    response = requests.post(
        API_URL,
        headers=headers,
        json=payload,
        timeout=120
    )

    if response.status_code != 200:
        return f"Model request failed: {response.text}"

    result = response.json()

    if isinstance(result, list) and len(result) > 0:
        return result[0].get(
            "generated_text",
            "I couldn't generate an answer."
        ).strip()

    return "I couldn't generate an answer."
