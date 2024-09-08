from autogen import AssistantAgent, UserProxyAgent
import os
from groq import Groq

config_list = [
    {
        # Let's choose the Llama 3 model
        "model": "llama3-70b-8192",
        # Put your Groq API key here or put it into the GROQ_API_KEY environment variable.
        "api_key": "a p i k e y",
        # We specify the API Type as 'groq' so it uses the Groq client class
        "api_type": "groq",
    }
]


system_message = """
Planner: Suggest a plan. Revise the plan based on feedback from the admin and critic, until admin approval. 
The plan may involve an executor who can execute functions and tools. 
Explain the plan clearly, identifying which step is performed by an executor.

Your available actions are:

check_interface_status:
e.g. check_interface_status: eth0
Checks whether the interface is up (active) or down (inactive).

monitor_errors:
e.g. monitor_errors: eth0
Monitors for errors such as dropped packets or connectivity issues on the specified interface.

test_connectivity:
e.g. test_connectivity: eth0
Performs a basic ping test to determine if data can pass through the interface.

look_at_traffic:
e.g. look_at_traffic: eth0
Checks for traffic on the interface to see if it is operating normally or underutilized.

get_cpu_usage:
e.g. get_cpu_usage
Returns the system's most CPU-intensive processes for today.

Review Alerts:
Use the network system's alerts or logs to identify automatically reported issues.

Solution to Problem 1: What are the systems that used the most CPU today?

1. Use `get_cpu_usage` to retrieve a list of systems consuming the most CPU today.
2. Output the systems with the highest CPU usage.

Solution to Problem 2: Which interfaces are faulty or not working?

1. Use `check_interface_status` to determine if an interface is active or inactive.
2. If inactive or suspected of malfunction, use `monitor_errors` to check for issues like dropped packets or connectivity problems.
3. Use `test_connectivity` to verify if the interface can pass data.
4. Use `look_at_traffic` to check if traffic is flowing through the interface, and if there is very little or no traffic, this may indicate the interface is not functioning properly.
5. Based on the results from the above tools, identify faulty interfaces.
"""

# Create the agent that uses the LLM.
assistant_agent = AssistantAgent(
    name="Groq Assistant",
    system_message=system_message,
    llm_config={"config_list": config_list},
)

# Create the agent that represents the user in the conversation.
user_proxy_agent = UserProxyAgent("user", code_execution_config=False)

chat_result = user_proxy_agent.initiate_chat(
    assistant_agent,
    message="Which servers are currently down?",
)