
import atexit
import sqlite3
import time
import logging
import threading

from typing import Any, Sequence

from evals.data import jsondumps
from evals.base import RunSpec
from evals.record import Event, RecorderBase

logger = logging.getLogger(__name__)

class SqliteRecorder(RecorderBase):
    def __init__(self, db_path: str, run_spec: RunSpec) -> None:
        super().__init__(run_spec)
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self._writing_lock = threading.Lock()

        # create tables if they don't exist
        self.conn.execute("CREATE TABLE IF NOT EXISTS runs (run_id, model_name, eval_name, base_eval, split, run_config, settings, created_by, created_at, final_report);")
        self.conn.execute("CREATE TABLE IF NOT EXISTS events (run_id, event_id, sample_id, type, data, created_by, created_at);")
        
        # insert run
        data = {
            "run_id": run_spec.run_id,
            "model_name": jsondumps(dict(completions=run_spec.completion_fns)),
            "eval_name": run_spec.eval_name,
            "base_eval": run_spec.base_eval,
            "split": run_spec.split,
            "run_config": jsondumps(run_spec.run_config),
            "settings": jsondumps(run_spec.run_config.get("initial_settings", {})),
            "created_by": run_spec.created_by,
            "created_at": run_spec.created_at,
            "final_report": None
        }
        self.conn.cursor().execute(
            "INSERT INTO runs VALUES(:run_id, :model_name, :eval_name, :base_eval, :split, :run_config, :settings, :created_by, :created_at, :final_report)", 
            data
        )
        atexit.register(self.flush_events)

    def _flush_events_internal(self, events_to_write: Sequence[Event]):
        with self._writing_lock:
            # insert events
            def event_to_record(event: Event):
                return {
                    "run_id": event.run_id,
                    "event_id": event.event_id,
                    "sample_id": event.sample_id,
                    "type": event.type,
                    "data": jsondumps(event.data),
                    "created_by": event.created_by,
                    "created_at": event.created_at
                }
            data = list(map(event_to_record, events_to_write))
            self.conn.cursor().executemany(
                "INSERT INTO events VALUES(:run_id, :event_id, :sample_id, :type, :data, :created_by, :created_at)", 
                data
            )
            # record flush
            self._last_flush_time = time.time()
            self._flushes_done += 1

    def record_final_report(self, final_report: Any):
        with self._writing_lock:
            # write final_report to runs
            params = {
                "run_id": self.run_spec.run_id,
                "final_report": jsondumps(final_report),
            }
            self.conn.cursor().execute(
                "UPDATE runs SET final_report = :final_report WHERE run_id = :run_id",
                params
            )

    def record_event(self, type, data=None, sample_id=None):
        # try to serialize data so we fail early!
        _ = jsondumps(data)
        return super().record_event(type, data, sample_id)