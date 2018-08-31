from typing import Optional
from .database import Database

import json


class InMemoryDatabase(Database):

    def __init__(self):
        super().__init__()
        self.storage = {}

    def add_document(self, id: str, doc: dict) -> None:
        self.storage[id] = doc

    def get_document_as_str(self, id: str) -> Optional[str]:
        doc = self.storage.get(id, None)
        return json.dumps(doc) if doc else None
