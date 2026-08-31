import os
import numpy as np
from huggingface_hub import InferenceClient


client = InferenceClient(
    provider="hf-inference",
    api_key=os.getenv("HF_TOKEN")
)


def create_embeddings(chunks):
    """
    Convert document chunks or questions into numerical vectors
    using Hugging Face hosted inference.
    """

    if chunks and isinstance(chunks[0], dict):
        texts = [chunk["text"] for chunk in chunks]
    else:
        texts = chunks

    if not texts:
        return np.array([])

    embeddings = client.feature_extraction(
        texts,
        model="sentence-transformers/all-MiniLM-L6-v2"
    )

    return np.asarray(embeddings)
