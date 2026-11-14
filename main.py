import os
import logging
from database import (
    init_database,
    get_messages,
    get_sessions,
    delete_messages,
    save_exchange
)
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator
from openai import OpenAI
from rag import answer_with_rag, collection

def get_ai_response(question, messages):
    request_messages = messages[-6:] + [
    {"role": "user", "content": question}
    ]

    response = client.chat.completions.create(
        model = "openrouter/free",
        messages = request_messages
    )
    answer = response.choices[0].message.content
    return answer


app = FastAPI()
init_database()
logging.basicConfig(
    level = logging.INFO,
    format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"]
)

class ChatRequest(BaseModel):
    session_id: str = Field(min_length=1)
    question: str = Field(min_length=1)

    @field_validator("session_id", "question", mode="before")
    @classmethod
    def validate_input(cls, value):
        if isinstance(value, str):
            return value.strip()
        return value      

class DocRequest(BaseModel):
    question: str = Field(min_length=1)     
        
class UserMessage(BaseModel):
    name: str
    message: str

@app.get("/")
def root():
    return {"message": "My first FastAPI server"}

@app.get("/hello")
def hello(name: str):
    return {"message": f"안녕하세요, {name}님!"}

@app.post("/message")
def receive_message(data: UserMessage):
    return {"reply": f"{data.name}님, {data.message} 메시지를 받았습니다."}

@app.post("/ask")
def ask_ai(data: ChatRequest):
    # 1. 데이터베이스에서 이전 대화 불러오기
    messages = get_messages(data.session_id)

    try:
        # 2. AI에게 질문 전달
        answer = get_ai_response(data.question, messages)

    except Exception:
        logger.exception("OpenRouter 요청 실패")
        raise HTTPException(
            status_code=502,
            detail="AI 서비스 요청에 실패했습니다."
        )

    # 3. 성공한 경우에만 질문과 답변 저장
    save_exchange(data.session_id, data.question, answer)
    logger.info("대화 저장 완료 session_id = %s", data.session_id)

    return {"answer": answer}

@app.post("/ask-doc")
def ask_doc(data: DocRequest):
    try:
        answer = answer_with_rag(data.question, collection)
    
    except Exception:
        logger.exception("RAG 요청 실패")
        raise HTTPException(
            status_code=502,
            detail="문서 질의에 실패했습니다."
        )
    return {"answer": answer}

@app.delete("/sessions/{session_id}")
def delete_session(session_id:str):
    if session_id not in get_sessions():
        raise HTTPException(
            status_code=404,
            detail="세션을 찾을 수 없습니다."
            )
        
    delete_messages(session_id)

    return {"message": "해당 세션 삭제 성공"}

@app.get("/sessions")
def list_sessions():
    return {"sessions": get_sessions()}


