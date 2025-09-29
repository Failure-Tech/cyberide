"""
Hi, I'm Goku!
"""
import os
import uuid
import asyncio
import threading
import contextvars
import pprint

from prompt import SYSTEM_PROMPT
from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

from google.adk.agents import LlmAgent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
from google.genai.types import Content, Part
from google import genai

from mem0 import MemoryClient, Memory
# import firebase_admin
# from firebase_admin import credentials, storage

# ----------------------------- ENV & BASIC SETUP -----------------------------
load_dotenv()

google_api_key = os.getenv("GOOGLE_API_KEY")
memo_api_key   = os.getenv("MEMO_API_KEY")
# openai.api_key = os.getenv("OPENAI_API_KEY")

model = "gemini-2.5-flash"                 # LLM model to use

mem0_client = MemoryClient(api_key=memo_api_key)

novel_client = genai.Client(api_key=google_api_key)

app_name = "memory_alzheimers_assistant_app"

current_user_id_var = contextvars.ContextVar("current_user_id", default=None)
thread_local        = threading.local()

# ----------------------------- FIREBASE SETUP --------------------------------
# TODO: Add Firebase credentials file to enable Firebase functionality
# cred = credentials.Certificate("./docs-3315a-firebase-adminsdk-lw73m-c27400fd79.json")
# firebase_admin.initialize_app(
#     cred,
#     {"storageBucket": os.getenv("NEXT_PUBLIC_FIREBASE_STORAGEBUCKET")}
# )

# ----------------------------- MEMORY HELPERS --------------------------------
memory_cache = {}

def get_memory_from_user(user_id: str) -> Memory:
    """
    Build (or fetch cached) Mem0 Memory object for this user.
    All Neo4j graph-store settings have been removed.
    """
    if user_id in memory_cache:
        return memory_cache[user_id]

    user_config = {
        "embedding_model": {
            "provider": "google",
            "config": {
                "model": "models/embedding-001",
                "api_key": google_api_key,
            },
        },
        "llm": {
            "provider": "gemini",
            "config": {
                "model": model,
                "temperature": 0.2,
                "api_key": google_api_key,
                "max_tokens": 2000,
                "top_p": 1.0,
            },
        },
        # ---------------------------------------------------------------------
        # Neo4j graph-store block REMOVED – comment back in if you restore Neo4j
        "graph_store": {
            "provider": "neo4j",
            "config": {
                "url": os.getenv("NEO4JURL"),
                "username": os.getenv("NEO4JUSERNAME"),
                "password": os.getenv("NEO4JPASSWORD"),
                "database": os.getenv("NEO4JDB"),
                "default_node_properties": {"userId": user_id},
            },
            "llm": {
                "provider": "gemini",
                "config": {"model": model, "temperature": 0.0, "api_key": google_api_key},
            },
        },
        # ---------------------------------------------------------------------
    }

    pprint.pprint(user_config)  # optional: comment out to silence console noise
    mem = Memory.from_config(config_dict=user_config)
    memory_cache[user_id] = mem
    return mem

def test_neo4j_connection(user_id: str):
    try:
        memory = get_memory_from_user(user_id=user_id)

        # Test with a simple message
        test_result = memory.add(
            messages=[{"role": "user", "content": "Test message for Neo4j connection"}],
            user_id=user_id
        )
        print(f"[DEBUG] Neo4j test successful: {test_result}")
        return True
    except Exception as e:
        print(f"[ERROR] Neo4j test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

# ----------------------- TOOL FUNCTIONS FOR THE AGENT ------------------------
# def save_user_info(information: str, **kwargs) -> dict:
#     user_id = kwargs.get("user_id") or current_user_id_var.get() or getattr(thread_local, "user_id", None)
#     if not user_id:
#         return {"status": "error", "message": "user_id is missing"}

#     try:
#         print(f"[DEBUG] SAVE_USER_INFO called for user_id={user_id}: {information}")
#         response = mem0_client.add(
#             messages=[{"role": "user", "content": information}],
#             user_id=user_id,
#             metadata={"type": "client_information", "app": app_name, "userId": user_id},
#             output_format="v1.1"
#         )

#         memory = get_memory_from_user(user_id=user_id)
#         memory.save(information)

#         return {"status": "saved", "details": response, "message": f"Successfully saved: {information}"}
#     except Exception as e:
#         print(f"[ERROR] Exception in save_user_info: {e}")
#         return {"status": "error", "message": f"Failed to save: {str(e)}"}

def save_user_info(information: str, **kwargs) -> dict:
    user_id = kwargs.get("user_id") or current_user_id_var.get() or getattr(thread_local, "user_id", None)
    if not user_id:
        return {"status": "error", "message": "user_id is missing"}

    try:
        print(f"[DEBUG] SAVE_USER_INFO called for user_id={user_id}: {information}")

        # Save to Mem0 cloud
        response = mem0_client.add(
            messages=[{"role": "user", "content": information}],
            user_id=user_id,
            metadata={"type": "client_information", "app": app_name, "userId": user_id},
            output_format="v1.1"
        )

        # Save to local Neo4j
        try:
            memory = get_memory_from_user(user_id=user_id)
            neo4j_result = memory.save(information)
            print(f"[DEBUG] Neo4j save result: {neo4j_result}")
        except Exception as neo4j_error:
            print(f"[ERROR] Neo4j save failed: {neo4j_error}")
            # Continue execution - don't fail the whole function

        return {"status": "saved", "details": response, "message": f"Successfully saved: {information}"}
    except Exception as e:
        print(f"[ERROR] Exception in save_user_info: {e}")
        return {"status": "error", "message": f"Failed to save: {str(e)}"}

request_memory_results = {}

def retrieve_user_info(query: str, **kwargs) -> dict:
    user_id = kwargs.get("user_id") or current_user_id_var.get() or getattr(thread_local, "user_id", None)
    if not user_id:
        return {"status": "error", "message": "user_id is missing"}

    try:
        print(f"[DEBUG] RETRIEVE_USER_INFO called for user_id={user_id}, query='{query}'")
        results = mem0_client.search(query=query, user_id=user_id, limit=10, output_format="v1.1")

        if results and results.get("results"):
            memories = [m["memory"] for m in results["results"]]
            request_memory_results[user_id] = memories
            return {"status": "success", "memories": memories, "count": len(memories)}
        else:
            return {"status": "no_results", "memories": [], "count": 0}
    except Exception as e:
        print(f"[ERROR] Exception in retrieve_user_info: {e}")
        return {"status": "error", "message": f"Failed to retrieve: {str(e)}"}

def delete_user_info(query: str, **kwargs) -> dict:
    user_id = kwargs.get("user_id") or current_user_id_var.get() or getattr(thread_local, "user_id", None)
    if not user_id:
        return {"status": "error", "message": "user_id is missing"}
    try:
        print(f"[DEBUG] DELETE_USER_INFO called for user_id={user_id}: {query}")
        response = mem0_client.delete(
            messages=[{"role": "user", "content": query}],
            user_id=user_id,
            output_format="v1.1"
        )
        return {"status": "deleted", "details": response, "message": f"Successfully deleted: {query}"}
    except Exception as e:
        print(f"[ERROR] Exception in delete_user_info: {e}")
        return {"status": "error", "message": f"Failed to delete: {str(e)}"}

def generate_code(query: str, **kwargs) -> dict:
    try:
        user_id = kwargs.get("user_id") or current_user_id_var.get() or getattr(thread_local, "user_id", None)
        if not user_id:
            return {"status": "error", "message": "user_id is missing"}
        
        # First, actually GENERATE the code using the Gemini API
        formatted_query = f"""
Please generate code for the following request and return ONLY the code wrapped in triple backticks with the language tag.

Request: {query}
"""
        
        # Use the novel_client to actually generate the code
        response = novel_client.models.generate_content(
            model=model,
            contents=formatted_query,
            config=types.GenerateContentConfig(
                system_instruction="You are a code generator. Always return code wrapped in triple backticks with the proper language tag. For example: ```python\ncode here\n```",
            )
        )
        
        generated_code = response.text
        
        # Now save it to mem0
        mem0_response = mem0_client.add(
            messages=[{"role": "assistant", "content": generated_code}],
            user_id=user_id,
            metadata={"type": "code", "app": app_name, "userId": user_id},
            output_format="v1.1"
        )
        
        # Return the actual generated code in the message
        return {
            "status": "saved", 
            "details": mem0_response, 
            "message": generated_code  # THIS is the key - return the actual code
        }
        
    except Exception as e:
        print(f"[ERROR] Exception with generate_code: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": f"Failed to generate code: {str(e)}"}
# ------------------------------- LLM AGENT -----------------------------------
memory_agent = LlmAgent(
    name="healthcare_assistant",
    model=model,
    description="""You are a cyber-aware code assistant using Mem0 in the background. Always generate secure, clean, and efficient code. 
    Follow modern cybersecurity best practices. Prevent common vulnerabilities (e.g., XSS, SQLi, buffer overflows). 
    Comment on any security-critical logic. Never output unsafe or deprecated code.
    Use the following tools for this:
    1.) Save user_information with the save_user_info helper function, and store it for later use and make sure to always call on this dependent on what the user wants.
    2.) Retrieve user information using the retrieve_user_info helper function in order to get past code or information about the specific product so that you can have a clearer response
    when answering the prompt.
    3.) Whenever asked to generate code, do as such and use generate_code helper function to save the code. Always return code snippets wrapped in Markdown-style triple backticks (```) with the correct language for highlighting. For example:
```
def my_function():
    return True
```
    """,
    instruction=SYSTEM_PROMPT,
    tools=[save_user_info, retrieve_user_info, delete_user_info, generate_code],
)

# ---------------------------- SESSION & RUNNER -------------------------------
session_service = InMemorySessionService()

# async def process_query_async(messages, user_id: str):
#     current_user_id_var.set(user_id)
#     thread_local.user_id = user_id

#     session_id = f"session_{uuid.uuid4().hex[:8]}"
#     print(f"[DEBUG] Processing query for user_id: {user_id}")

#     # Create chat session
#     await session_service.create_session(
#         app_name=app_name,
#         user_id=user_id,
#         session_id=session_id,
#     )

#     runner = Runner(agent=memory_agent, app_name=app_name, session_service=session_service)

#     # Normalise input
#     if isinstance(messages, types.Content):
#         new_message = messages
#     elif isinstance(messages, list) and messages:
#         latest = messages[-1]
#         new_message = types.Content(
#             role="user" if latest.get("sentByUser", False) else "model",
#             parts=[types.Part(text=latest["text"])],
#         )
#     elif isinstance(messages, str):
#         new_message = types.Content(role="user", parts=[types.Part(text=messages)])
#     else:
#         raise ValueError("No valid messages provided.")

#     # final_response = None
#     async for chunk in runner.run_async(
#         user_id=user_id,
#         session_id=session_id,
#         new_message=new_message,
#     ):
#         print(f"[DEBUG] Chunk received: {chunk}")
#         # if chunk.is_final_response() and chunk.content and chunk.content.parts:
#         #     final_response = chunk.content.parts[0].text

#         final_response = ""

#         if chunk.is_final_response() and chunk.content and chunk.content.parts:
#             for part in chunk.content.parts:
#                 if part.text:
#                     final_response += part.text + "\n"
#                 elif part.function_response:
#                     tool_msg = part.function_response.response.get("message")
#                     if tool_msg:
#                         final_response += tool_msg + "\n"


#     return final_response, session_id, request_memory_results.get(user_id, [])

async def process_query_async(messages, user_id: str):
    current_user_id_var.set(user_id)
    thread_local.user_id = user_id

    session_id = f"session_{uuid.uuid4().hex[:8]}"
    print(f"[DEBUG] Processing query for user_id: {user_id}")

    # Create chat session
    await session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id,
    )

    runner = Runner(agent=memory_agent, app_name=app_name, session_service=session_service)

    # Normalise input
    if isinstance(messages, types.Content):
        new_message = messages
    elif isinstance(messages, list) and messages:
        latest = messages[-1]
        new_message = types.Content(
            role="user" if latest.get("sentByUser", False) else "model",
            parts=[types.Part(text=latest["text"])],
        )
    elif isinstance(messages, str):
        new_message = types.Content(role="user", parts=[types.Part(text=messages)])
    else:
        raise ValueError("No valid messages provided.")

    final_response = ""
    all_chunks = []

    async for chunk in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=new_message,
    ):
        print(f"[DEBUG] Chunk received: {chunk}")
        all_chunks.append(chunk)
        
        # Collect all content from the chunk
        if chunk.content and chunk.content.parts:
            for part in chunk.content.parts:
                if part.text:
                    print(f"[DEBUG] Adding text part: {part.text}")
                    final_response += part.text
                elif hasattr(part, 'function_response') and part.function_response:
                    tool_response = part.function_response.response
                    print(f"[DEBUG] Function response: {tool_response}")
                    if isinstance(tool_response, dict):
                        # Get the message field which contains the generated code
                        tool_msg = tool_response.get("message", "")
                        if tool_msg:
                            print(f"[DEBUG] Adding tool message: {tool_msg}")
                            final_response += "\n" + tool_msg

    print(f"[DEBUG] FINAL RESPONSE TO SEND: {final_response}")
    print(f"[DEBUG] Length of final response: {len(final_response)}")
    
    return final_response, session_id, request_memory_results.get(user_id, [])

# ------------------------------- FLASK API -----------------------------------
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True, allow_headers="*", methods=["GET", "POST", "OPTIONS"])

# @app.route("/query", methods=["POST"])
# def handle_query():
#     data = request.json
#     if not data:
#         return jsonify({"status": "error", "message": "No JSON data provided"}), 400

#     query    = data.get("query")
#     messages = data.get("messages")
#     user_id  = data.get("user_id")

#     if not user_id or (not messages and not query):
#         return jsonify({"status": "error", "message": "Missing messages or user_id"}), 400

#     loop = asyncio.new_event_loop()
#     asyncio.set_event_loop(loop)
#     try:
#         result, session_id, memories = loop.run_until_complete(
#             process_query_async(messages or query, user_id)
#         )
#         response_text = result or "I'm here to help you with your memories."
#         return jsonify({
#             "status": "success",
#             "result_return": response_text,
#             "session_id": session_id,
#             "user_id": user_id,
#             "memories": memories,
#         })
#     finally:
#         loop.close()

@app.route("/query", methods=["POST"])
def handle_query():
    data = request.json
    if not data:
        return jsonify({"status": "error", "message": "No JSON data provided"}), 400

    query    = data.get("query")
    messages = data.get("messages")
    user_id  = data.get("user_id")

    if not user_id or (not messages and not query):
        return jsonify({"status": "error", "message": "Missing messages or user_id"}), 400

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result, session_id, memories = loop.run_until_complete(
            process_query_async(messages or query, user_id)
        )
        response_text = result or "I'm here to help you with your memories."
        
        print(f"[DEBUG] Response text being sent to frontend: {response_text}")
        print(f"[DEBUG] Response length: {len(response_text)}")
        
        response_json = {
            "status": "success",
            "result_return": response_text,
            "session_id": session_id,
            "user_id": user_id,
            "memories": memories,
        }
        
        print(f"[DEBUG] Full JSON response: {response_json}")
        
        return jsonify(response_json)
    finally:
        loop.close()

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"status": "error", "message": "No file uploaded"}), 400

    file    = request.files["file"]
    user_id = request.form.get("user_id")
    if not file or not user_id:
        return jsonify({"status": "error", "message": "File and user_id are required"}), 400

    filename     = secure_filename(file.filename)
    upload_dir   = os.path.join("uploads", user_id)
    os.makedirs(upload_dir, exist_ok=True)

    saved_name = f"{uuid.uuid4().hex}_{filename}"
    file_path  = os.path.join(upload_dir, saved_name)
    file.save(file_path)

    NGROK_URL  = "https://ed58f759da7e.ngrok-free.app"
    public_url = f"{NGROK_URL}/uploads/{user_id}/{saved_name}"

    prompt_text = f"I have uploaded an image here: {public_url}. Please describe this image."

    gemini_message = Content(role="user", parts=[Part(text=prompt_text)])

    mem0_client.add(
        messages=[{"role": "user", "content": f"Uploaded an image: {filename} (URL: {public_url})"}],
        user_id=user_id,
        metadata={"type": "file_upload", "filename": filename, "upload_path": file_path},
        output_format="v1.1"
    )

    summary, session_id, _ = asyncio.run(process_query_async(gemini_message, user_id))
    print("File '{filename}' uploaded and analyzed.")
    return jsonify({
        "status": "success",
        "message": f"File '{filename}' uploaded and analyzed.",
        "summary": summary,
        "local_path": file_path,
        "url": public_url,
    })

@app.route("/uploads/<user_id>/<filename>")
def serve_uploaded_file(user_id, filename):
    return send_from_directory(os.path.join("uploads", user_id), filename)


memory_cache = {}

@app.route("/api/ai/generate", methods=["POST"])
def novel_ai_generate():
    try:
        data = request.json
        if not data:
            return jsonify({"status": "error", "error": "No data was given"}), 500

        query = data.get("query")

        if not query:
            return jsonify({"status": "error", "error": "No query was given"}), 400

        # no need to use mem0, can use gemini api directly
        response = novel_client.models.generate_content(
            model=model,
            contents=query,
            config=types.GenerateContentConfig(
                system_instruction="You are a direct text editor. When asked to improve, fix, or modify text, return ONLY the improved text without explanations, options, or additional commentary. Be concise and direct. If asked to fix grammar in 'Hello my name is Aarnav', return only 'Hello, my name is Aarnav.' Do not provide multiple options or explanations.",
                thinking_config=types.ThinkingConfig(thinking_budget=0) # we are broke, so thinking is disabled for now
            )
        )

        if not response:
            return jsonify({"status": "error", "error": "There was an error in our model, please try again"})

        return jsonify({"status": "success", "message": response.text})

    except Exception as error:
        print(f"[ERROR] in /api/ai/generate: {error}")
        return jsonify({"status": "error", "error": str(error)}), 500

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy", "service": "memory_assistant", "version": "1.1"})

@app.route("/code", methods=["POST"])
def code_generate():
    try:
        data = request.json
        if not data or "query" not in data or "user_id" not in data:
            return jsonify({"status": "error", "error": "Missing 'query' or 'user_id'"}), 400

        result = generate_code(data["query"], user_id=data["user_id"])
        return jsonify(result), 200 if result["status"] == "saved" else 500

    except Exception as error:
        print(f"[ERROR] in /code: {error}")
        return jsonify({"status": "error", "error": str(error)}), 500


@app.route("/user/<user_id>/memories", methods=["GET"])
def get_user_memories(user_id):
    try:
        results = mem0_client.get_all(user_id=user_id)
        memories = [m.get("memory", str(m)) for m in results] if results else []
        return jsonify({"status": "success", "memories": memories, "count": len(memories)})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# --------------------------- MAIN ENTRY POINT --------------------------------
if __name__ == "__main__":
    for var in ["GOOGLE_API_KEY", "MEMO_API_KEY"]:
        if not os.getenv(var):
            print(f"Warning: missing env var {var}")

    print("Starting Memory Assistant API server on http://0.0.0.0:5000 …")
    app.run(debug=True, host="0.0.0.0", port=5000)
