# INIT -> PLAN -> ACT -> OBSERVE -> DECIDE -> END

from typing import Any, Dict, Optional
from .constants import LIFECYCLE_ORDER

class AgentState:
    """
    Represents the state of an agent in the execution flow.
    Manages transitions between different stage.
    """
    def __init__(self, data: Optional[Dict[str, Any]] = None, stage: str = "INIT"):
        self.data = data or {}
        self.stage = stage

    def next_stage(self) -> Optional[str]:
        """
        Determines the next stage in the execution flow.
        """
        return LIFECYCLE_ORDER.get(self.stage)

    def is_terminal(self) -> bool:
        return self.stage == "END"
    
class AgentStateMachine:
    """
    Validates and manages the agent lifecycle stages.
    """
    @staticmethod
    def validate_transition(current_stage: str, next_stage: Optional[str]) -> None:
        """
        Validates if the transition from current_stage to next_stage is valid.
        """
        if next_stage is None:
            raise ValueError(f"No next stage is defined after {current_stage}.")
        if LIFECYCLE_ORDER.get(current_stage) != next_stage:
            raise ValueError(f"Invalid transition from {current_stage} to {next_stage}.")
        
    @staticmethod
    def transition(state: AgentState) -> AgentState:
        """
        Transition of the agent to the next stage.
        """
        next_stage = state.next_stage()
        AgentStateMachine.validate_transition(state.stage, next_stage)
        state.stage = next_stage
        return state