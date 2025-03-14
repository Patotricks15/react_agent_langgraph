from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage
from langgraph.graph import StateGraph, END
from pydantic import BaseModel


class AgentState(BaseModel):
    input_text: str
    thought: str
    output_action: str


llm = ChatOpenAI(model="gpt-3.5-turbo-1106", temperature=0)

def reasoning_agent(state: AgentState) -> AgentState:
    response = llm([HumanMessage(content=f"Think step by step: {state.input_text}")])

    return AgentState(
        input_text=state.input_text,
        thought=response.content,
        output_action=state.output_action
    )

def action_agent(state: AgentState) -> AgentState:
    response = llm([HumanMessage(content=f"Based on the problem: {state.input_text}, and the thought {state.thought}, build an action plan")])

    return AgentState(
        input_text=state.input_text,
        thought=state.thought,
        output_action=response.content
    )

workflow = StateGraph(state_schema=AgentState)

workflow.add_node("reasoning", reasoning_agent)
workflow.add_node("action", action_agent)

workflow.set_entry_point("reasoning")
workflow.add_edge("reasoning", "action") 
workflow.add_edge("action", END)

graph = workflow.compile()

user_input = "Build a 3-months plan to study the basics of English language"
initial_state = AgentState(
    input_text=user_input,
    thought="",
    output_action=""
)

result = graph.invoke(initial_state)

png_bytes = graph.get_graph(xray=1).draw_mermaid_png()

# Save the PNG data to a file
with open("react_agent_graph.png", "wb") as f:
    f.write(png_bytes)

print(result)
