from langchain.agents import initialize_agent
from langchain.agents import Tool
from langchain.chat_models import ChatOpenAI
from langchain.agents import AgentExecutor

tools = [Tool(name="Search", func=my_search_function)]
llm = ChatOpenAI()

agent_executor = initialize_agent(tools, llm, agent_type="zero_shot", verbose=True)

# Example function to interact with agent
def run_agent(agent_executor, input_data):
    response = agent_executor.run(input_data)
    return response
