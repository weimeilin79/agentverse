from a2a.server.apps import A2AStarletteApplication
from a2a.types import AgentCard, AgentCapabilities, AgentSkill
from a2a.server.tasks import InMemoryTaskStore
from a2a.server.request_handlers import DefaultRequestHandler
from google.adk.agents.llm_agent import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
import os
import logging
from dotenv import load_dotenv
from shadowblade.agent_executor import ShadowBladeAgentExecutor
import uvicorn
from shadowblade import agent


load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

host=os.environ.get("A2A_HOST", "localhost")
port=int(os.environ.get("A2A_PORT",10003))
PUBLIC_URL=os.environ.get("PUBLIC_URL")

class ShadowBladeAgent:
    """An agent to help user planning a event with its desire location."""
    SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]

    def __init__(self):
        self._agent = self._build_agent()
        self.runner = Runner(
            app_name=self._agent.name,
            agent=self._agent,
            artifact_service=InMemoryArtifactService(),
            session_service=InMemorySessionService(),
            memory_service=InMemoryMemoryService(),
        )
        capabilities = AgentCapabilities(streaming=True)
        skill = AgentSkill(
            id="event_planner",
            name="Event planner",
            description="""
            This agent generates multiple fun plan suggestions tailored to your specified location, dates, and interests,
            all designed for a moderate budget. It delivers detailed itineraries,
            including precise venue information (name, latitude, longitude, and description), in a structured JSON format.
            """,
            tags=["instavibe"],
            examples=["What about Bostona MA this weekend?"],
        )
        self.agent_card = AgentCard(
            name="Event Planner Agent",
            description="""
            This agent generates multiple fun plan suggestions tailored to your specified location, dates, and interests,
            all designed for a moderate budget. It delivers detailed itineraries,
            including precise venue information (name, latitude, longitude, and description), in a structured JSON format.
            """,
            url=f"{PUBLIC_URL}",
            version="1.0.0",
            defaultInputModes=ShadowBladeAgent.SUPPORTED_CONTENT_TYPES,
            defaultOutputModes=ShadowBladeAgent.SUPPORTED_CONTENT_TYPES,
            capabilities=capabilities,
            skills=[skill],
        )

    def get_processing_message(self) -> str:
        return "Processing the planning request..."

    def _build_agent(self) -> LlmAgent:
        """Builds the LLM agent for the night out planning agent."""
        return agent.root_agent


if __name__ == '__main__':
    try:
        ShadowBladeAgent = ShadowBladeAgent()

        request_handler = DefaultRequestHandler(
            agent_executor=ShadowBladeAgentExecutor(ShadowBladeAgent.runner,ShadowBladeAgent.agent_card),
            task_store=InMemoryTaskStore(),
        )

        server = A2AStarletteApplication(
            agent_card=ShadowBladeAgent.agent_card,
            http_handler=request_handler,
        )
        logger.info(f"Attempting to start server with Agent Card: {ShadowBladeAgent.agent_card.name}")
        logger.info(f"Server object created: {server}")

        uvicorn.run(server.build(), host='0.0.0.0', port=port)
    except Exception as e:
        logger.error(f"An error occurred during server startup: {e}")
        exit(1)