

from langgraph.graph import MessagesState


class AgentState(MessagesState):
    summary: str
    response_type: str
    audio_buffer: bytes
    image_path: str
