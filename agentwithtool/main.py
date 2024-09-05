from typing import Annotated, Literal
import autogen

Operator = Literal["+", "-", "*", "/"]

def calculator(a: int, b: int, operator: Annotated[Operator, "operator"]) -> int:
    if operator == "+":
        return a + b
    elif operator == "-":
        return a - b
    elif operator == "*":
        return a * b
    elif operator == "/":
        return a / b
    else:
        raise ValueError("Invalid Operator")
    

local_llm_config = {
    "config_list": [
        {
            "model" : "NotRequired", # alread loaded with LiteLLM command
            "api_key" : "NotRequired",
            "base_url": "http://localhost:4000", # Your Lite LLM URL
            "price": [0,0]
        }
    ],
    "cache_seed": None, # Turns of caching, useful for testing different models
}

chatbot = autogen.AssistantAgent(
    name="chatbot",
    system_message="""For calculation tasks,
    only use the functions you have been provided with.
    If the function has been called preciously,
    return only the word 'TERMINATE'.""",
    llm_config=local_llm_config,
)

user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    is_termination_msg=lambda x: x.get("content", "") and "TERMINATE" in x.get("content", ""),
    human_input_mode="NEVER",
    max_consecutive_auto_reply=1,
    code_execution_config={"work_dir": "code", "use_docker": False},
)


@user_proxy.register_for_execution()
@chatbot.register_for_llm(description="Simple arithmetic calculator.")

def calculator_tool(
    a: Annotated[int, "First operand"],
    b : Annotated[int, "Second operand"],
    operator: Annotated[Operator, "Arithmetic operator (+, -, *, /)"]
) -> str:
    result = calculator(a, b, operator)
    return f"The result of {a} {operator} {b} is {result}."

res = user_proxy.initiate_chat(
    chatbot,
    message="What is 7 * 8?",
    summary_method="reflection_with_llm",
)

print(res)