

from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential


class GraphGateway:
    def __init__(self, graph) -> None:
        self._graph = graph

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception),
        reraise=True,
    )
    def invoke(self, *, user_id: str, message: str):
        config = {"configurable": {"thread_id": user_id}}
        return self._graph.invoke({"messages": message}, config=config)
