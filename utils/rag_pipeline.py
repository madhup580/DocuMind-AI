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
# 2. Generate answer using Hugging Face API
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
- If the answer is not present in the document context, say exactly:
I couldn't find that information in the uploaded document.

DOCUMENT CONTEXT:

{context}

QUESTION:

{query}
"""

    # Get Hugging Face API token
    hf_token = os.getenv("HF_TOKEN")

    if not hf_token:
        return "Hugging Face API token is not configured."

    # Hugging Face hosted model
    model = "Qwen/Qwen2.5-0.5B-Instruct"

    url = "https://router.huggingface.co/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {hf_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "Answer questions using only the provided document context."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 100,
        "temperature": 0.1
    }

    try:

        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=60
        )

        response.raise_for_status()

        result = response.json()

        answer = result["choices"][0]["message"]["content"].strip()

        return answer

    except Exception as e:

        print("Hugging Face API error:", e)

        return "Unable to generate an answer right now."
