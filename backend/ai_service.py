import asyncio
import logging
import random
import requests
import json
from typing import Optional
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.models_loaded = False
        self.hf_model = None
        self.hf_tokenizer = None
        self.hf_generator = None
        
    async def initialize_models(self):
        """Initialize Hugging Face models asynchronously"""
        if self.models_loaded:
            return
            
        try:
            logger.info("Loading Hugging Face DistilGPT-2 model...")
            
            # Use DistilGPT-2 - lightweight and fast
            model_name = "distilgpt2"
            
            # Load model and tokenizer
            self.hf_tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.hf_model = AutoModelForCausalLM.from_pretrained(model_name)
            
            # Set padding token
            if self.hf_tokenizer.pad_token is None:
                self.hf_tokenizer.pad_token = self.hf_tokenizer.eos_token
            
            # Create text generation pipeline
            self.hf_generator = pipeline(
                "text-generation",
                model=self.hf_model,
                tokenizer=self.hf_tokenizer,
                device=-1,  # Use CPU (more compatible with Render)
                do_sample=True,
                temperature=0.7,
                max_length=150,
                pad_token_id=self.hf_tokenizer.eos_token_id
            )
            
            self.models_loaded = True
            logger.info("✅ Hugging Face model loaded successfully!")
            
        except Exception as e:
            logger.error(f"❌ Error loading Hugging Face model: {e}")
            logger.info("🔄 Falling back to contextual responses")
            self.models_loaded = False
        
    async def generate_response(self, question: str, max_length: int = 100) -> str:
        """Generate AI response for a given question"""
        # Try HuggingFace model first
        if not self.models_loaded:
            await self.initialize_models()
        
        if self.models_loaded and self.hf_generator:
            try:
                return await self._generate_hf_response(question)
            except Exception as e:
                logger.error(f"HF model error: {e}")
                # Fall back to contextual responses
                
        # Use contextual responses as fallback
        return self._get_contextual_response(question)
    
    async def _generate_hf_response(self, question: str) -> str:
        """Generate response using Hugging Face model"""
        try:
            # Create a conversational prompt
            prompt = f"Pergunta: {question}\nResposta:"
            
            # Generate response
            response = self.hf_generator(
                prompt,
                max_length=len(prompt.split()) + 50,
                num_return_sequences=1,
                temperature=0.7,
                do_sample=True,
                truncation=True
            )
            
            # Extract the generated text
            generated_text = response[0]['generated_text']
            
            # Remove the prompt and get only the answer
            answer = generated_text.replace(prompt, "").strip()
            
            # Clean up the response
            if answer:
                # Remove incomplete sentences at the end
                sentences = answer.split('.')
                if len(sentences) > 1 and len(sentences[-1]) < 10:
                    answer = '.'.join(sentences[:-1]) + '.'
                
                # Limit length
                if len(answer) > 200:
                    answer = answer[:200] + "..."
                
                return answer if answer else self._get_contextual_response(question)
            else:
                return self._get_contextual_response(question)
                
        except Exception as e:
            logger.error(f"Error in HF response generation: {e}")
            return self._get_contextual_response(question)
        
    def _get_contextual_response(self, question: str) -> str:
        """Get contextual responses based on question content (fallback)"""
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