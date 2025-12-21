import json
import os
from datetime import datetime
from typing import Dict, Any, Optional

class KernelTracer:
    """Tracer for logging kernel events per run_id.
    """

    def __init__(self, base_path: str = ".traces"):
        self.base_path = base_path
        os.makedirs(self.base_path, exist_ok = True)

    def _trace_file(self, run_id:str) -> str:
        return os.path.join(self.base_path, f"{run_id}.trace.jsonl")
    
    def emit(self, run_id: str, event: str, payload: Optional[Dict[str, Any]] =None) -> str:
        """Emit a trace event for a given run_id.
        Returns the filepath written."""

        entry = {
            "ts": datetime.utcnow().isoformat() + "Z",
            "event": event,
            "payload": payload or {}                    
        }

        filename = self._trace_file(run_id)
        with open(filename, "a") as f:
            f.write(json.dumps(entry, default=str) + "\n")
        return filename
    