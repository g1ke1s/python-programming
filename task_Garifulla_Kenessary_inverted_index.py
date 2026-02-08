import argparse
import struct
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

    def dump(self, filepath: str, strategy: str = "struct") -> None:
        """Save the inverted index to a file using the specified strategy."""
        if strategy == "json":
            with open(filepath, 'w', encoding='utf-8') as file:
                json.dump(self.index, file)
        elif strategy == "struct":
            with open(filepath, 'wb') as file:
                serialized_table = []
                row_data = []

                for word, doc_ids in self.index.items():
                    encoded_word = word.encode("utf-8")
                    serialized_table.append((len(encoded_word), len(doc_ids)))
                    row_data.extend(doc_ids)

                table_size = len(serialized_table)
                file.write(struct.pack("I", table_size))

                for word, (length, doc_count) in zip(self.index.keys(), serialized_table):
                    word_bytes = word.encode("utf-8")
                    file.write(struct.pack(f"H{length}sH", length, word_bytes, doc_count))

                file.write(struct.pack(f"{len(row_data)}H", *row_data))

    @classmethod
    def load(cls, filepath: str, strategy: str = "struct"):
        """Load the inverted index from a file using the specified strategy."""
        instance = cls()
        if strategy == "json":
            with open(filepath, 'r', encoding='utf-8') as file:
                instance.index = json.load(file)
        elif strategy == "struct":
            with open(filepath, 'rb') as file:
                table_size = struct.unpack("I", file.read(struct.calcsize("I")))[0]
                instance.index = {}
                for _ in range(table_size):
                    length = struct.unpack("H", file.read(struct.calcsize("H")))[0]
                    word_bytes = file.read(length)
                    doc_count = struct.unpack("H", file.read(struct.calcsize("H")))[0]
                    doc_ids = struct.unpack(f"{doc_count}H", file.read(doc_count * struct.calcsize("H")))
                    instance.index[word_bytes.decode("utf-8")] = list(doc_ids)
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

    build_parser = subparsers.add_parser("build", help="Build an inverted index")
    build_parser.add_argument("--dataset", default="sample.txt", help="Path to the dataset file (default: sample.txt)")
    build_parser.add_argument("--output", required=True, help="Path to save the inverted index")
    build_parser.add_argument("--strategy", choices=["json", "struct"], default="struct", help="Storage strategy (default: struct)")

    query_parser = subparsers.add_parser("query", help="Query the inverted index")
    query_parser.add_argument("--index", required=True, help="Path to the inverted index file")
    query_parser.add_argument("--query", nargs="+", action="append", help="Query words")

    args = parser.parse_args()

    if args.command == "build":
        documents = load_documents(args.dataset)
        inverted_index = build_inverted_index(documents)
        inverted_index.dump(args.output, strategy=args.strategy)
        print(f"Inverted index built and saved to {args.output}")

    elif args.command == "query":
        inverted_index = InvertedIndex.load(args.index, strategy="struct")
        for query_words in args.query:
            result = inverted_index.query(query_words)
            print(",".join(map(str, result)))

if __name__ == "__main__":
    main()

