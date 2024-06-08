import os
import asyncio
import uuid
import traceback
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import redis.asyncio as redis
from dotenv import load_dotenv
from bolna.helpers.utils import store_file, load_file
from bolna.prompts import *
from bolna.helpers.logger_config import configure_logger
from bolna.models import *
from bolna.llms import LiteLLM
from bolna.agent_manager.assistant_manager import AssistantManager
from twilio.twiml.voice_response import VoiceResponse, Connect
from dotenv import load_dotenv
from fastapi.responses import PlainTextResponse


load_dotenv()
logger = configure_logger(__name__)

redis_pool = redis.ConnectionPool.from_url(os.getenv('REDIS_URL'), decode_responses=True)
redis_client = redis.Redis.from_pool(redis_pool)
active_websockets: List[WebSocket] = []

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "https://polished-needlessly-monkfish.ngrok-free.app", "http://192.168.167.1:38842"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


class CreateAgentPayload(BaseModel):
    agent_config: AgentModel
    agent_prompts: Optional[Dict[str, Dict[str, str]]]


@app.post("/agent")
async def create_agent(agent_data: CreateAgentPayload):
    agent_uuid = str(uuid.uuid4())
    data_for_db = agent_data.agent_config.model_dump()
    data_for_db["assistant_status"] = "seeding"
    agent_prompts = agent_data.agent_prompts
    logger.info(f'Data for DB {data_for_db}')

    if len(data_for_db['tasks']) > 0:
        logger.info("Setting up follow up tasks")
        for index, task in enumerate(data_for_db['tasks']):
            if task['task_type'] == "extraction":
                extraction_prompt_llm = os.getenv("EXTRACTION_PROMPT_GENERATION_MODEL")
                extraction_prompt_generation_llm = LiteLLM(model=extraction_prompt_llm, max_tokens=2000)
                extraction_prompt = await extraction_prompt_generation_llm.generate(
                    messages=[
                        {'role': 'system', 'content': EXTRACTION_PROMPT_GENERATION_PROMPT},
                        {'role': 'user', 'content': data_for_db["tasks"][index]['tools_config']["llm_agent"]['extraction_details']}
                    ])
                data_for_db["tasks"][index]["tools_config"]["llm_agent"]['extraction_json'] = extraction_prompt

    stored_prompt_file_path = f"{agent_uuid}/conversation_details.json"
    await asyncio.gather(
        redis_client.set(agent_uuid, json.dumps(data_for_db)),
        store_file(file_key=stored_prompt_file_path, file_data=agent_prompts, local=True)
    )

    return {"agent_id": agent_uuid, "state": "created"}


############################################################################################# 
# Websocket 
#############################################################################################
@app.websocket("/chat")
async def websocket_endpoint(websocket: WebSocket):
    logger.info("Attempting to connect to WebSocket")
    try:
        await websocket.accept()
        logger.info("WebSocket connection accepted")
    except Exception as e:
        logger.error(f"Error accepting WebSocket connection: {e}")
        return

    active_websockets.append(websocket)
    agent_config, context_data = None, None
    agent_config = load_file('./local_setup/agent_config.json', is_json=True)
    logger.info(f"Retrieved agent config: {agent_config}")

    assistant_manager = AssistantManager(agent_config, websocket)
    
    logger.info(f"Assistant Manager: {assistant_manager}")
    try:
        async for index, task_output in assistant_manager.run(local=True):
            logger.info(task_output)
    except WebSocketDisconnect:
        active_websockets.remove(websocket)
        logger.info("WebSocket disconnected")
    except Exception as e:
        traceback.print_exc()
        logger.error(f"Error in executing: {e}")
        await websocket.close(code=1011, reason="Internal server error")
        
        
@app.post('/call')
async def twilio_callback():
    try:
        response = VoiceResponse()

        connect = Connect()
        websocket_twilio_route = 'wss://polished-needlessly-monkfish.ngrok-free.app/chat'
        connect.stream(url=websocket_twilio_route)
        print(f"websocket connection done to {websocket_twilio_route}")
        response.append(connect)

        return PlainTextResponse(str(response), status_code=200, media_type='text/xml')

    except Exception as e:
        print(f"Exception occurred in twilio_callback: {e}")