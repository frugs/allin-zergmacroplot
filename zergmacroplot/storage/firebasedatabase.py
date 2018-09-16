import json
from typing import Optional

import pyrebase

from .database import Database


class FirebaseDatabase(Database):

    def __init__(self, serialised_config: str):
        super().__init__()
        self.config = json.loads(serialised_config)

    def add_document(self, doc_id: str, doc: dict) -> None:
        self._upload_analysis(doc_id, doc)

    def get_document_as_str(self, doc_id: str) -> Optional[str]:
        return self._fetch_analysis_data(doc_id)

    def _open_db_connection(self):
        return pyrebase.initialize_app(self.config).database()

    def _upload_analysis(self, replay_id: str, replay_analysis: dict) -> None:
        db = self._open_db_connection()
        db.child("zerg_macro_analyses").child(replay_id).set(
            json.dumps(replay_analysis))

    def _fetch_analysis_data(self, replay_id: str) -> str:
        db = self._open_db_connection()
        analysis_data = db.child("zerg_macro_analyses").child(
            replay_id).get().val()
        return analysis_data if analysis_data else ""
