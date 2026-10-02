from rag import config


_model = None
_model_name = None


def get_model():
    """Load the embedding model once and reuse it."""

    global _model, _model_name

    if (
        _model is None
        or _model_name != config.EMBEDDING_MODEL
    ):
        from sentence_transformers import SentenceTransformer

        _model = SentenceTransformer(
            config.EMBEDDING_MODEL
        )

        _model_name = config.EMBEDDING_MODEL

    return _model


def embed_texts(texts: list) -> list:
    """
    Convert a list of text strings into embedding vectors.
    """

    if not texts:
        return []

    vectors = get_model().encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=False
    )

    return vectors.tolist()


def embed_query(query: str) -> list:
    """Convert one query into an embedding vector."""

    return embed_texts([query])[0]