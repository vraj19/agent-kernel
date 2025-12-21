from concurrent.futures import ThreadPoolExecutor, TimeoutError, Future
from typing import Callable, Dict, Any, Optional
import traceback
import time

class ToolRunner:
    """
    Runs tool calls asynchronously with timeout support.
    - Register python callables by name via `register(name, fn)`.
    - execute(tool_spec, timeout=...) runs the callable with tool_spec['args']
    - If tool name not registered, returns a structured "not found" result.
    """

    def __init__(self, max_workers: int = 4, default_timeout: float = 5.0):
        self._registry: Dict[str, Callable[..., Any]] = {}
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self.default_timeout = default_timeout

    def register(self, name: str, fn: Callable[..., Any]) -> None:
        """Register a Python callable to handle calls for this tool name."""
        self._registry[name] = fn

    def unregister(self, name: str) -> None:
        """Unregister a previously registered tool name."""
        self._registry.pop(name, None)

    def _call_callable(self, fn: Callable[..., Any], args: Dict[str, Any]) -> Any:
        """Invoke the callable using kwargs when possible, fallback to single arg."""
        try: 
            if isinstance(args, dict):
                return fn(**args)
            return fn(args)
        except TypeError:
            # Fallback: pass the whole args as a single positional argument
            return fn(args)
        

    def execute(self, tool_spec: Dict[str, Any], timeout: Optional[float] = None) -> Dict[str, Any]:
        """
        Execute a tool spec of shape {"name": str, "args": dict}.
        Returns a normalized result dict:
        {"tool": name, "ok": True/False, "result": ... , "error": ...}
        """
        name = tool_spec.get("name")
        args = tool_spec.get("args", {}) or {}
        timeout = timeout if timeout is not None else self.default_timeout

        # Not registered => return structured "not found" result (backward compatiblity)
        if name not in self._registry:
            return {
                "tool": name,
                "ok": False,
                "result": None,
                "error": f"no registered tool '{name}'",
            }
        fn = self._registry[name]
        future: Future = self._executor.submit(self._call_callable, fn, args)
        start_ts = time.time()
        try:
            result = future.result(timeout=timeout)
            duration = time.time() - start_ts
            return {
                "tool": name,
                "ok": True,
                "result": result,
                "duration": duration,
            }
        except TimeoutError:
            future.cancel()
            return {
                "tool": name,
                "ok": False,
                "result": None,
                "error": f"tool '{name}' timed out after {timeout} seconds",
            }
        except Exception as e:
            tb_str = traceback.format_exc()
            return {
                "tool": name,
                "ok": False,
                "result": None,
                "error": f"tool '{name}' raised an exception: {str(e)}",
                "traceback": tb_str,
            }