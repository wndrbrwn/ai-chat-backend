import os
import logging
from database import (
    init_database,
    get_messages,
    get_sessions,
    delete_messages,
    save_exchange
)
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel, Field, field_validator
from openai import AsyncOpenAI
from rag import answer_with_rag, collection, index_document
from fastapi.responses import StreamingResponse

MAX_UPLOAD_BYTES = 1 * 1024 * 1024

async def get_ai_response(question, messages):
    request_messages = messages[-6:] + [
    {"role": "user", "content": question}
    ]

    response = await client.chat.completions.create(
        model = "openrouter/free",
        messages = request_messages
    )
    answer = response.choices[0].message.content
    return answer

async def stream_ai_response(session_id, question, messages):
    request_messages = messages[-6:] + [
        {"role": "user", "content": question}
    ]
    
    chunks = []
    
    try:
        stream = await client.chat.completions.create(
            model = "openrouter/free",
            messages = request_messages,
            stream = True
        )

        
        async for chunk in stream:
            if not chunk.choices:
                continue
            text = chunk.choices[0].delta.content
            if text:
                chunks.append(text)
                yield text
    
    except Exception:
        logger.exception("OpenRouter 요청 실패")
        yield "AI 서비스 요청에 실패했습니다."
        return

    answer = "".join(chunks)
    save_exchange(session_id, question, answer)

app = FastAPI()
init_database()
logging.basicConfig(
    level = logging.INFO,
    format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)
client = AsyncOpenAI(
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
async def ask_ai(data: ChatRequest):
    # 1. 데이터베이스에서 이전 대화 불러오기
    messages = get_messages(data.session_id)

    try:
        # 2. AI에게 질문 전달
        answer = await get_ai_response(data.question, messages)

    except Exception:
        logger.exception("OpenRouter 요청 실패")
        raise HTTPException(
            status_code = 502,
            detail = "AI 서비스 요청에 실패했습니다."
        )

    # 3. 성공한 경우에만 질문과 답변 저장
    save_exchange(data.session_id, data.question, answer)
    logger.info("대화 저장 완료 session_id = %s", data.session_id)

    return {"answer": answer}

@app.post("/ask-stream")
async def ask_stream(data: ChatRequest):
    messages = get_messages(data.session_id)
    return StreamingResponse(
        stream_ai_response(data.session_id, data.question, messages),
        media_type = "text/plain"
    )

@app.post("/ask-doc")
def ask_doc(data: DocRequest):
    try:
        result = answer_with_rag(data.question, collection)
    
    except Exception:
        logger.exception("RAG 요청 실패")
        raise HTTPException(
            status_code = 502,
            detail = "문서 질의에 실패했습니다."
        )
    return {"answer": result["answer"], "sources": result["sources"]}

@app.post("/documents")
def upload_document(file: UploadFile = File(...)):
    if not file.filename.endswith(".txt"):
        raise HTTPException(status_code = 400, detail = ".txt 파일만 업로드할 수 있습니다.")
    
    raw = file.file.read(MAX_UPLOAD_BYTES + 1)
    
    if len(raw) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code = 413, detail = "파일이 너무 큽니다. 최대 1MB까지 가능합니다.")

    try:
        text = raw.decode("utf-8")

    except UnicodeDecodeError:
        raise HTTPException(status_code = 400, detail = "UTF-8 텍스트 파일만 가능합니다.")

    if not text.strip():
        raise HTTPException(status_code = 400, detail = "빈 파일입니다.")

    try:
        count = index_document(file.filename, text, collection)

    except Exception:
        logger.exception("문서 색인 실패")
        raise HTTPException(status_code = 502, detail = "문서 색인에 실패했습니다.")

    return {"source": file.filename, "chunks": count}

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


