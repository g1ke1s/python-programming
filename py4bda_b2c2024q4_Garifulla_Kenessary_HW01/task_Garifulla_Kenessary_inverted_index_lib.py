from __future__ import annotations
from typing import Dict, List
from collections import defaultdict
import json


class InvertedIndex:
    def __init__(self):
        self.index = defaultdict(list)  # Map word to list of document IDs

    def add(self, doc_id: int, words: List[str]) -> None:
        """Add words from a document to the inverted index."""
        for word in words:
            if doc_id not in self.index[word]:
                self.index[word].append(doc_id)

    def query(self, words: List[str]) -> List[int]:
        """Return the list of relevant documents for the given query."""
        if not words:
            return []
        result_sets = [set(self.index[word]) for word in words if word in self.index]
        if not result_sets:
            return []
        return list(set.intersection(*result_sets))

    def dump(self, filepath: str) -> None:
        """Save the inverted index to a file."""
        with open(filepath, "w") as f:
            json.dump(self.index, f)

    @classmethod
    def load(cls, filepath: str) -> InvertedIndex:
        """Load the inverted index from a file."""
        with open(filepath, "r") as f:
            data = json.load(f)
        instance = cls()
        instance.index = defaultdict(list, {k: v for k, v in data.items()})
        return instance

    def __eq__(self, other: object) -> bool:
        """Check equality based on the index content."""
        if not isinstance(other, InvertedIndex):
            return NotImplemented
        return self.index == other.index




class ArrayStoragePolicy:
    @staticmethod
    def dump(word_to_docs_mapping: Dict[str, List[int]], filepath: str) -> None:
        """Dump the inverted index to a file using an array-based storage."""
        with open(filepath, "w") as f:
            json.dump(word_to_docs_mapping, f)

    @staticmethod
    def load(filepath: str) -> Dict[str, List[int]]:
        """Load the inverted index from a file."""
        with open(filepath, "r") as f:
            return json.load(f)




def load_documents(filepath: str) -> Dict[str, str]:
    """Load documents from a file into a dictionary."""
    documents = {}
    with open(filepath, "r") as fin:
        for line in fin:
            parts = line.strip().split(maxsplit=1)
            if len(parts) == 2:
                doc_id = str(parts[0])
                content = parts[1]
                documents[doc_id] = content
    return documents


def build_inverted_index(documents: Dict[str, str]) -> InvertedIndex:
    """Build an inverted index from the given documents."""
    inverted_index = InvertedIndex()
    for doc_id, content in documents.items():
        words = content.split()
        inverted_index.add(str(doc_id), words)
    return inverted_index


def main():
    """Example main function demonstrating usage."""
    # Load documents
    documents = load_documents("/root/testing/wikipedia_sample")
    # Build inverted index
    inverted_index = build_inverted_index(documents)
    # Save inverted index to file
    inverted_index.dump("/root/testing/inverted.index")
    # Load inverted index from file
    loaded_inverted_index = InvertedIndex.load("/root/testing/inverted.index")
    # Query the index
    document_ids = loaded_inverted_index.query(["two", "words"])
    print(f"Documents containing the query words: {document_ids}")

if __name__ == "__main__":
    main()

