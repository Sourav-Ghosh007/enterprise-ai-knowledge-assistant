from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class Document:
    content: str
    source: str
    metadata: Dict[str, Any]


doc = Document("Test content", "test.txt", {"type": "txt"})
print(doc.content)
print(doc.metadata)