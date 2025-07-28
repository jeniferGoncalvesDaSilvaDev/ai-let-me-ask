from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import os
import uuid
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import json
import certifi

# Import AI service
import sys
sys.path.append('/app/backend')
from ai_service import ai_service

# Pydantic models
class RoomCreate(BaseModel):
    name: str
    description: str

class Room(BaseModel):
    id: str
    name: str
    description: str
    created_at: datetime
    question_count: int = 0

class QuestionCreate(BaseModel):
    content: str

class Question(BaseModel):
    id: str
    room_id: str
    content: str
    created_at: datetime
    answer: Optional[str] = None

class Answer(BaseModel):
    id: str
    question_id: str
    content: str
    created_at: datetime

# FastAPI app
app = FastAPI(title="NLW Agents API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
client = AsyncIOMotorClient(MONGO_URL, tlsCAFile=certifi.where())
db = client["ai-let-me-ask"]
rooms_collection = db.rooms
questions_collection = db.questions
answers_collection = db.answers

# Helper function to convert ObjectId to string
def serialize_doc(doc):
    if doc is None:
        return None
    if isinstance(doc, list):
        return [serialize_doc(item) for item in doc]
    if isinstance(doc, dict):
        for key, value in doc.items():
            if isinstance(value, ObjectId):
                doc[key] = str(value)
            elif isinstance(value, dict):
                doc[key] = serialize_doc(value)
            elif isinstance(value, list):
                doc[key] = serialize_doc(value)
    return doc

# Routes
@app.get("/api/")
async def health_check():
    """Verifica se a API está online"""
    return {"status": "online", "message": "NLW Agents API is running"}

@app.get("/api/rooms", response_model=List[Room])
async def get_rooms():
    """Lista todas as salas cadastradas"""
    try:
        rooms = []
        async for room in rooms_collection.find():
            # Count questions for this room
            question_count = await questions_collection.count_documents({"room_id": room["id"]})
            
            room_data = {
                "id": room["id"],
                "name": room["name"],
                "description": room["description"],
                "created_at": room["created_at"],
                "question_count": question_count
            }
            rooms.append(room_data)
        
        return rooms
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching rooms: {str(e)}")

@app.post("/api/rooms", response_model=Room)
async def create_room(room: RoomCreate):
    """Cria uma nova sala"""
    try:
        room_id = str(uuid.uuid4())
        room_data = {
            "id": room_id,
            "name": room.name,
            "description": room.description,
            "created_at": datetime.now(),
        }
        
        await rooms_collection.insert_one(room_data)
        
        return Room(
            id=room_id,
            name=room.name,
            description=room.description,
            created_at=room_data["created_at"],
            question_count=0
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating room: {str(e)}")

@app.post("/api/rooms/{room_id}/questions", response_model=Question)
async def create_question(room_id: str, question: QuestionCreate):
    """Cria uma nova pergunta em uma sala e gera resposta automática com IA"""
    try:
        # Verify room exists
        room = await rooms_collection.find_one({"id": room_id})
        if not room:
            raise HTTPException(status_code=404, detail="Room not found")
        
        question_id = str(uuid.uuid4())
        question_data = {
            "id": question_id,
            "room_id": room_id,
            "content": question.content,
            "created_at": datetime.now(),
            "answer": None
        }
        
        await questions_collection.insert_one(question_data)
        
        # Generate AI response
        print(f"Generating AI response for question: {question.content}")
        ai_response = await ai_service.generate_response(question.content)
        print(f"AI response generated: {ai_response}")
        
        # Create answer
        answer_id = str(uuid.uuid4())
        answer_data = {
            "id": answer_id,
            "question_id": question_id,
            "content": ai_response,
            "created_at": datetime.now()
        }
        
        await answers_collection.insert_one(answer_data)
        
        # Update question with answer
        await questions_collection.update_one(
            {"id": question_id},
            {"$set": {"answer": ai_response}}
        )
        
        return Question(
            id=question_id,
            room_id=room_id,
            content=question.content,
            created_at=question_data["created_at"],
            answer=ai_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating question: {str(e)}")

@app.get("/api/rooms/{room_id}/questions", response_model=List[Question])
async def get_room_questions(room_id: str):
    """Lista perguntas e respostas de uma sala específica"""
    try:
        # Verify room exists
        room = await rooms_collection.find_one({"id": room_id})
        if not room:
            raise HTTPException(status_code=404, detail="Room not found")
        
        questions = []
        async for question in questions_collection.find({"room_id": room_id}).sort("created_at", -1):
            questions.append(Question(
                id=question["id"],
                room_id=question["room_id"],
                content=question["content"],
                created_at=question["created_at"],
                answer=question.get("answer")
            ))
        
        return questions
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching questions: {str(e)}")

@app.post("/api/rooms/{room_id}/audio")
async def upload_audio(room_id: str, audio: UploadFile = File(...)):
    """Envia um arquivo de áudio para transcrição automática com Whisper e geração de resposta via IA"""
    try:
        # Verify room exists
        room = await rooms_collection.find_one({"id": room_id})
        if not room:
            raise HTTPException(status_code=404, detail="Room not found")
        
        # Validate audio file
        if not audio.filename.endswith(('.webm', '.wav', '.mp3')):
            raise HTTPException(status_code=400, detail="Invalid audio format. Supported: .webm, .wav, .mp3")
        
        # Read audio data
        audio_data = await audio.read()
        
        # Extract format from filename
        audio_format = audio.filename.split('.')[-1]
        
        # Transcribe audio using Whisper
        print(f"Transcribing audio file: {audio.filename}")
        transcribed_text = await ai_service.transcribe_audio(audio_data, audio_format)
        print(f"Transcription result: {transcribed_text}")
        
        # Create question from transcription
        question_id = str(uuid.uuid4())
        question_data = {
            "id": question_id,
            "room_id": room_id,
            "content": transcribed_text,
            "created_at": datetime.now(),
            "answer": None
        }
        
        await questions_collection.insert_one(question_data)
        
        # Generate AI response
        print(f"Generating AI response for audio transcription: {transcribed_text}")
        ai_response = await ai_service.generate_response(transcribed_text)
        print(f"AI response generated: {ai_response}")
        
        # Create answer
        answer_id = str(uuid.uuid4())
        answer_data = {
            "id": answer_id,
            "question_id": question_id,
            "content": ai_response,
            "created_at": datetime.now()
        }
        
        await answers_collection.insert_one(answer_data)
        
        # Update question with answer
        await questions_collection.update_one(
            {"id": question_id},
            {"$set": {"answer": ai_response}}
        )
        
        return {
            "transcribed_text": transcribed_text,
            "question": {
                "id": question_id,
                "room_id": room_id,
                "content": transcribed_text,
                "created_at": question_data["created_at"],
                "answer": ai_response
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing audio: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)