import re
from pathlib import Path
from typing import Optional

from rag import config


SUPPORTED_EXTENSIONS = {".md", ".txt"}

DEFAULT_SOURCE = (
    "FoodRescue project knowledge base "
    "(student-written summary, not an official regulation)"
)


def clean_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = "\n".join(line.rstrip() for line in text.split("\n"))
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def parse_front_matter(text: str) -> tuple:
    """
    Read optional metadata at the top of a document.

    Example:

    ---
    source: FoodRescue knowledge base
    topic: cooked food safety
    ---
    """

    lines = text.split("\n")

    if not lines or lines[0].strip() != "---":
        return {}, text

    for end in range(1, len(lines)):
        if lines[end].strip() == "---":
            metadata = {}

            for line in lines[1:end]:
                if ":" in line:
                    key, value = line.split(":", 1)
                    metadata[key.strip().lower()] = value.strip()

            return metadata, "\n".join(lines[end + 1:])

    return {}, text


def load_documents(data_dir: Optional[Path] = None) -> list:
    """
    Load all Markdown/text documents from the RAG data directory.
    """

    folder = Path(data_dir) if data_dir else config.DATA_DIR

    if not folder.is_dir():
        raise FileNotFoundError(
            f"Knowledge-base folder not found: {folder}"
        )

    documents = []

    for path in sorted(folder.iterdir()):

        if not path.is_file():
            continue

        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        raw = path.read_text(
            encoding="utf-8-sig"
        )

        metadata, body = parse_front_matter(
            clean_text(raw)
        )

        text = clean_text(body)

        if not text:
            continue

        documents.append(
            {
                "text": text,
                "source": metadata.get(
                    "source",
                    DEFAULT_SOURCE
                ),
                "topic": metadata.get(
                    "topic",
                    path.stem.replace("_", " ")
                ),
                "document_name": path.stem,
            }
        )

    return documents