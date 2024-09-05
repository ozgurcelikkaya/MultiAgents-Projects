import chromadb
from typing_extensions import Annotated
import autogen
from autogen import AssistantAgent
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent

local_llm_config = {
    "config_list": [
        {
            "model": "NotRequired",  # Loaded with LiteLLM command
            "api_key": "NotRequired",  # Not needed
            "base_url": "http://localhost:4000",  # Your LiteLLM URL
            "price": [0, 0],  # Put in price per 1K tokens [prompt, response] as free!
        }
    ],
    "cache_seed": None,  # Turns off caching, useful for testing different models
}

def termination_msg(x):
    return isinstance(x, dict) and "TERMINATE" == str(x.get("content", ""))[-9:].upper()


boss = autogen.UserProxyAgent(
    name="Boss",
    is_termination_msg=termination_msg,
    human_input_mode="NEVER",
    code_execution_config=False,
    default_auto_reply="Reply 'TERMINATE' if the task is done",
    description="The boss who ask questions and give tasks.",
)

boss_aid = RetrieveUserProxyAgent(
    name="Boss_Assistant",
    is_termination_msg=termination_msg,
    human_input_mode="NEVER",
    default_auto_reply="Reply 'TERMINATE' if the task is done",
    max_consecutive_auto_reply=3,
    retrieve_config={
        "task":"code",
        "docs_path":"....your...docs....path" # docs path
        "chunk_token_size": 1000,
        "model": local_llm_config,
        "collection_name":"groupchat",
        "get_or_create":True,
    },
    code_execution_config=False,
    description="Assistant who has extra content retrieval power for solving difficult problems.",
)

coder = AssistantAgent(
    name="Senior_Python_Engineer",
    is_termination_msg=termination_msg,
    system_message="You are a senior python engineer,you provide python code to answer questions. Reply 'TERMINATE' in the end when everything is done.",
    llm_config=local_llm_config,
    description="Senior Python Engineer who can write code to solve problems and answer questions",
)

nm = autogen.AssistantAgent(
    name="Network_Manager",
    is_termination_msg=termination_msg,
    system_message="You are a network manager. Reply 'TERMINATE' in the end when everything is done.",
    llm_config=local_llm_config,
    description="Network Manager who can design and plan the project.",
)

reviewer = autogen.AssistantAgent(
    name="Code_Reviewer",
    is_termination_msg=termination_msg,
    system_message="You are a code reviewer. Reply 'TERMINATE' in the end when everything is done.",
    llm_config=local_llm_config,
    description="Code Reviewer who can review the code.",
)

# PROBLEM = "How to use Network Management System? Give me sample code."

def _reset_agents():
    boss.reset()
    boss_aid.reset()
    coder.reset()
    nm.reset()
    reviewer.reset()


def rag_chat():
    _reset_agents()
    groupchat = autogen.GroupChat(
        agents=[boss_aid, nm, coder, reviewer], messages=[], max_round=12, speaker_selection_method="round_robin"
    )

    manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=local_llm_config)

    boss_aid.initiate_chat(
        manager,
        message=boss_aid.message_generator,
        problem=PROBLEM,
        n_results=3,
    )

    def norag_chat():
        _reset_agents()
        groupchat = autogen.GroupChat(
            agents=[boss, nm, coder, reviewer],
            messages=[],
            max_round=12,
            speaker_selection_method="auto",
            allow_repeat_speaker=False,
        )
        
        manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=local_llm_config)
        boss.initiate_chat(
            manager,
            message=PROBLEM,
        )


    def call_rag_chat():
        _reset_agents()

        def retrieve_content(
                message: Annotated[
                    str,
                    "Refined message which keeps the original meaning and can be used to retrieve content for code generation and questions answering.",
                ],
                n_results: Annotated[int, "number of results"] = 3,
        ) -> str:
            boss_aid.n_results = n_results
            _context ={"problem": message,"n_results": n_results}
            ret_msg = boss_aid.message_generator(boss_aid, None, _context)
            return ret_msg or message
        
        boss_aid.human_input_mode="NEVER"

        for caller in [pm,coder,reviewer]:
            d_retrieve_content = caller.register_for_llm(
                description="retrieve content for code generation and question answering.", api_style="function"
            )(retrieve_content)

        for executor in [boss,pm]:
            executor.register_for_execution()(d_retrieve_content)


        groupchat = autogen.GroupChat(
            agents=[boss, nm, coder, reviewer],
            messages=[],
            max_round=12,
            speaker_selection_method="round_robin",
            allow_repeat_speaker=False,
        )

        manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=local_llm_config)

        boss.initiate_chat( # start chatting
            manager,
            message=PROBLEM
        )