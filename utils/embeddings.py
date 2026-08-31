from sentence_transformers import SentenceTransformer


model = SentenceTransformer("all-MiniLM-L6-v2")


def create_embeddings(chunks):
    """
    Convert document chunks or questions into numerical vectors.
    """

    # If chunks contain dictionaries, extract their text
    if chunks and isinstance(chunks[0], dict):
        texts = [chunk["text"] for chunk in chunks]
    else:
        texts = chunks

    embeddings = model.encode(texts)

    return embeddings