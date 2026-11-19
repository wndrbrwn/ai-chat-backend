# AI Chat Backend

FastAPI 기반의 AI 챗봇 백엔드 프로젝트입니다. OpenRouter API를 활용한 대화형 AI 응답, 실시간 스트리밍, 문서 기반 질의응답(RAG) 기능을 제공합니다.

SQLite로 대화 기록을 저장하고 ChromaDB를 이용해 문서 검색 기능을 구현했습니다.

## 기술 스택

| 구분 | 기술 |
|---|---|
| Language | Python 3.12 |
| Backend | FastAPI |
| Database | SQLite |
| Vector Database | ChromaDB |
| LLM API | OpenRouter |
| AI SDK | OpenAI Python SDK |
| Testing | pytest, FastAPI TestClient |
| Containerization | Docker, Docker Compose |

## 주요 기능

- **AI Chat:** OpenRouter API를 활용한 AI 대화 기능
- **Session Management:** Session ID를 기반으로 대화 기록 분리 및 관리
- **Conversation Context:** 최근 메시지 6개(사용자·AI 메시지 합산)를 AI 요청에 포함하여 대화 맥락 유지
- **Persistent Storage:** SQLite를 이용한 대화 기록 저장 및 서버 재시작 후 데이터 유지
- **Atomic Message Storage:** 하나의 데이터베이스 트랜잭션으로 사용자 메시지와 AI 응답 저장
- **Streaming Response:** LLM 응답을 생성되는 순서대로 클라이언트에 전달
- **RAG (Retrieval-Augmented Generation):** ChromaDB에서 관련 문서를 검색하고 검색 결과를 근거로 AI 답변 생성
- **Error Handling:** 입력 검증 및 AI 서비스 오류에 대한 HTTP 상태 코드 처리
- **Automated Testing:** pytest와 모의 객체를 활용한 API 및 데이터베이스 테스트

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | 서버 상태 확인 |
| GET | `/hello` | 인사말 반환 (학습용 예제) |
| POST | `/message` | 간단한 메시지 처리 (학습용 예제) |
| POST | `/ask` | 대화 맥락을 반영한 AI 답변 생성 |
| POST | `/ask-stream` | AI 응답을 스트리밍 방식으로 전달 |
| POST | `/ask-doc` | 문서 검색 결과를 기반으로 AI 답변 생성 |
| GET | `/sessions` | 저장된 대화 세션 목록 조회 |
| DELETE | `/sessions/{session_id}` | 특정 세션의 대화 기록 삭제 |

## 프로젝트 구조

```text
ai-chat-backend/
├── main.py
├── database.py
├── rag.py
├── embed_demo.py
├── chunk_demo.py
├── rag_demo.py
├── sample.txt
├── test_main.py
├── test_database.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .gitignore
└── README.md
```

- `main.py`: FastAPI 애플리케이션 및 API 엔드포인트
- `database.py`: SQLite 데이터베이스 및 대화 기록 관리
- `rag.py`: 문서 색인, 벡터 검색 및 RAG 답변 생성
- `embed_demo.py`: 텍스트 임베딩 실습
- `chunk_demo.py`: 문서 청킹 실습
- `rag_demo.py`: RAG 검색 및 답변 생성 실습
- `sample.txt`: RAG 테스트용 문서

SQLite 데이터베이스 파일, ChromaDB 저장 폴더 및 Python 가상환경은 로컬에서 생성되며 Git 버전 관리 대상에서 제외됩니다.

## 환경변수

| 변수 | 필수 여부 | 기본값 | 설명 |
|---|---|---|---|
| `OPENROUTER_API_KEY` | 필수 | 없음 | OpenRouter API 인증 키 |
| `DB_PATH` | 선택 | `chat_history.db` | SQLite 데이터베이스 파일 경로 |

## 실행 방법

### Docker Compose

Windows PowerShell 기준으로 작성했습니다.

1. 프로젝트 루트에 `.env` 파일을 생성합니다.

   ```env
   OPENROUTER_API_KEY=your_openrouter_api_key
   ```

2. Docker Compose를 실행합니다.

   ```powershell
   docker compose up --build -d
   ```

3. 최초 실행 시 RAG 대상 문서를 색인합니다.

   ```powershell
   docker compose exec app python rag.py
   ```

4. SQLite와 ChromaDB 데이터는 Docker Named Volume을 통해 컨테이너 외부에 보존되도록 구성합니다. 컨테이너를 종료하고 다시 생성해도 데이터가 유지됩니다.

   ```powershell
   docker compose down
   docker compose up -d
   ```

   데이터 볼륨까지 삭제하려면 `docker compose down -v`를 사용합니다. 이 명령은 저장된 데이터도 삭제하므로 주의해야 합니다.

### 로컬 실행

Windows PowerShell 기준입니다.

1. 가상환경을 생성하고 활성화합니다.

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

2. 의존성을 설치합니다.

   ```powershell
   python -m pip install -r requirements.txt
   ```

3. OpenRouter API 키를 환경변수로 설정합니다.

   ```powershell
   $env:OPENROUTER_API_KEY="your_openrouter_api_key"
   ```

4. FastAPI 서버를 실행합니다.

   ```powershell
   python -m uvicorn main:app --reload
   ```

### API 문서

브라우저에서 다음 주소로 접속합니다.

http://127.0.0.1:8000/docs

Swagger UI를 통해 API 엔드포인트를 확인하고 요청을 테스트할 수 있습니다.

## 테스트

pytest를 사용하여 API 엔드포인트와 데이터베이스 기능을 테스트합니다.

```powershell
python -m pytest -v
```

주요 테스트 항목:

- 세션별 대화 기록 분리 및 조회
- 메시지 저장, 수정 및 삭제
- 데이터베이스 트랜잭션 롤백
- AI 요청 성공 및 실패 상황
- 스트리밍 응답 및 오류 처리
- 문서 기반 질의응답 및 예외 처리

테스트에는 다음 기능을 활용합니다.

- **FastAPI TestClient:** 실제 서버를 별도로 실행하지 않고 API 엔드포인트 테스트
- **monkeypatch:** 외부 AI API 호출을 모의 함수로 대체
- **tmp_path:** 실제 데이터베이스와 분리된 임시 SQLite 데이터베이스 사용

테스트 중에는 실제 OpenRouter API를 호출하지 않으며, 실제 대화 기록 데이터베이스를 수정하지 않습니다.

## 데이터베이스 설계

### SQLite: `chat_messages`

| Column | Type | Description |
|---|---|---|
| message_id | INTEGER | 고유 메시지 ID |
| session_id | TEXT | 대화 세션 식별자 |
| role | TEXT | 메시지 발신자 (`user` 또는 `assistant`) |
| content | TEXT | 메시지 내용 |

각 메시지는 개별 행으로 저장하며 `session_id`를 기준으로 대화 기록을 조회합니다.

### ChromaDB

문서 내용을 청크 단위로 나누고 임베딩하여 벡터 형태로 저장합니다. 사용자 질문과 관련된 문서 청크를 검색한 후 검색 결과를 LLM에 전달합니다.

ChromaDB는 `PersistentClient`를 사용하며 Docker 환경에서는 Named Volume을 통해 저장 데이터를 보존합니다.

## 알려진 한계

- OpenRouter 무료 모델을 사용하므로 모델 가용성과 응답 품질이 달라질 수 있습니다.
- 세션은 클라이언트가 전달하는 Session ID를 기준으로 구분합니다.
- 사용자 인증 및 계정 시스템은 구현되어 있지 않습니다.
- `/ask-doc`은 세션과 연결되어 있지 않으며 대화 기록을 사용하거나 저장하지 않습니다.
- `/ask-stream`은 스트리밍 도중 오류가 발생하면 HTTP 상태 코드는 200으로 유지되고 응답 본문에 오류 안내 문구를 전달합니다.
- RAG 색인은 `python rag.py`를 통한 수동 실행 방식이며, 현재 대상 문서는 `sample.txt` 하나입니다.
- 현재 프로젝트는 로컬 개발 및 백엔드 학습을 중심으로 구성되어 있습니다.