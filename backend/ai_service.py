import asyncio
import logging
import random
import whisper
import io
import tempfile
import os
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.whisper_model = None
        self.models_loaded = False
        
    async def initialize_models(self):
        """Initialize AI models asynchronously"""
        if self.models_loaded:
            return
            
        logger.info("Initializing AI models...")
        
        try:
            # Load Whisper model
            logger.info("Loading Whisper model...")
            self.whisper_model = whisper.load_model("base")
            logger.info("Whisper model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load Whisper: {str(e)}")
            self.whisper_model = None
            
        self.models_loaded = True
        logger.info("AI models initialization completed")
        
    async def generate_response(self, question: str, max_length: int = 150) -> str:
        """Generate AI response for a given question"""
        if not self.models_loaded:
            await self.initialize_models()
            
        # Simulate AI processing time
        await asyncio.sleep(0.5)
        
        # Simple rule-based responses for testing
        responses = self._get_contextual_responses(question)
        
        return random.choice(responses)
        
    def _get_contextual_responses(self, question: str) -> list:
        """Get contextual responses based on question content"""
        question_lower = question.lower()
        
        # Greeting responses
        if any(word in question_lower for word in ['olá', 'oi', 'hello', 'hi']):
            return [
                "Olá! Como posso ajudá-lo hoje?",
                "Oi! É um prazer conversar com você.",
                "Olá! Estou aqui para responder suas perguntas."
            ]
        
        # Name responses
        if any(word in question_lower for word in ['nome', 'name', 'quem é você']):
            return [
                "Sou uma IA assistente criada para responder suas perguntas.",
                "Meu nome é NLW Assistant, estou aqui para ajudar!",
                "Sou um assistente virtual do NLW Agents."
            ]
        
        # How are you responses
        if any(word in question_lower for word in ['como você está', 'how are you', 'tudo bem']):
            return [
                "Estou funcionando perfeitamente, obrigado por perguntar!",
                "Tudo ótimo! Pronto para ajudar você.",
                "Estou bem e animado para conversar!"
            ]
        
        # Help responses
        if any(word in question_lower for word in ['ajuda', 'help', 'socorro']):
            return [
                "Claro! Estou aqui para ajudar. O que você precisa?",
                "Posso ajudá-lo com qualquer pergunta que você tiver.",
                "Estou pronto para ajudar! Qual é sua dúvida?"
            ]
        
        # Technology responses
        if any(word in question_lower for word in ['tecnologia', 'programação', 'código', 'technology']):
            return [
                "Adoro falar sobre tecnologia! Posso ajudar com programação, IA e muito mais.",
                "Tecnologia é fascinante! Sobre qual área específica você gostaria de saber?",
                "Estou sempre atualizado com as últimas tendências tecnológicas."
            ]
        
        # Default responses
        return [
            "Interessante pergunta! Deixe-me pensar sobre isso.",
            "Essa é uma boa questão. Baseado no que sei, posso dizer que é um tópico complexo.",
            "Obrigado por perguntar! É sempre bom poder ajudar com informações.",
            "Vou fazer o meu melhor para responder sua pergunta de forma útil.",
            "Essa pergunta me faz refletir. Vou tentar dar uma resposta abrangente."
        ]
        
    async def transcribe_audio(self, audio_data: bytes, audio_format: str = "webm") -> str:
        """Transcribe audio using Whisper"""
        if not self.models_loaded:
            await self.initialize_models()
            
        if not self.whisper_model:
            return "Desculpe, não consigo processar áudio no momento."
            
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix=f".{audio_format}", delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            try:
                # Transcribe audio
                result = self.whisper_model.transcribe(temp_file_path)
                transcription = result["text"].strip()
                
                if not transcription:
                    return "Não consegui entender o áudio. Tente novamente."
                    
                return transcription
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            logger.error(f"Error transcribing audio: {str(e)}")
            return "Desculpe, ocorreu um erro ao processar o áudio."

# Global AI service instance
ai_service = AIService()