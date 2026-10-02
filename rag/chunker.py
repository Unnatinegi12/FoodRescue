from typing import Optional

from rag import config


# Prefer cutting at natural boundaries.
_BREAKS = ["\n\n", "\n", ". ", " "]


def _find_cut(text: str, start: int, end: int) -> int:
    """Find a natural place to cut the chunk."""
    earliest = start + (end - start) // 2

    for separator in _BREAKS:
        index = text.rfind(
            separator,
            earliest,
            end
        )

        if index != -1:
            return index + len(separator)

    return end


def chunk_text(
    text: str,
    chunk_size: Optional[int] = None,
    overlap: Optional[int] = None
) -> list:

    size = (
        config.CHUNK_SIZE
        if chunk_size is None
        else chunk_size
    )

    overlap = (
        config.CHUNK_OVERLAP
        if overlap is None
        else overlap
    )

    if size <= 0 or overlap < 0 or overlap >= size:
        raise ValueError(
            "need chunk_size > 0 and 0 <= overlap < chunk_size"
        )

    text = text.strip()
    chunks = []

    start = 0

    while start < len(text):

        end = min(
            start + size,
            len(text)
        )

        if end < len(text):
            end = _find_cut(
                text,
                start,
                end
            )

        piece = text[start:end].strip()

        if piece:
            chunks.append(piece)

        if end >= len(text):
            break

        # Start the next chunk slightly before
        # the previous chunk ended.
        next_start = max(
            end - overlap,
            start + 1
        )

        # Move to the beginning of a word.
        while (
            next_start < end
            and not text[next_start - 1].isspace()
        ):
            next_start += 1

        start = next_start

    return chunks


def chunk_documents(documents: list) -> list:
    """
    Split every document into chunks while
    preserving its metadata.
    """

    chunks = []

    for doc in documents:

        for index, piece in enumerate(
            chunk_text(doc["text"])
        ):
            chunks.append(
                {
                    "id": f"{doc['document_name']}-{index:03d}",
                    "text": piece,
                    "source": doc["source"],
                    "topic": doc["topic"],
                    "document_name": doc["document_name"],
                    "chunk_index": index,
                }
            )

    return chunks