from typing import Callable, Dict, Any, Optional
import uuid


from .state_machine import AgentState, AgentStateMachine
from .tool_validator import ToolValidator
from .checkpoint import CheckpointManager
from .tracer import KernelTracer
from .tool_runner import ToolRunner

from .constants import LIFECYCLE_STAGES

AgentLogic = Callable[[Dict[str, Any], str], Dict[str, Any]]


class KernelExecutor:
    """
    Executes the agent lifecycle using:
    - state machine for stage transitions
    - calls user-defined AgentLogic for stage-specific behavior
    - tool validation for tool calls
    - delegates tool execution to ToolRunner
    - checkpointing for saving/loading stages
    - emits small trace events for observability 
    """

    def __init__(
        self,
        tool_validator: Optional[ToolValidator] = None,
        checkpoint_manager: Optional[CheckpointManager] = None,
        tracer: Optional[KernelTracer] = None,
        tool_runner: Optional[ToolRunner] = None,
    ):
        self.tool_validator = tool_validator or ToolValidator()
        self.checkpoint_manager = checkpoint_manager or CheckpointManager()
        self.tracer = tracer or KernelTracer()
        self.tool_runner = tool_runner or ToolRunner()

    def start_run(self, initial_data: Dict[str, Any]) -> str:
        """
        Ensure a run_id exists in initial_data and return it.
        If user provided one (for replay), keep it; otherwise generate a UUID."""
        
        run_id = initial_data.get("_run_id")
        if not run_id:
            run_id = str(uuid.uuid4())
            initial_data["_run_id"] = run_id
        return run_id
    
    def _checkpoint_and_trace(self, state: AgentState):
        run_id = state.data.get("_run_id", "unknown")
        stage = state.stage

        # save full state checkpoint
        self.checkpoint_manager.save(run_id, stage, state.data)

        # Emit trace event
        self.tracer.emit(run_id, "stage_complete", {"stage": stage})

    def step(self, state: AgentState, agent_logic: AgentLogic) -> AgentState:
        """
        Advance one lifecycle stage and run the corresponding agent logic."""
        
        # Transition to next stage
        state = AgentStateMachine.transition(state)
        stage = state.stage
        run_id = state.data.get("_run_id")

        # Trace stage enter
        self.tracer.emit(run_id=run_id, event="stage_enter", payload={"stage": stage})

        # --- Stage logic execution ---
        if stage == "PLAN":
            output = agent_logic(state.data, "PLAN") or {}
            state.data["plan"] = output

        elif stage == "ACT":
            plan = state.data.get("plan",{})
            tool = plan.get("tool")
            if tool:
                self.tool_validator.validate(tool)
                result = self.tool_runner.execute(tool)
                # append observation (normalize to list)
                obs = state.data.get("observations", [])
                obs.append(result)
                state.data["observations"] = obs
        elif stage == "OBSERVE":
            obs_summary = agent_logic(state.data, "OBSERVE") or {}
            state.data['obs_summary'] = obs_summary

        elif stage == "DECIDE":
            decision = agent_logic(state.data, "DECIDE") or {}
            state.data['decision'] = decision
            
            # if the agent says finish, short-circuit to END
            if decision.get("finish"):
                state.stage = "END"
                self._checkpoint_and_trace(state)
                return state
            
        # checkpoint + trace after stage
        self._checkpoint_and_trace(state)
        return state