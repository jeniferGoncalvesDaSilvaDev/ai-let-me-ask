import asyncio
import logging
import random
import requests
import json
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.models_loaded = True  # Skip model loading for now
        
    async def initialize_models(self):
        """Initialize AI models asynchronously"""
        if self.models_loaded:
            return
            
        logger.info("AI Service initialized with contextual responses")
        self.models_loaded = True
        
    async def generate_response(self, question: str, max_length: int = 100) -> str:
        """Generate AI response for a given question"""
        if not self.models_loaded:
            await self.initialize_models()
        
        # Use contextual responses (reliable fallback)
        return self._get_contextual_response(question)
        
    def _get_contextual_response(self, question: str) -> str:
        """Get contextual responses based on question content"""
        question_lower = question.lower()
        
        # Greeting responses
        if any(word in question_lower for word in ['olá', 'oi', 'hello', 'hi', 'bom dia', 'boa tarde', 'boa noite']):
            return random.choice([
                "Olá! Como posso ajudá-lo hoje?",
                "Oi! É um prazer conversar com você.",
                "Olá! Estou aqui para responder suas perguntas.",
                "Bom dia! Em que posso ser útil?",
                "Olá! Pronto para uma boa conversa!"
            ])
        
        # Name/identity responses
        if any(word in question_lower for word in ['nome', 'name', 'quem é você', 'who are you', 'se apresente']):
            return random.choice([
                "Sou uma IA assistente criada para responder suas perguntas no NLW Agents.",
                "Meu nome é NLW Assistant, estou aqui para ajudar com suas dúvidas!",
                "Sou um assistente virtual inteligente, pronto para conversar sobre qualquer assunto!"
            ])
        
        # How are you responses
        if any(word in question_lower for word in ['como você está', 'how are you', 'tudo bem', 'como vai']):
            return random.choice([
                "Estou funcionando perfeitamente e pronto para ajudar! E você, como está?",
                "Tudo ótimo por aqui! Sempre animado para uma boa conversa.",
                "Estou muito bem, obrigado por perguntar! Como posso ajudá-lo hoje?"
            ])
        
        # Technology responses
        if any(word in question_lower for word in ['tecnologia', 'programação', 'código', 'technology', 'programming', 'software']):
            return random.choice([
                "Tecnologia é fascinante! É uma área em constante evolução que molda nosso futuro.",
                "Programação é uma das habilidades mais valiosas hoje. Sobre qual linguagem ou conceito você gostaria de saber?",
                "A tecnologia está transformando o mundo de maneiras incríveis. Que aspecto específico te interessa?"
            ])
        
        # AI/ML responses  
        if any(word in question_lower for word in ['inteligência artificial', 'machine learning', 'ia', 'ai', 'deep learning']):
            return random.choice([
                "A Inteligência Artificial está revolucionando como interagimos com a tecnologia! É um campo empolgante.",
                "Machine Learning permite que computadores aprendam com dados - é realmente fascinante!",
                "IA é um campo amplo que vai desde chatbots como eu até carros autônomos e diagnósticos médicos."
            ])
        
        # Career/work responses
        if any(word in question_lower for word in ['carreira', 'trabalho', 'emprego', 'profissão', 'career']):
            return random.choice([
                "Carreiras em tecnologia oferecem muitas oportunidades! Há diversas áreas para explorar.",
                "O mercado de trabalho em tech está sempre aquecido. Que área te interessa mais?",
                "Desenvolver habilidades técnicas é um ótimo investimento para o futuro profissional."
            ])
        
        # Help responses
        if any(word in question_lower for word in ['ajuda', 'help', 'socorro', 'dúvida', 'não sei']):
            return random.choice([
                "Claro! Estou aqui para ajudar. Pode me contar mais sobre o que você precisa saber?",
                "Posso ajudá-lo com qualquer pergunta que você tiver. Vamos resolver isso juntos!",
                "Estou pronto para esclarecer suas dúvidas! Qual é o assunto?"
            ])
        
        # What/how questions
        if any(word in question_lower for word in ['o que é', 'what is', 'como', 'how', 'por que', 'why']):
            return random.choice([
                "Essa é uma pergunta interessante! Baseado no contexto, é um tópico que vale a pena explorar em detalhes.",
                "Boa pergunta! Esse assunto tem várias facetas interessantes que podemos discutir.",
                "Excelente questão! Deixe-me pensar na melhor forma de explicar isso para você."
            ])
        
        # Learning/education responses
        if any(word in question_lower for word in ['aprender', 'estudar', 'curso', 'learn', 'study']):
            return random.choice([
                "Aprender é sempre uma excelente escolha! Sobre qual área você gostaria de se aprofundar?",
                "Estudar é fundamental para o crescimento pessoal e profissional. Que tipo de conhecimento você busca?",
                "Há muitos recursos interessantes para aprender hoje em dia. Em que posso orientá-lo?"
            ])
        
        # General knowledge responses
        if any(word in question_lower for word in ['explicar', 'explain', 'definir', 'define', 'conceito']):
            return random.choice([
                "Claro! Adoraria explicar isso para você. É importante compreender bem os conceitos.",
                "Vou fazer o meu melhor para explicar de forma clara e didática.",
                "Definições e conceitos são fundamentais para o entendimento. Vamos esclarecer isso!"
            ])
        
        # Default intelligent responses
        return random.choice([
            "Interessante perspectiva! Esse é um tópico que sempre gera boas discussões.",
            "Essa é uma questão relevante. Há várias formas de abordar esse assunto.",
            "Obrigado por compartilhar isso! É sempre enriquecedor trocar ideias.",
            "Vou fazer o meu melhor para dar uma resposta útil e completa.",
            "Que pergunta instigante! Me faz refletir sobre várias possibilidades.",
            "Esse é um ponto importante que merece uma resposta cuidadosa.",
            "Baseado no que você perguntou, posso dizer que é um assunto complexo e interessante.",
            "Essa questão toca em aspectos importantes que vale a pena explorar."
        ])
        
    async def transcribe_audio(self, audio_data: bytes, audio_format: str = "webm") -> str:
        """Transcribe audio - simplified version"""
        # For now, return a helpful message since audio processing is complex
        return "Funcionalidade de áudio temporariamente indisponível. Por favor, digite sua pergunta diretamente."

# Global AI service instance
ai_service = AIService()