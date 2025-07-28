# 📋 Guia dos Requirements - NLW Agents API

## 📁 Arquivos de Dependências Criados

### 1. `/app/backend/requirements.txt` ⭐ **PRINCIPAL**
```bash
# Arquivo principal com todas as dependências organizadas
# Use este para desenvolvimento e produção completa
pip install -r requirements.txt
```

### 2. `/app/requirements-detailed.txt` 📚 **DOCUMENTADO**
```bash
# Arquivo com comentários explicativos para cada dependência
# Útil para entender o que cada package faz
```

### 3. `/app/requirements-minimal.txt` ⚡ **DEPLOY RÁPIDO**
```bash
# Versão minimalista sem AI/Whisper
# Para deploy mais rápido se não usar funcionalidades de IA
pip install -r requirements-minimal.txt
```

## 🏗️ Dependências por Categoria

### **Web Framework (FastAPI)**
- `fastapi==0.104.1` - Framework web moderno
- `uvicorn[standard]==0.24.0` - Servidor ASGI
- `python-multipart==0.0.6` - Upload de arquivos

### **Database (MongoDB)**
- `motor==3.3.2` - Driver MongoDB assíncrono
- `pymongo==4.6.0` - Driver MongoDB oficial

### **Validação de Dados**
- `pydantic==2.5.0` - Validação e serialização

### **Inteligência Artificial**
- `transformers==4.36.0` - Modelos Hugging Face
- `torch==2.1.0` - PyTorch para ML
- `tokenizers==0.15.0` - Tokenizadores NLP
- `openai-whisper==20231117` - Transcrição de áudio

### **Processamento de Áudio**
- `librosa==0.10.1` - Análise de áudio
- `soundfile==0.12.1` - I/O de arquivos de áudio
- `ffmpeg-python==0.2.0` - Interface FFmpeg

### **Segurança & Utilidades**
- `certifi==2023.11.17` - Certificados SSL
- `python-dotenv==1.0.0` - Variáveis de ambiente

## 🚀 Comandos de Instalação

### **Desenvolvimento Local:**
```bash
cd backend
pip install -r requirements.txt
```

### **Deploy Render (Automático):**
```yaml
# No render.yaml já está configurado:
buildCommand: |
  cd backend
  pip install -r requirements.txt
```

### **Deploy Manual:**
```bash
# Clone e instale
git clone seu-repositorio
cd projeto/backend
pip install -r requirements.txt
uvicorn server:app --host 0.0.0.0 --port 8001
```

## 🧪 Testar Instalação

```bash
cd backend
python -c "
import fastapi, uvicorn, motor, pymongo, pydantic
import transformers, torch, whisper, librosa, certifi
print('✅ Todas as dependências instaladas!')
"
```

## 📊 Tamanhos Aproximados

- **Completo (requirements.txt):** ~2.5GB (com PyTorch/Whisper)
- **Minimal (requirements-minimal.txt):** ~100MB (sem AI)

## ⚠️ Notas Importantes

1. **PyTorch é pesado** (~1.5GB) - necessário para Whisper
2. **Whisper models** são baixados automaticamente na primeira execução
3. **FFmpeg** pode precisar ser instalado no sistema (já incluído no Render)
4. **Certifi** resolve problemas SSL com MongoDB Atlas

## 🎯 Para Produção no Render

O arquivo `requirements.txt` principal já está **perfeitamente configurado** para o Render e inclui todas as dependências necessárias para:

✅ FastAPI Backend  
✅ MongoDB Atlas  
✅ Transcrição de Áudio (Whisper)  
✅ Processamento de IA  
✅ Upload de arquivos  
✅ Conexões SSL seguras  

**🚀 Pronto para deploy!**