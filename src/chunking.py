from __future__ import annotations

import math
import re


class FixedSizeChunker:
    """
    Split text into fixed-size chunks with optional overlap.

    Rules:
        - Each chunk is at most chunk_size characters long.
        - Consecutive chunks share overlap characters.
        - The last chunk contains whatever remains.
        - If text is shorter than chunk_size, return [text].
    """

    def __init__(self, chunk_size: int = 500, overlap: int = 50) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        if len(text) <= self.chunk_size:
            return [text]

        step = self.chunk_size - self.overlap
        chunks: list[str] = []
        for start in range(0, len(text), step):
            chunk = text[start : start + self.chunk_size]
            chunks.append(chunk)
            if start + self.chunk_size >= len(text):
                break
        return chunks


class SentenceChunker:
    """
    Split text into chunks of at most max_sentences_per_chunk sentences.

    Sentence detection: split on ". ", "! ", "? " or ".\n".
    Strip extra whitespace from each chunk.
    """

    def __init__(self, max_sentences_per_chunk: int = 3) -> None:
        self.max_sentences_per_chunk = max(1, max_sentences_per_chunk)

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []

        sentences = [
            sentence.strip()
            for sentence in re.split(r"(?<=[.!?])(?:[ \t]+|\r?\n+)", text.strip())
            if sentence.strip()
        ]
        return [
            " ".join(sentences[start : start + self.max_sentences_per_chunk])
            for start in range(0, len(sentences), self.max_sentences_per_chunk)
        ]


class RecursiveChunker:
    """
    Recursively split text using separators in priority order.

    Default separator priority:
        ["\n\n", "\n", ". ", " ", ""]
    """

    DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

    def __init__(self, separators: list[str] | None = None, chunk_size: int = 500) -> None:
        self.separators = self.DEFAULT_SEPARATORS if separators is None else list(separators)
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []
        if self.chunk_size <= 0:
            raise ValueError("chunk_size must be greater than zero")

        return [chunk.strip() for chunk in self._split(text, self.separators) if chunk.strip()]

    def _split(self, current_text: str, remaining_separators: list[str]) -> list[str]:
        if not current_text:
            return []
        if len(current_text) <= self.chunk_size:
            return [current_text]
        if not remaining_separators:
            return [
                current_text[start : start + self.chunk_size]
                for start in range(0, len(current_text), self.chunk_size)
            ]

        separator = remaining_separators[0]
        next_separators = remaining_separators[1:]
        if not separator:
            return [
                current_text[start : start + self.chunk_size]
                for start in range(0, len(current_text), self.chunk_size)
            ]
        if separator not in current_text:
            return self._split(current_text, next_separators)

        raw_parts = current_text.split(separator)
        parts = [
            part + separator if index < len(raw_parts) - 1 else part
            for index, part in enumerate(raw_parts)
            if part or index < len(raw_parts) - 1
        ]

        split_parts: list[str] = []
        for part in parts:
            if len(part) > self.chunk_size:
                split_parts.extend(self._split(part, next_separators))
            else:
                split_parts.append(part)

        chunks: list[str] = []
        current_chunk = ""
        for part in split_parts:
            if current_chunk and len(current_chunk) + len(part) > self.chunk_size:
                chunks.append(current_chunk)
                current_chunk = part
            else:
                current_chunk += part
        if current_chunk:
            chunks.append(current_chunk)
        return chunks


def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def compute_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Compute cosine similarity between two vectors.

    cosine_similarity = dot(a, b) / (||a|| * ||b||)

    Returns 0.0 if either vector has zero magnitude.
    """
    magnitude_a = math.sqrt(_dot(vec_a, vec_a))
    magnitude_b = math.sqrt(_dot(vec_b, vec_b))
    if magnitude_a == 0.0 or magnitude_b == 0.0:
        return 0.0
    return _dot(vec_a, vec_b) / (magnitude_a * magnitude_b)


class ChunkingStrategyComparator:
    """Run all built-in chunking strategies and compare their results."""

    def compare(self, text: str, chunk_size: int = 200) -> dict:
        strategies = {
            "fixed_size": FixedSizeChunker(chunk_size=chunk_size, overlap=0),
            "by_sentences": SentenceChunker(max_sentences_per_chunk=3),
            "recursive": RecursiveChunker(chunk_size=chunk_size),
        }

        comparison = {}
        for name, chunker in strategies.items():
            chunks = chunker.chunk(text)
            comparison[name] = {
                "count": len(chunks),
                "avg_length": sum(map(len, chunks)) / len(chunks) if chunks else 0.0,
                "chunks": chunks,
            }
        return comparison


class HeadingChunker:
    """Split documents by semantic headings, then split oversized sections."""

    HEADING_PREFIXES = (
        "đối tượng",
        "điều kiện",
        "tiêu chuẩn",
        "quy trình",
        "hồ sơ",
        "thời hạn",
        "thời gian",
        "mức học bổng",
        "chính sách",
        "một số nguyên tắc",
        "thủ khoa",
        "hoàn cảnh",
    )

    def __init__(self, chunk_size: int = 1000) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than zero")
        self.chunk_size = chunk_size

    def _is_heading(self, line: str) -> bool:
        stripped = line.strip()
        if not stripped or stripped.startswith(("-", "+", "*")):
            return False
        if re.match(r"^#{1,6}\s+\S", stripped):
            return True

        normalized = stripped.casefold().rstrip(":")
        has_semantic_prefix = normalized.startswith(self.HEADING_PREFIXES)
        return len(stripped) <= 120 and has_semantic_prefix and (
            stripped.endswith(":") or stripped.isupper()
        )

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []

        sections: list[tuple[str, str]] = []
        heading = ""
        body_lines: list[str] = []

        for line in text.splitlines():
            if self._is_heading(line):
                if heading or any(part.strip() for part in body_lines):
                    sections.append((heading, "\n".join(body_lines).strip()))
                heading = line.strip()
                body_lines = []
            else:
                body_lines.append(line)
        if heading or any(part.strip() for part in body_lines):
            sections.append((heading, "\n".join(body_lines).strip()))

        chunks: list[str] = []
        for section_heading, section_body in sections:
            section = "\n\n".join(part for part in (section_heading, section_body) if part)
            if len(section) <= self.chunk_size:
                chunks.append(section)
                continue

            prefix = f"{section_heading}\n\n" if section_heading else ""
            body_limit = max(1, self.chunk_size - len(prefix))
            body_chunks = RecursiveChunker(chunk_size=body_limit).chunk(section_body)
            chunks.extend(f"{prefix}{part}".strip() for part in body_chunks)

        return [chunk for chunk in chunks if chunk]
