from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from decouple import config
import openai

# Custom Function Imports
from functions.database import store_messages, reset_messages
from functions.openai_requests import convert_audio_to_text, get_chat_response
from functions.text_to_speech import convert_text_to_speech

# Initiate App
app = FastAPI()

# CORS - Origins
origins = [
    "http://localhost",
    "http://localhost:3000",
]

# CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Check health
@app.get("/reset")
async def check_conversation():
    reset_messages()
    return {"message": "Conversation reset"}

@app.get("/")
async def check_health():
    return {"message": "Healthy"}

@app.get("/post-audio-get/")
async def get_audio():
    audio_input = open("voice.mp3", "rb")
    message_decoded = convert_audio_to_text(audio_input)

    if not message_decoded:
        raise HTTPException(status_code=400, detail="Failed to decode audio")

    chat_response = get_chat_response(message_decoded)

    if not chat_response:
        raise HTTPException(status_code=400, detail="Failed to get chat response")

    store_messages(message_decoded, chat_response)

    audio_output = convert_text_to_speech(chat_response)

    if not audio_output:
        raise HTTPException(status_code=400, detail="Failed to get Eleven Labs audio")

    def iterfile():
        yield audio_output

    return StreamingResponse(iterfile(), media_type="audio/mpeg")


