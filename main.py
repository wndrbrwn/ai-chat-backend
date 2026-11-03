import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator
from openai import OpenAI

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
chat_sessions = {}

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
    messages = chat_sessions.get(data.session_id, [])
    
    try:
        answer = get_ai_response(data.question, messages)
    
    except Exception as e:
        print("OpenRouter 오류:", e)
        raise HTTPException(
        status_code=502,
        detail="AI 서비스 요청에 실패했습니다."
        )    
    
    messages.append({"role": "user", "content": data.question})
    messages.append({"role": "assistant", "content": answer})

    chat_sessions[data.session_id] = messages
    
    return {"answer": answer}

@app.delete("/sessions/{session_id}")
def delete_session(session_id:str):
    if session_id not in chat_sessions:
        raise HTTPException(
            status_code=404,
            detail="세션을 찾을 수 없습니다."
            )
        
    del chat_sessions[session_id]
    return {"message": "해당 세션 삭제 성공"}

@app.get("/sessions")
def get_session():
    return {"sessions": chat_sessions}


