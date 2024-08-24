from fastapi import FastAPI
from main import echo_handler

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/echo")
async def echo(message: str):
    return await echo_handler(message)


# class Message:
#     def __init__(self, message_id: int, chat_id: int, text: str):
#         self.text = text