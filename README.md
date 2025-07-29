# 🤖 NLW Agents API

Uma plataforma completa de **perguntas e respostas com IA integrada**, construída com **FastAPI** e **React**. Permite a criação de salas de discussão com respostas automáticas geradas por IA e suporte a upload de áudio para transcrição automática.

![App Preview](https://img.shields.io/badge/Status-Funcionando-brightgreen)
![Tech Stack](https://img.shields.io/badge/Stack-React%20%2B%20FastAPI%20%2B%20MongoDB-blue)

## 🌟 Características Principais

- **Interface Web Moderna**: Frontend React com Tailwind CSS responsivo
- **API RESTful Completa**: Backend FastAPI com documentação automática
- **Banco de Dados**: MongoDB Atlas para persistência de dados
- **IA Integrada**: Sistema de respostas contextuais inteligentes
- **Upload de Áudio**: Suporte para transcrição de arquivos de áudio
- **Tempo Real**: Interface de chat responsiva e intuitiva

## 🛠️ Tecnologias Utilizadas

### Frontend
- **React 18** - Interface de usuário moderna
- **Tailwind CSS** - Framework CSS utilitário
- **Axios** - Cliente HTTP para requisições
- **React Scripts** - Ferramentas de build e desenvolvimento

### Backend
- **FastAPI** - Framework web Python moderno e rápido
- **Motor** - Driver MongoDB assíncrono
- **Pydantic** - Validação de dados com tipos Python
- **Uvicorn** - Servidor ASGI de alta performance
- **Python-multipart** - Suporte para upload de arquivos

### Banco de Dados
- **MongoDB Atlas** - Banco de dados NoSQL na nuvem
- **Motor/PyMongo** - Drivers Python para MongoDB

## 🚀 Funcionalidades

### ✅ Implementadas
- 🏠 **Gestão de Salas**: Criar, listar e selecionar salas de discussão
- 💬 **Sistema Q&A**: Interface de chat para perguntas e respostas
- 🤖 **IA Contextual**: Respostas inteligentes baseadas no contexto
- 🎤 **Upload de Áudio**: Suporte para arquivos .webm, .wav, .mp3
- 📱 **Design Responsivo**: Interface adaptável para todos os dispositivos
- ⚡ **Tempo Real**: Atualizações automáticas de perguntas e respostas

### 🔄 Em Desenvolvimento
- 🎯 **IA Avançada**: Integração com modelos de linguagem modernos
- 🎵 **Transcrição Real**: Implementação completa do Whisper OpenAI
- 👤 **Autenticação**: Sistema de usuários e permissões
- 📊 **Analytics**: Estatísticas de uso e engajamento

## 📋 Pré-requisitos

- **Python 3.11+**
- **Node.js 16+**
- **Yarn** (recomendado)
- **MongoDB Atlas** (ou instância local)

## ⚙️ Instalação e Configuração

### 1. Clone o Repositório
```bash
git clone <repository-url>
cd nlw-agents-api
```

### 2. Configure o Backend
```bash
cd backend

# Instale as dependências
pip install -r requirements.txt

# Configure as variáveis de ambiente
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

### 3. Configure o Frontend
```bash
cd frontend

# Instale as dependências
yarn install

# Configure as variáveis de ambiente
cp .env.example .env
# Edite o arquivo .env com a URL do backend
```

### 4. Execute a Aplicação

#### Usando Supervisor (Recomendado)
```bash
# Inicie todos os serviços
sudo supervisorctl restart all

# Verifique o status
sudo supervisorctl status
```

#### Execução Manual
```bash
# Terminal 1 - Backend
cd backend
uvicorn server:app --host 0.0.0.0 --port 8001 --reload

# Terminal 2 - Frontend
cd frontend
yarn start
```

## 🌐 Estrutura da API

### Endpoints Principais

#### Salas
- `GET /api/` - Status da API
- `GET /api/rooms` - Lista todas as salas
- `POST /api/rooms` - Cria uma nova sala

#### Perguntas e Respostas
- `GET /api/rooms/{room_id}/questions` - Lista perguntas da sala
- `POST /api/rooms/{room_id}/questions` - Cria nova pergunta
- `POST /api/rooms/{room_id}/audio` - Upload de áudio para transcrição

### Exemplo de Payloads

#### Criar Sala
```json
{
  "name": "Tecnologia e IA",
  "description": "Discussões sobre tecnologia e inteligência artificial"
}
```

#### Criar Pergunta
```json
{
  "content": "O que é inteligência artificial?"
}
```

## 📊 Estrutura de Dados

### Sala (Room)
```json
{
  "id": "uuid-string",
  "name": "Nome da Sala",
  "description": "Descrição da sala",
  "created_at": "2025-01-28T10:30:00Z",
  "question_count": 5
}
```

### Pergunta (Question)
```json
{
  "id": "uuid-string",
  "room_id": "uuid-string",
  "content": "Conteúdo da pergunta",
  "created_at": "2025-01-28T10:30:00Z",
  "answer": "Resposta da IA"
}
```

## 🔧 Configuração do Ambiente

### Variáveis de Ambiente

#### Backend (.env)
```env
MONGO_URL=mongodb+srv://user:password@cluster.mongodb.net/database
```

#### Frontend (.env)
```env
REACT_APP_BACKEND_URL=https://your-backend-url.com
DANGEROUSLY_DISABLE_HOST_CHECK=true
```

## 🚦 Monitoramento e Logs

### Verificar Status dos Serviços
```bash
sudo supervisorctl status
```

### Visualizar Logs
```bash
# Backend
tail -f /var/log/supervisor/backend.out.log
tail -f /var/log/supervisor/backend.err.log

# Frontend
tail -f /var/log/supervisor/frontend.out.log
tail -f /var/log/supervisor/frontend.err.log
```

## 🎨 Interface do Usuário

A aplicação possui uma interface moderna e intuitiva:

- **Painel Lateral**: Lista de salas disponíveis
- **Área Principal**: Chat de perguntas e respostas
- **Formulários**: Criação de salas e envio de perguntas
- **Upload de Áudio**: Área para envio de arquivos de áudio
- **Design Responsivo**: Funciona em desktop, tablet e mobile

## 🔍 Recursos da IA

O sistema atual utiliza um **AI Service** com respostas contextuais que:

- Reconhece saudações e responde apropriadamente
- Identifica perguntas sobre tecnologia e programação
- Fornece respostas sobre IA e Machine Learning
- Adapta-se ao contexto da pergunta
- Oferece fallbacks inteligentes para casos gerais

## 🚀 Deploy e Produção

### Considerações para Produção

1. **Segurança**
   - Remover `DANGEROUSLY_DISABLE_HOST_CHECK=true`
   - Configurar CORS adequadamente
   - Implementar autenticação/autorização

2. **Performance**
   - Usar proxy reverso (Nginx)
   - Implementar cache (Redis)
   - Otimizar queries do MongoDB

3. **Monitoramento**
   - Logs estruturados
   - Métricas de performance
   - Alertas automáticos

## 🐛 Solução de Problemas

### Problemas Comuns

**Frontend não carrega (Invalid Host header)**
```bash
# Adicione ao .env do frontend:
DANGEROUSLY_DISABLE_HOST_CHECK=true

# Reinicie o frontend
sudo supervisorctl restart frontend
```

**Backend não conecta ao MongoDB**
```bash
# Verifique a URL do MongoDB no .env
# Verifique os logs do backend
tail -f /var/log/supervisor/backend.err.log
```

**Dependências não instaladas**
```bash
# Backend
cd backend && pip install -r requirements.txt

# Frontend
cd frontend && yarn install
```

## 📈 Próximos Passos

- [ ] Integração com OpenAI GPT ou Claude
- [ ] Implementação real do Whisper para transcrição
- [ ] Sistema de autenticação com JWT
- [ ] Temas personalizáveis na interface
- [ ] Export de conversas para PDF/JSON
- [ ] API de analytics e métricas
- [ ] Notificações em tempo real
- [ ] Suporte a múltiplos idiomas

## 📜 Licença

Este projeto é open-source sob a licença MIT.

## 👨‍💻 Autor

**Jenifer Gonçalves da Silva**

---

⭐ **Se este projeto foi útil, considere dar uma estrela no repositório!**

