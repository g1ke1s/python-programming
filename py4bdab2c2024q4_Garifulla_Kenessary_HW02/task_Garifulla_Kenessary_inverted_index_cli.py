import argparse
import json
from typing import List, Dict


class InvertedIndex:
    def __init__(self):
        self.index = {}

    def query(self, words: List[str]) -> List[int]:
        """Find documents containing all given words."""
        result_sets = [set(self.index.get(word, [])) for word in words]
        if result_sets:
            return list(set.intersection(*result_sets))
        return []

    def dump(self, filepath: str) -> None:
        """Save the inverted index to a file."""
        with open(filepath, 'w', encoding='utf-8') as file:
            json.dump(self.index, file)

    @classmethod
    def load(cls, filepath: str):
        """Load the inverted index from a file."""
        instance = cls()
        with open(filepath, 'r', encoding='utf-8') as file:
            instance.index = json.load(file)
        return instance


def load_documents(filepath: str) -> Dict[int, str]:
    """Load documents from a file."""
    documents = {}
    with open(filepath, 'r', encoding='utf-8') as file:
        for line in file:
            doc_id, content = line.strip().split('\t', 1)
            documents[int(doc_id)] = content
    return documents


def build_inverted_index(documents: Dict[int, str]) -> InvertedIndex:
    """Build an inverted index from the documents."""
    inverted_index = InvertedIndex()
    for doc_id, content in documents.items():
        for word in content.split():
            if word not in inverted_index.index:
                inverted_index.index[word] = []
            if doc_id not in inverted_index.index[word]:
                inverted_index.index[word].append(doc_id)
    return inverted_index


def main():
    parser = argparse.ArgumentParser(description="Inverted Index CLI")
    subparsers = parser.add_subparsers(dest="command")

    # Subparser for building the index
    build_parser = subparsers.add_parser("build", help="Build an inverted index")
    build_parser.add_argument("--dataset", required=True, help="Path to the dataset file")
    build_parser.add_argument("--output", required=True, help="Path to save the inverted index")
    build_parser.add_argument("--strategy", choices=["json"], default="json", help="Storage strategy (default: json)")

    # Subparser for querying the index
    query_parser = subparsers.add_parser("query", help="Query the inverted index")
    query_parser.add_argument("--json-index", required=True, help="Path to the inverted index file")
    query_parser.add_argument("--query", nargs="+", action="append", required=True, help="Query words")

    args = parser.parse_args()

    if args.command == "build":
        documents = load_documents(args.dataset)
        inverted_index = build_inverted_index(documents)
        inverted_index.dump(args.output)
        print(f"Inverted index built and saved to {args.output}")

    elif args.command == "query":
        inverted_index = InvertedIndex.load(args.json_index)
        for query_words in args.query:
            result = inverted_index.query(query_words)
            print(",".join(map(str, result)))


if __name__ == "__main__":
    main()

