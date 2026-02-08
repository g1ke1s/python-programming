import pytest
import subprocess
from task_Garifulla_Kenessary_inverted_index import InvertedIndex, load_documents, build_inverted_index

def test_inverted_index_dump_is_not_zero(tmp_path):
    documents = load_documents("sample.txt")
    inverted_index = build_inverted_index(documents)
    dump_path = tmp_path / "index.json"
    inverted_index.dump(dump_path, strategy="json")
    assert dump_path.stat().st_size > 0

def test_inverted_index_query_cp1251(tmp_path):
    documents = {1: "пример текста", 2: "текст с кодировкой cp1251"}
    inverted_index = build_inverted_index(documents)
    dump_path = tmp_path / "index.struct"
    inverted_index.dump(dump_path, strategy="struct")

    loaded_index = InvertedIndex.load(dump_path, strategy="struct")
    result = loaded_index.query(["текст".encode("cp1251").decode("cp1251")])
    assert 1 in result or 2 in result

def test_inverted_index_query_utf8(tmp_path):
    documents = {1: "example text", 2: "utf-8 encoding text"}
    inverted_index = build_inverted_index(documents)
    dump_path = tmp_path / "index.struct"
    inverted_index.dump(dump_path, strategy="struct")

    loaded_index = InvertedIndex.load(dump_path, strategy="struct")
    result = loaded_index.query(["text"])
    assert 1 in result or 2 in result

def test_inverted_index_query_utf8_cli(tmp_path):
    dataset_path = "sample.txt"

    index_path = tmp_path / "index.struct"
    subprocess.run([
        "python3", "task_Garifulla_Kenessary_inverted_index.py",
        "build", "--dataset", dataset_path, "--output", str(index_path), "--strategy", "struct"
    ], check=True)

    result = subprocess.run([
        "python3", "task_Garifulla_Kenessary_inverted_index.py",
        "query", "--index", str(index_path), "--query", "text"
    ], capture_output=True, text=True, check=True)
    assert "1" in result.stdout or "2" in result.stdout

def test_json_and_default_strategy_are_different():
    assert InvertedIndex.dump.__defaults__[0] != "json"

def test_struct_and_default_strategy_are_the_same():
    assert InvertedIndex.dump.__defaults__[0] == "struct"

def test_inverted_index_build_compression_quality(tmp_path):
    documents = load_documents("sample.txt")
    inverted_index = build_inverted_index(documents)
    dump_path = tmp_path / "index.struct"
    inverted_index.dump(dump_path, strategy="struct")

    compression_size = dump_path.stat().st_size / (1024 * 1024)  # Размер в МБ
    assert compression_size <= 12

