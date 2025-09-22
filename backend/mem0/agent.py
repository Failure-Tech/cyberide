# Import dependencies
import os
import asyncio
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from mem0 import MemoryClient
from dotenv import load_dotenv
import uuid

load_dotenv()

google_api_key = os.getenv("GOOGLE_API_KEY")
mem0_api_key = os.getenv("MEM0_API_KEY")
# Define a global user ID for simplicity TODO: implement proper user management
USER_ID = "Alex"

# Initialize Mem0 client

mem0_client = MemoryClient(api_key=mem0_api_key)

def save_code_info(information: str) -> dict:
    response = mem0_client.add(
        [{"role": "user", "content": information}],
        user_id=USER_ID,
        run_id="code_session",
        metadata={"type": "code_info"},
    )

    return response

def retrieve_code_info(query: str) -> dict:
    results = mem0_client.search(
        query,
        user_id=USER_ID,
        limit=5,
        threshold=0.7,
        output_format="v1.1",
    )

    if results and len(results) > 0:
        memories = [memory["memory"] for memory in results.get("results", [])]
        return {
            "status": "success",
            "memories": memories,
            "count": len(memories)
        }

    else:
        return {
            "status": "no_results",
            "memories": [],
            "count": 0
        }
    
# DEFINE SPECIFIC CODE TOOLS THAT WOULD BE USEFUL FOR AGENT (search functionality, best practices, etc.)

code_agent = Agent(
    name="code_agent",
    model="gemini-1.5-flash",
    description="An agent that assists with coding tasks, leveraging code-related tools and memory.",
    instruction="""A coding assistant that helps with code-related tasks and remembers user preferences.""", # system prompt
    tools=[save_code_info, retrieve_code_info]
)

session_service = InMemorySessionService()

APP_NAME = "code_agent_app"
USER_ID = "Alex"
# SESSION_ID = "session_001" # also generate unique session ids
SESSION_ID = str(uuid.uuid4())

session = session_service.create_session(
    app_name=APP_NAME,
    user_id=USER_ID,
    session_id=SESSION_ID,
)

print(f"Using session ID: {SESSION_ID}")

runner = Runner(app_name=APP_NAME, agent=code_agent, session_service=session_service)

# Function to interact with the agent
async def call_agent_async(query, runner, user_id, session_id):
    """Sends a query to the agent and returns the final response."""
    print(f"\n>>> Patient: {query}")

    # Format the user's message
    content = types.Content(
        role='user',
        parts=[types.Part(text=query)]
    )

    # Set user_id for tools to access
    save_code_info.user_id = user_id
    retrieve_code_info.user_id = user_id

    # Run the agent
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=content
    ):
        if event.is_final_response():
            if event.content and event.content.parts:
                response = event.content.parts[0].text
                print(f"<<< Assistant: {response}")
                return response

    return "No response received."

# Example conversation flow
async def run_conversation():
    # First interaction - patient introduces themselves with key information
    await call_agent_async(
        "Hi, I'm Alex. I've been having headaches for the past week, and I have a penicillin allergy.",
        runner=runner,
        user_id=USER_ID,
        session_id=SESSION_ID
    )

    # # Request for health information
    # await call_agent_async(
    #     "Can you tell me more about what might be causing my headaches?",
    #     runner=runner,
    #     user_id=USER_ID,
    #     session_id=SESSION_ID
    # )

    # # Schedule an appointment
    # await call_agent_async(
    #     "I think I should see a doctor. Can you help me schedule an appointment for next Monday at 2pm?",
    #     runner=runner,
    #     user_id=USER_ID,
    #     session_id=SESSION_ID
    # )

    # # Test memory - should remember patient name, symptoms, and allergy
    # await call_agent_async(
    #     "What medications should I avoid for my headaches?",
    #     runner=runner,
    #     user_id=USER_ID,
    #     session_id=SESSION_ID
    # )

# Run the conversation example
if __name__ == "__main__":
    asyncio.run(run_conversation())