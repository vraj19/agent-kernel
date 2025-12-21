import inspect
from typing import Any, Callable, Dict, Optional

from .state_machine import AgentState
from .executor import KernelExecutor, AgentLogic
from .tool_runner import ToolRunner


class KernelNode:
    """
    Langgraph-compatible node that runs user-provided agentic logic through the kernel lifecycle.

    Usability modes:
        - Simple user function: def fn(state) -> dict
        * Kernel will automatically call this function at the PLAN and DECIDE stages.
        - Advanced user function: def fn(state, stage) -> dict
        * Kernel calls this function for the stages user chooses to handle, passing the current stage as an argument.
    """

    def __init__(
            self,
            user_logic: Callable[...,Dict[str, Any]],
            executor: Optional[KernelExecutor] = None,
            tool_runner: Optional[ToolRunner] = None,
    ):
        """
        user_logic: either fn(state: dict) or fn(state:dict, stage: str)
        executor: optional KernelExecutor instance (uses default if None)
        tool_runner: optional ToolRunner instance (uses default if None)
        """
        if executor is not None:
            self.executor = executor
        else:
            self.executor = KernelExecutor(tool_runner=tool_runner)

        self.user_logic = user_logic

        # Detect if user provided a stage-aware function
        sig = inspect.signature(user_logic)
        params = len(sig.parameters)
        # Accepts: 1 param => simple mode (Simple User), 2 or more params => stage-aware mode(Advanced user)
        self._stage_aware = params >= 2

    def _make_adapter(self) -> AgentLogic:
        """
        Return an AgentLogic callable with signature (state: Dict[str,Any], stage: str) -> Dict[str,Any]
        that adapts the user provided function accordingly.
        """
        def adapter(state: Dict[str, Any], stage: str) -> Dict[str, Any]:
            # If user provided stage-aware function, call directly
            if self._stage_aware:
                try:
                    return self.user_logic(state, stage) or {}
                
                except Exception as e:
                    return {}
            # Simple user function: call only for PLAN and DECIDE stages
            try:
                if stage == "PLAN":
                    return self.user_logic(state) or {}
                if stage == "DECIDE":
                    return self.user_logic(state) or {}
                return {}
            except Exception as e:
                return {}
        return adapter
    
    def __call__(self, input_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Entry point when used as a node in LangGraph.
        - bootstraps run_id into state
        - checkpoints INIT
        - loops through lifecycle via the executor until END
        - returns the final state.data
        """
        # Ensure state is a dict
        state_data = dict(input_state or {})

        # Build adapter and use executor
        agent_logic_adapter = self._make_adapter()

        # Start run (assign run_id if missing)
        run_if = self.executor.start_run(state_data)

        # Create AgentState and save initial checkpoint if executor supports it
        agent_state = AgentState(data=state_data, stage="INIT")

        try: 
            if hasattr(self.executor, 'checkpoint_agent_state'):
                self.executor.checkpoint_agent_state(agent_state)
        except Exception as e:
            pass

        # Loop until END stage
        while not agent_state.is_terminal():
            agent_state = self.executor.step(agent_state, agent_logic_adapter)

        # Return the final state dictionary (includes _run_id)
        return agent_state.data
    
    