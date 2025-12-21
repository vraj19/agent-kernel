import json 
import os
from typing import Dict, Any, List, Optional
from .constants import LIFECYCLE_STAGES

class CheckpointManager:
    """Manages saving and loading of checkpoints for agent lifecycles.
    Each stage produces a checkpoint so runs can be replayed or debugged later.
    """

    def __init__(self, base_path: str = ".checkpoints"):
        self.base_path = base_path
        os.makedirs(self.base_path, exist_ok = True)

    def _run_dir(self, run_id: str) -> str:
        """Directory for a specific run's checkpoints."""
        return os.path.join(self.base_path, run_id)

    def save(self, run_id: str, stage: str, state: Dict[str, Any]) -> str:
        """Saves a checkpoint for a given stage and run_id."""
        run_dir = self._run_dir(run_id)
        os.makedirs(run_dir, exist_ok = True)

        filepath = os.path.join(run_dir, f"{stage}.json")
        
        payload = {
            "stage": stage,
            "data": state,
        }

        with open(filepath, "w") as f:
            json.dump(payload, f, indent = 2, default=str)
        return filepath

    def list_runs(self) -> List[str]:
        """Lists all run_ids that have checkpoints saved."""
        try:
            return sorted(
                d for d in os.listdir(self.base_path)
                if os.path.isdir(os.path.join(self.base_path, d))
            )
        except FileNotFoundError:
            return []
        
    def load(self, run_id: str, stage: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Loads a checkpoint for a given run_id and optional stage.
        If stage is None, loads the latest stage for the run.
        Return None if no checkpoint found.
        """
        run_dir = self._run_dir(run_id)
        if not os.path.exists(run_dir):
            return None

        # If a specific stage is requested, try to load it directly
        if stage:
            filepath = os.path.join(run_dir, f"{stage}.json")
            if  os.path.isfile(filepath):
                with open(filepath, "r") as f:
                    return json.load(f)
            return None
        
        # No stage provided , load the latest stage
        for s in reversed(LIFECYCLE_STAGES):
            filepath = os.path.join(run_dir, f"{s}.json")
            if os.path.isfile(filepath):
                with open(filepath, "r") as f:
                    return json.load(f)
        return None