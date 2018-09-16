from typing import Optional
from .database import Database

import json


class InMemoryDatabase(Database):

    def __init__(self):
        super().__init__()
        self.storage = {}

    def add_document(self, doc_id: str, doc: dict) -> None:
        self.storage[doc_id] = doc

    def get_document_as_str(self, doc_id: str) -> Optional[str]:
        doc = self.storage.get(doc_id, None)
        return json.dumps(doc) if doc else None
