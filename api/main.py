from typing import Union

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"response": "Hello from Lars'  first API! :)"}

@app.get("/chatbot")
def chatbot(user_input: str):
    return {"response": f"Hello from the LLama! This was the user prompt: {user_input}"}

