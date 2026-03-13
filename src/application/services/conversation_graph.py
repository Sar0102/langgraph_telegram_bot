
import random
from typing import Literal

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import BaseTool
from langgraph.constants import END, START
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from pydantic import BaseModel, Field

from src.application.state import AgentState
from src.domain.constants import AUDIO, TEXT
from src.domain.policies import should_summarize
from src.domain.prompts import ROUTER_SYSTEM_PROMPT, SYSTEM_PROMPT


class RouterResponse(BaseModel):
    response_type: str = Field(
        description='The response type for the next reply. Must be "text", "audio", or "image".'
    )


class ConversationGraphFactory:
    def __init__(
        self,
        *,
        llm,
        retriever_tool: BaseTool,
        media_service,
        checkpointer,
        summary_threshold: int,
    ) -> None:
        self._llm = llm
        self._llm_with_tools = llm.bind_tools([retriever_tool])
        self._retriever_tool = retriever_tool
        self._media_service = media_service
        self._checkpointer = checkpointer
        self._summary_threshold = summary_threshold

    def create(self):
        workflow = StateGraph(AgentState)
        workflow.add_node("router_node", self._router_node)
        workflow.add_node("generate_text_response_node", self._generate_text_response_node)
        workflow.add_node("summarize_conversation_node", self._summarize_conversation_node)
        workflow.add_node("tools", ToolNode([self._retriever_tool]))
        workflow.add_node("generate_final_response_node", self._generate_final_response_node)

        workflow.add_edge(START, "router_node")
        workflow.add_edge("router_node", "generate_text_response_node")
        workflow.add_conditional_edges(
            "generate_text_response_node",
            tools_condition,
            {"tools": "tools", END: "generate_final_response_node"},
        )
        workflow.add_edge("tools", "generate_text_response_node")
        workflow.add_conditional_edges(
            "generate_final_response_node",
            self._should_summarize_conversation,
        )
        workflow.add_edge("summarize_conversation_node", END)
        return workflow.compile(checkpointer=self._checkpointer)

    def _router_node(self, state: AgentState):
        llm_structured = self._llm.with_structured_output(RouterResponse)
        response = llm_structured.invoke(
            [SystemMessage(content=ROUTER_SYSTEM_PROMPT), state["messages"][-1]]
        )
        if response.response_type == TEXT and random.random() > 0.5:
            return {"response_type": AUDIO}
        return {"response_type": response.response_type}

    def _generate_text_response_node(self, state: AgentState):
        summary = state.get("summary", "")
        if summary:
            system_prompt = f'{SYSTEM_PROMPT}\nSummary of conversation earlier: "{summary}"'
        else:
            system_prompt = SYSTEM_PROMPT
        messages = [SystemMessage(content=system_prompt)] + state["messages"]
        response = self._llm_with_tools.invoke(messages)
        return {"messages": response}

    def _summarize_conversation_node(self, state: AgentState):
        summary = state.get("summary", "")
        if summary:
            summary_msg = (
                f"This is the summary of the conversation to date: {summary}\n\n"
                "Extend the summary by taking into account the new messages above:"
            )
        else:
            summary_msg = "Create a summary of the conversation above:"
        messages = state["messages"] + [HumanMessage(content=summary_msg)]
        response = self._llm_with_tools.invoke(messages)
        delete_messages = self._media_service.make_remove_messages(state["messages"][:-2])
        return {"summary": response.content, "messages": delete_messages}

    def _generate_final_response_node(self, state: AgentState):
        response_type = state["response_type"]
        content = state["messages"][-1].content
        if response_type == AUDIO:
            return {"audio_buffer": self._media_service.generate_audio(content)}
        if response_type == "image":
            return {"image_path": self._media_service.generate_image(content)}
        return state

    def _should_summarize_conversation(
        self, state: AgentState
    ) -> Literal["summarize_conversation_node", END]:
        if should_summarize(len(state["messages"]), self._summary_threshold):
            return "summarize_conversation_node"
        return END
