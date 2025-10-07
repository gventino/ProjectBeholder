from fastapi import FastAPI
from pydantic import BaseModel

# Crie uma instância do FastAPI
app = FastAPI()


# Defina um modelo de dados para a requisição
# Isso garante que a requisição terá um campo "message" do tipo string
class Message(BaseModel):
    message: str


@app.post("/echo")
async def echo_message(message: Message):
    """
    Este endpoint recebe uma mensagem no corpo da requisição e a retorna.
    """
    return {"echo": message.message}


@app.get("/")
async def root():
    return {"message": "Bem-vindo à API de Echo! Use o endpoint /echo para testar."}
