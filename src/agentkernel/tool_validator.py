from typing import Dict , Any

class ToolValidator:
    """
    Validates the tool calls before execution.
    """

    def validate(self, tool_call: Dict[str, Any]) -> bool:
        # Must be a dictionary 

        if not isinstance(tool_call, dict):
            raise ValueError("Tool call must be a dictionary")
        
        # Must have a name key
        if "name" not in tool_call or not isinstance(tool_call["name"], str):
            raise ValueError("Tool call must include a 'name' key of type str")
        
        # Args must be a dictionary if present
        if "args" in tool_call and not isinstance(tool_call["args"], dict):
            raise ValueError("Tool call 'args' must be a dictionary if provided")
        
        # --- Future Extensions ---
        # TODO: enforce allowed tool list (whitelist) 
        # TODO: enforce max timeouts per tool
        # TODO: enforce cost caps
        # TODO: add rate limiting

        return True