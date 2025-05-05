from fastapi import FastAPI, Request, Header, Body, Form, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from agent.SalesGPT import SalesGPT
from agent.StageAnalyzerChain import StageAnalyzerChain
from agent.AgentConversationChain import AgentConversationChain
from agent.storage import upload_image_to_blob
from agent.Tools import save_image_relation
from langchain_openai import AzureChatOpenAI
from dotenv import load_dotenv
import os
import uuid 
import datetime
load_dotenv()

# Inicializa FastAPI
app = FastAPI()

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

# Instancia do LLM
llm = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    azure_deployment=os.getenv("DEPLOYMENT_NAME"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    model_name=os.getenv("DEPLOYMENT_NAME")
)

# Inicializa o agente
sales_agent = SalesGPT.from_llm(llm)
sales_agent.seed_agent()

# Modelo para entrada da mensagem
class MessageInput(BaseModel):
    message: str

@app.post("/newAgent")
def new_agent(user: str = Header(..., convert_underscores=False)):
    session_id = str(uuid.uuid4())  # Gera um GUID
    sales_agent.seed_agent()
    stage = sales_agent.determine_conversation_stage()
    answer = sales_agent.step(session_id)

    return {
        "sessionId": session_id,
        "user": user,
        "conversationStep": stage,
        "salesAnswer": answer,
        "datetime": str(datetime.datetime.now())
    }

@app.post("/conversationStep")
def conversation_step(
    message: str = Body(..., convert_underscores=False),
    user: str = Body(..., convert_underscores=False),
    session_id: str = Header(..., convert_underscores=False),
):
    # Aqui você pode logar ou salvar user se quiser usar por sessão
    print(f"Usuário {user} enviou: {message}")
    
    sales_agent.human_step(message, session_id)
    stage = sales_agent.determine_conversation_stage()
    answer = sales_agent.step(session_id)
    
    return {
        "user": user,
        "conversationStep": stage,
        "salesAnswer": answer,
        "datetime": str(datetime.datetime.now())
    }

@app.post("/upload-image")
async def upload_image(user: str = Body(..., convert_underscores=False),
                       session_id: str = Header(..., convert_underscores=False),
                       file: UploadFile = File(...)):
    # try:
        filename = f"{session_id}_{uuid.uuid4()}_{file.filename}"
        contents = await file.read()
        print(f"Arquivo recebido: {filename}")
        # Upload to Azure Blob
        image_url = upload_image_to_blob(contents, filename)
        print(f"Arquivo enviado para o Azure Blob: {image_url}")
        # Salva no banco
        save_image_relation(session_id, image_url)

        sales_agent.human_step(f"Endereço da imagem: {image_url}")
        stage = sales_agent.determine_conversation_stage()
        answer = sales_agent.step(session_id)
        

        return {
            "user": user,
            "conversationStep": stage,
            "salesAnswer": answer,
            "datetime": str(datetime.datetime.now())
    }
    
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=str(e))