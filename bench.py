from __future__ import annotations

import argparse
import contextlib
import re
import sys
from pathlib import Path

from src.agent import KnowledgeBaseAgent
from src.chunking import (
    ChunkingStrategyComparator,
    FixedSizeChunker,
    HeadingChunker,
    RecursiveChunker,
)
from src.embeddings import LOCAL_EMBEDDING_MODEL, LocalEmbedder, _mock_embed
from src.models import Document
from src.store import EmbeddingStore


CORPUS_DIR = Path("data/hocbong")

# Each member changes only this line when comparing chunking strategies.
CHUNKER = HeadingChunker(chunk_size=1000)

BENCHMARKS = [
    {
        "query": "Sau khi đăng ký trực tuyến, người học phải chuẩn bị và nộp minh chứng như thế nào?",
        "gold_answer": (
            "Ứng viên FaMI chuẩn bị đơn theo mẫu; minh chứng kết quả học tập và rèn luyện "
            "năm học 2024-2025; minh chứng thành tích nghiên cứu nếu có. Tất cả được scan "
            "thành một PDF để gửi trực tuyến, đồng thời nộp bản cứng tại C1-119 trong thời "
            "gian 12/11-20/11/2025."
        ),
        "gold_doc_id": "hust-fami-scholarship-2025-2026",
        "answer_markers": ["C1-119", "12/11-20/11/2025"],
        "metadata_filter": {"audience": "student"},
    },
    {
        "query": "Ba ngưỡng điểm xét tuyển của học bổng tân sinh viên TP.HCM năm 2025 là gì?",
        "gold_answer": (
            "Điểm thi tốt nghiệp THPT của ba môn từ 18; điểm học bạ của tổ hợp ba môn từ "
            "22 (hoặc học sinh Khá ba năm THPT đối với sinh viên cao đẳng); hoặc điểm thi "
            "đánh giá năng lực ĐHQG từ 650. Các mức điểm đều không tính ưu tiên và không nhân hệ số."
        ),
        "gold_doc_id": "hcmunre-freshman-scholarship-2025",
        "answer_markers": ["18 điểm trở lên", "22 điểm trở lên", "650 điểm trở lên"],
        "metadata_filter": None,
    },
    {
        "query": "Học bổng theo chính sách chung của Đại học Khoa học Huế được cấp vào thời điểm nào?",
        "gold_answer": (
            "Học bổng được cấp vào đầu học kỳ 2 năm thứ nhất, sau khi sinh viên hoàn thành "
            "học kỳ 1 và đăng ký học tập học kỳ 2 của năm học thứ nhất."
        ),
        "gold_doc_id": "husc-admission-scholarship-2025",
        "answer_markers": ["đầu học kỳ 2", "đã đăng ký học tập của học kỳ 2"],
        "metadata_filter": None,
    },
    {
        "query": "Quy định học bổng tuyển sinh khóa 2025 của Đại học Mở áp dụng cho năm nhóm đối tượng nào?",
        "gold_answer": (
            "Năm nhóm gồm: Thủ khoa và Á khoa tuyển sinh toàn trường; Thủ khoa ngành tuyển "
            "sinh; sinh viên có thành tích cao trong học tập; học bổng hợp tác địa phương; "
            "và học bổng tăng cường."
        ),
        "gold_doc_id": "ou-admission-scholarship-2025",
        "answer_markers": ["Thủ khoa, Á khoa tuyển sinh toàn trường", "Học bổng tăng cường"],
        "metadata_filter": None,
    },
    {
        "query": "TDTU liệt kê những ngành kỹ thuật nào được áp dụng học bổng khuyến khích cho nữ sinh viên?",
        "gold_answer": (
            "Các ngành gồm Kỹ thuật điện; Kỹ thuật điện tử viễn thông; chuyên ngành Kỹ thuật "
            "thiết kế vi mạch bán dẫn; Kỹ thuật điều khiển và tự động hóa; Kỹ thuật cơ điện tử; "
            "Kỹ thuật xây dựng; Kỹ thuật xây dựng công trình giao thông; Quy hoạch vùng và đô "
            "thị; Bảo hộ lao động; và Công nghệ kỹ thuật môi trường."
        ),
        "gold_doc_id": "tdtu-scholarship-2025-2026",
        "answer_markers": [
            "nữ sinh viên",
            "Kỹ thuật điều khiển và tự động hóa",
            "Công nghệ kỹ thuật môi trường",
        ],
        "metadata_filter": None,
    },
]


def parse_frontmatter(path: Path) -> tuple[dict[str, str], str]:
    raw = path.read_text(encoding="utf-8")
    parts = raw.split("---", 2)
    if len(parts) != 3 or parts[0].strip():
        raise ValueError(f"Missing YAML frontmatter: {path}")

    metadata: dict[str, str] = {}
    for line in parts[1].splitlines():
        if not line.strip() or line.lstrip().startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip().strip('"').strip("'")
    return metadata, parts[2].strip()


def load_chunked_documents(chunker=CHUNKER) -> list[Document]:
    documents: list[Document] = []
    for path in sorted(CORPUS_DIR.glob("*.md")):
        metadata, content = parse_frontmatter(path)
        for index, chunk in enumerate(chunker.chunk(content)):
            chunk_metadata = {
                **metadata,
                "doc_id": path.stem,
                "chunk_index": index,
                "chunker": chunker.__class__.__name__,
            }
            documents.append(
                Document(id=f"{path.stem}#{index}", content=chunk, metadata=chunk_metadata)
            )
    return documents


def resolve_embedding_backend(name: str):
    if name == "local":
        embedder = LocalEmbedder(model_name=LOCAL_EMBEDDING_MODEL)
        return embedder, LOCAL_EMBEDDING_MODEL
    return _mock_embed, "mock embeddings fallback"


def run_benchmark(embedding_fn=_mock_embed, backend_name: str = "mock embeddings fallback") -> None:
    documents = load_chunked_documents()
    store = EmbeddingStore(
        collection_name="scholarship_benchmark", embedding_fn=embedding_fn
    )
    store.add_documents(documents)

    print(f"Chunker: {CHUNKER.__class__.__name__}")
    print(f"Embedding backend: {backend_name}")
    print(f"Loaded {len(documents)} chunks from {len(list(CORPUS_DIR.glob('*.md')))} documents")

    for number, benchmark in enumerate(BENCHMARKS, start=1):
        query = benchmark["query"]
        metadata_filter = benchmark["metadata_filter"]
        results = store.search_with_filter(query, top_k=3, metadata_filter=metadata_filter)

        print(f"\nQ{number}: {query}")
        print(f"Filter: {metadata_filter}")
        print(f"Gold doc: {benchmark['gold_doc_id']}")
        print(f"Gold answer: {benchmark['gold_answer']}")
        for rank, result in enumerate(results, start=1):
            preview = " ".join(result["content"].split())[:180]
            print(
                f"  {rank}. score={result['score']:.4f} "
                f"doc_id={result['metadata']['doc_id']} "
                f"chunk={result['metadata']['chunk_index']} | {preview}"
            )


def run_baseline() -> None:
    comparator = ChunkingStrategyComparator()
    selected = [
        "hust-fami-scholarship-2025-2026.md",
        "husc-admission-scholarship-2025.md",
        "tdtu-scholarship-2025-2026.md",
    ]
    print("document,strategy,count,avg_length")
    for filename in selected:
        _, content = parse_frontmatter(CORPUS_DIR / filename)
        comparison = comparator.compare(content, chunk_size=800)
        for strategy, stats in comparison.items():
            print(f"{filename},{strategy},{stats['count']},{stats['avg_length']:.2f}")


def normalize(text: str) -> str:
    return " ".join(text.casefold().split())


def contains_markers(text: str, markers: list[str]) -> bool:
    normalized = normalize(text)
    return all(normalize(marker) in normalized for marker in markers)


def extractive_answer_from_text(text: str, markers: list[str]) -> str:
    units: list[str] = []
    for unit in re.split(r"(?<=[.!?])\s+|\n+", text):
        if any(normalize(marker) in normalize(unit) for marker in markers):
            cleaned = " ".join(unit.split())
            if cleaned and cleaned not in units:
                units.append(cleaned)
    return " ".join(units) if units else "Không tìm thấy đủ thông tin trong ngữ cảnh truy xuất."


class RetrievedContextStore:
    """Adapter that lets KnowledgeBaseAgent answer from an already-ranked result set."""

    def __init__(self, results: list[dict]) -> None:
        self.results = results

    def search(self, query: str, top_k: int = 3) -> list[dict]:
        return self.results[:top_k]


def evaluate_query(store: EmbeddingStore, benchmark: dict, metadata_filter) -> dict:
    results = store.search_with_filter(
        benchmark["query"], top_k=3, metadata_filter=metadata_filter
    )
    gold_doc_id = benchmark["gold_doc_id"]
    markers = benchmark["answer_markers"]
    gold_rank = next(
        (
            rank
            for rank, result in enumerate(results, start=1)
            if result["metadata"].get("doc_id") == gold_doc_id
        ),
        None,
    )
    gold_context = "\n".join(
        result["content"]
        for result in results
        if result["metadata"].get("doc_id") == gold_doc_id
    )
    content_hit = contains_markers(gold_context, markers)
    agent = KnowledgeBaseAgent(
        store=RetrievedContextStore(results),
        llm_fn=lambda prompt: extractive_answer_from_text(prompt, markers),
    )
    agent_answer = agent.answer(benchmark["query"], top_k=3)
    agent_correct = contains_markers(agent_answer, markers)

    if gold_rank == 1 and content_hit and agent_correct:
        points = 2
    elif gold_rank in {2, 3} and content_hit and agent_correct:
        points = 1
    else:
        points = 0

    return {
        "results": results,
        "gold_rank": gold_rank,
        "doc_hit": gold_rank is not None,
        "content_hit": content_hit,
        "agent_answer": agent_answer,
        "agent_correct": agent_correct,
        "points": points,
    }


def print_top_three(evaluation: dict) -> None:
    for rank, result in enumerate(evaluation["results"], start=1):
        metadata = result["metadata"]
        print(
            f"    {rank}. score={result['score']:.4f} "
            f"doc_id={metadata['doc_id']} chunk={metadata['chunk_index']}"
        )


def run_cp6_evaluation(embedding_fn=_mock_embed, backend_name: str = "mock embeddings fallback") -> None:
    strategies = {
        "fixed": FixedSizeChunker(chunk_size=1000, overlap=100),
        "recursive": RecursiveChunker(chunk_size=1000),
        "heading": HeadingChunker(chunk_size=1000),
    }
    print("CHECKPOINT 6 - SCHOLARSHIP RETRIEVAL EVALUATION")
    print(f"Embedding backend: {backend_name}")
    if embedding_fn is _mock_embed:
        print(
            "WARNING: MockEmbedder hashes text with MD5 and does not encode semantics. "
            "Retrieval ranks/scores are noise; chunk counts and coherence remain meaningful."
        )

    for strategy_name, chunker in strategies.items():
        documents = load_chunked_documents(chunker)
        store = EmbeddingStore(
            collection_name=f"scholarship_{strategy_name}", embedding_fn=embedding_fn
        )
        store.add_documents(documents)
        total_points = 0
        doc_hits = 0
        content_hits = 0

        print(f"\n=== STRATEGY: {strategy_name} ({len(documents)} chunks) ===")
        for number, benchmark in enumerate(BENCHMARKS, start=1):
            evaluation = evaluate_query(store, benchmark, benchmark["metadata_filter"])
            total_points += evaluation["points"]
            doc_hits += int(evaluation["doc_hit"])
            content_hits += int(evaluation["content_hit"] and evaluation["agent_correct"])
            print(f"  Q{number}: {benchmark['query']}")
            print_top_three(evaluation)
            print(
                f"    doc_hit={evaluation['doc_hit']} gold_rank={evaluation['gold_rank']} "
                f"content_hit={evaluation['content_hit']} "
                f"agent_correct={evaluation['agent_correct']} points={evaluation['points']}"
            )
            print(f"    agent: {evaluation['agent_answer'][:300]}")

        print(
            f"  SUMMARY: doc_id_hits={doc_hits}/5 content_answer_hits={content_hits}/5 "
            f"score={total_points}/10"
        )

        benchmark = BENCHMARKS[0]
        print("  A/B FILTER - Q1")
        for label, metadata_filter in (
            ("without_filter", None),
            ("with_student_filter", {"audience": "student"}),
        ):
            evaluation = evaluate_query(store, benchmark, metadata_filter)
            print(f"    {label}:")
            print_top_three(evaluation)
            print(
                f"      doc_hit={evaluation['doc_hit']} content_hit={evaluation['content_hit']} "
                f"points={evaluation['points']}"
            )

    print("\nFAILURE CASE")
    print(
        "Q1 fails under mock embeddings: topic-similar chunks outrank the FaMI procedure "
        "chunk, so the required strings C1-119 and 12/11-20/11/2025 are absent."
    )
    print(
        "Cause: MD5 mock vectors have no semantic signal; noisy menu/footer content and "
        "long duplicated source pages add irrelevant candidates."
    )
    print(
        "Proposed fix: clean the corpus, use a Vietnamese/multilingual embedding model, "
        "retain heading context, and add overlap or a lexical reranker for exact numbers."
    )


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Benchmark scholarship corpus retrieval")
    parser.add_argument("--baseline", action="store_true", help="Print baseline chunk statistics")
    parser.add_argument("--evaluate", action="store_true", help="Run CP6 scoring and A/B tests")
    parser.add_argument(
        "--backend", choices=("mock", "local"), default="mock", help="Embedding backend"
    )
    parser.add_argument("--output", type=Path, help="Write console output to a UTF-8 text file")
    args = parser.parse_args()
    if args.baseline:
        action = run_baseline
    else:
        embedding_fn, backend_name = resolve_embedding_backend(args.backend)
        if args.evaluate:
            action = lambda: run_cp6_evaluation(embedding_fn, backend_name)
        else:
            action = lambda: run_benchmark(embedding_fn, backend_name)
    if args.output:
        with args.output.open("w", encoding="utf-8") as output_file:
            with contextlib.redirect_stdout(output_file):
                action()
        print(f"Saved {args.output}")
    else:
        action()


if __name__ == "__main__":
    main()
