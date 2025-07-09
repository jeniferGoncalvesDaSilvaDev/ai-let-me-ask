---

# 🤖 NLW Agents API

Uma API construída com **FastAPI** que permite a criação de salas de discussão com **respostas automáticas geradas por IA**. Além disso, suporta **transcrição de áudio com Whisper** e conversão da fala em perguntas automaticamente respondidas por modelos da Hugging Face.

---

## 🧠 Tecnologias Utilizadas

- [FastAPI](https://fastapi.tiangolo.com/)
- [Transformers - Hugging Face](https://huggingface.co/transformers/)
  - Modelos: `microsoft/DialoGPT-medium`, fallback: `gpt2`
- [Whisper (OpenAI)](https://github.com/openai/whisper)
- [Torch](https://pytorch.org/)
- [Pydub](https://github.com/jiaaro/pydub)
- [Uvicorn](https://www.uvicorn.org/)
- [CORS Middleware](https://fastapi.tiangolo.com/tutorial/cors/)

---

## 🚀 Funcionalidades

- ✅ Criação e listagem de salas de perguntas
- ✅ Geração de respostas com IA usando modelos de linguagem natural
- ✅ Transcrição de áudio com Whisper
- ✅ Criação automática de perguntas a partir de áudio enviado
- ✅ Armazenamento temporário em memória com dados de exemplo

---

## 📁 Estrutura das Salas

Cada sala contém:
- `id`: identificador único
- `name`: nome da sala
- `description`: descrição do tema
- `createdAt`: data de criação
- `questionsCount`: quantidade de perguntas associadas

---

## 📌 Endpoints Disponíveis

### `GET /`
Retorna status da API.

### `GET /rooms`
Lista todas as salas cadastradas.

### `POST /rooms`
Cria uma nova sala.

#### Payload:
```json
{
  "name": "Nome da Sala",
  "description": "Descrição da Sala"
}

POST /rooms/{room_id}/questions

Adiciona uma nova pergunta em uma sala e gera a resposta automaticamente.

Payload:

{
  "question": "O que é inteligência artificial?"
}

GET /rooms/{room_id}/questions

Lista todas as perguntas e respostas de uma sala.

POST /rooms/{room_id}/audio

Recebe um arquivo de áudio (.webm, .wav, etc), realiza a transcrição com Whisper e gera uma resposta automática.


---

📦 Exemplo de Dados Pré-Carregados

O sistema inicializa com 3 salas e perguntas/respostas automáticas para teste:

Tecnologia e Inovação

Programação e Desenvolvimento

Carreira em Tech



---

🧠 IA e Geração de Texto

O modelo padrão utilizado é o:

microsoft/DialoGPT-medium

Se ocorrer erro no carregamento, o sistema realiza fallback para:

gpt2

Ambos são acessados via Hugging Face pipeline.


---

🗣️ Transcrição de Voz com Whisper

A transcrição de voz utiliza o modelo base do Whisper. O áudio é convertido automaticamente para .wav caso necessário.


---

⚙️ Como Executar o Projeto

1. Clone o repositório:



git clone https://github.com/seu-usuario/nlw-agents-api.git
cd nlw-agents-api

2. Instale as dependências:



pip install -r requirements.txt

3. Execute o servidor:



uvicorn main:app --host 0.0.0.0 --port 3333


---

🌐 CORS

CORS ativado para:

http://localhost:5173

http://localhost:3000



---

📌 Observações

Este projeto é apenas um MVP / protótipo. O armazenamento é feito em memória.

Para produção, recomenda-se:

Banco de dados (PostgreSQL, MongoDB, etc.)

Camada de autenticação/autorização

Logging robusto

Interface web com React, Vue ou outro framework




---

📜 Licença

Este projeto é open-source 


---

Feito com 💻 por Jenifer Gonçalves da Silva

---

