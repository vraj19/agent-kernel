"""
Simple usage example of a basic agent.
Demonstrates::
    - simple user agent logic (no stage awareness)
    - registering a tool with ToolRunner
    - executing through KernelNode
"""

from agentkernel.kernel_node import KernelNode
from agentkernel.tool_runner import ToolRunner
import requests

# --- 1. Define a tool (normal python function) ---

def wikipedia_search(query: str) -> str:
    # Fetches short summary from Wikipedia
    title = query.replace(" ", "_")
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{title}"

    headers = {"User-Agent": "agentKernel/0.0.1 (https://github.com/vraj19/agent-kernel)"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()

    return {
        'title': data.get('title', 'N/A'),
        "summary": data.get('extract', 'No summary available.'),
        "url": data.get('content_urls', {}).get('desktop', {}).get('page', '')
    }

# --- 2. Register tool with ToolRunner ---
tool_runner = ToolRunner()
tool_runner.register(name="wikipedia_search", fn=wikipedia_search)

# --- 3. Define simple user agent logic ---
def agent_logic(state: dict) -> dict:
    return {
        "tool": {
            "name": "wikipedia_search",
            "args": {
                "query": state['input']
            }   
        }
    }

# --- 4. Wrap with KernelNode ---
agent_node = KernelNode(
    user_logic=agent_logic,
    tool_runner=tool_runner
)

# --- 5. Run ---

if __name__ == "__main__":
    result = agent_node({"input": "Artificial Intelligence"})
    print("\nFinal Agent State:")
    print(result)