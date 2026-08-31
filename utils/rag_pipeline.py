from utils.embeddings import create_embeddings
from utils.vector_store import search_vector_store
from transformers import pipeline


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
# 2. Load local LLM only when needed
# --------------------------------------------------

generator = None


def get_generator():
    global generator

    if generator is None:
        generator = pipeline(
            "text-generation",
            model="HuggingFaceTB/SmolLM2-135M-Instruct"
        )

    return generator


# --------------------------------------------------
# 3. Generate answer
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

    prompt = f"""<|im_start|>system
You answer questions about documents.

Use ONLY the document context provided below.

Rules:
- Do not use outside knowledge.
- Do not repeat the question.
- Do not explain your reasoning.
- Do not invent information.
- Give a clear and concise answer.
- If the answer is not present in the document context, say exactly:
I couldn't find that information in the uploaded document.
<|im_end|>

<|im_start|>user
DOCUMENT CONTEXT:

{context}

QUESTION:

{query}
<|im_end|>

<|im_start|>assistant
"""

    result = get_generator()(
        prompt,
        max_new_tokens=100,
        do_sample=False,
        return_full_text=False
    )

    answer = result[0]["generated_text"].strip()

    return answer
