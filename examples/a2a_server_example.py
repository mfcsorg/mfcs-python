import json
from python_a2a import A2AServer, AgentCard, Message, MessageRole, TextContent
from python_a2a.models.agent import AgentSkill
from python_a2a.server.http import run_server

class EchoServer(A2AServer):
    def handle_message(self, message: Message) -> Message:
        user_input = message.content.text

        return Message(
            role=MessageRole.AGENT,
            content=TextContent(text=json.dumps({"status": "success", "data": f"Echo: {user_input}"}))
        )

agent_card = AgentCard(
    name="Echo Agent",
    description="Returns the same message it receives.",
    url="http://localhost:8000",
    skills=[
        AgentSkill(
            id="echo",
            name="Echo Skill",
            description="Echoes back the input text.",
            input_modes=["text"],
            output_modes=["text"]
        )
    ]
)

server = EchoServer(
    agent_card=agent_card
)

if __name__ == "__main__":
    run_server(server, host="localhost", port=8000)
