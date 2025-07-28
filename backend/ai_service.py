import asyncio
import logging
import random
import requests
import json
import io
import tempfile
import os
import speech_recognition as sr
from typing import Optional
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import torch

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.text_generator = None
        self.speech_recognizer = sr.Recognizer()
        self.models_loaded = False
        
    async def initialize_models(self):
        """Initialize AI models asynchronously"""
        if self.models_loaded:
            return
            
        logger.info("Initializing lightweight AI models...")
        
        try:
            # Try to load a lightweight model for text generation
            logger.info("Loading lightweight text generation model...")
            
            # First try: DistilGPT-2 (very lightweight)
            try:
                self.text_generator = pipeline(
                    "text-generation",
                    model="distilgpt2",
                    tokenizer="distilgpt2",
                    device=-1,  # Force CPU usage
                    torch_dtype=torch.float32
                )
                logger.info("DistilGPT-2 model loaded successfully")
            except Exception as e:
                logger.warning(f"Failed to load DistilGPT-2: {str(e)}")
                
                # Fallback: Standard GPT-2 small
                try:
                    self.text_generator = pipeline(
                        "text-generation",
                        model="gpt2",
                        tokenizer="gpt2", 
                        device=-1,  # Force CPU usage
                        torch_dtype=torch.float32
                    )
                    logger.info("GPT-2 model loaded successfully")
                except Exception as e:
                    logger.error(f"Failed to load GPT-2: {str(e)}")
                    self.text_generator = None
            
        except Exception as e:
            logger.error(f"Failed to load AI models: {str(e)}")
            self.text_generator = None
            
        self.models_loaded = True
        logger.info("AI models initialization completed")
        
    async def generate_response(self, question: str, max_length: int = 100) -> str:
        """Generate AI response for a given question"""
        if not self.models_loaded:
            await self.initialize_models()
        
        # First try local model
        if self.text_generator:
            try:
                # Create a proper prompt for conversation
                prompt = f"Usuário: {question}\nAssistente:"
                
                # Generate response
                result = self.text_generator(
                    prompt,
                    max_length=len(prompt.split()) + 30,
                    num_return_sequences=1,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=50256
                )
                
                generated_text = result[0]['generated_text']
                # Extract just the assistant's response
                response = generated_text.split("Assistente:")[-1].strip()
                
                if response and len(response) > 10:
                    return response[:200]  # Limit response length
                    
            except Exception as e:
                logger.error(f"Error generating response with local model: {str(e)}")
        
        # Fallback to Hugging Face Inference API (Llama or other free model)
        try:
            return await self._generate_with_huggingface_api(question)
        except Exception as e:
            logger.error(f"Error with Hugging Face API: {str(e)}")
        
        # Final fallback to contextual responses
        return self._get_contextual_response(question)
        
    async def _generate_with_huggingface_api(self, question: str) -> str:
        """Use Hugging Face Inference API as fallback (free tier)"""
        
        # Try different free models
        models_to_try = [
            "microsoft/DialoGPT-medium",
            "microsoft/DialoGPT-small", 
            "gpt2",
            "facebook/blenderbot-400M-distill"
        ]
        
        for model_name in models_to_try:
            try:
                api_url = f"https://api-inference.huggingface.co/models/{model_name}"
                
                payload = {
                    "inputs": f"Pergunta: {question}\nResposta:",
                    "parameters": {
                        "max_length": 150,
                        "temperature": 0.7,
                        "return_full_text": False
                    }
                }
                
                response = requests.post(
                    api_url,
                    headers={"Content-Type": "application/json"},
                    json=payload,
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if isinstance(result, list) and len(result) > 0:
                        generated_text = result[0].get('generated_text', '').strip()
                        if generated_text and len(generated_text) > 5:
                            return generated_text[:200]
                            
                logger.info(f"Model {model_name} not available, trying next...")
                await asyncio.sleep(1)  # Rate limiting
                
            except Exception as e:
                logger.error(f"Error with model {model_name}: {str(e)}")
                continue
        
        raise Exception("All Hugging Face models failed")
        
    def _get_contextual_response(self, question: str) -> str:
        """Get contextual responses based on question content (fallback)"""
        question_lower = question.lower()
        
        # Greeting responses
        if any(word in question_lower for word in ['olá', 'oi', 'hello', 'hi', 'bom dia', 'boa tarde']):
            return random.choice([
                "Olá! Como posso ajudá-lo hoje?",
                "Oi! É um prazer conversar com você.",
                "Olá! Estou aqui para responder suas perguntas.",
                "Bom dia! Em que posso ser útil?"
            ])
        
        # Name/identity responses
        if any(word in question_lower for word in ['nome', 'name', 'quem é você', 'who are you']):
            return random.choice([
                "Sou uma IA assistente criada para responder suas perguntas.",
                "Meu nome é NLW Assistant, estou aqui para ajudar!",
                "Sou um assistente virtual do NLW Agents, pronto para conversar!"
            ])
        
        # Technology responses
        if any(word in question_lower for word in ['tecnologia', 'programação', 'código', 'technology', 'programming']):
            return random.choice([
                "Adoro falar sobre tecnologia! É uma área em constante evolução.",
                "Programação é uma habilidade fundamental nos dias de hoje. Sobre qual linguagem você gostaria de saber?",
                "A tecnologia está transformando o mundo. Que aspecto específico te interessa?"
            ])
        
        # AI/ML responses  
        if any(word in question_lower for word in ['inteligência artificial', 'machine learning', 'ia', 'ai']):
            return random.choice([
                "A Inteligência Artificial está revolucionando como interagimos com a tecnologia!",
                "Machine Learning é fascinante - permite que computadores aprendam com dados.",
                "IA é um campo amplo que inclui desde chatbots até carros autônomos."
            ])
        
        # Help responses
        if any(word in question_lower for word in ['ajuda', 'help', 'socorro', 'dúvida']):
            return random.choice([
                "Claro! Estou aqui para ajudar. O que você precisa saber?",
                "Posso ajudá-lo com qualquer pergunta que você tiver.",
                "Estou pronto para esclarecer suas dúvidas!"
            ])
        
        # Default intelligent responses
        return random.choice([
            "Interessante pergunta! Baseado no que sei, é um tópico que merece reflexão.",
            "Essa é uma boa questão. Vou tentar dar uma resposta útil baseada no contexto.",
            "Obrigado por perguntar! É sempre bom poder compartilhar conhecimento.",
            "Vou fazer o meu melhor para responder de forma clara e objetiva.",
            "Essa pergunta me faz pensar em várias possibilidades interessantes."
        ])
        
    async def transcribe_audio(self, audio_data: bytes, audio_format: str = "webm") -> str:
        """Transcribe audio using SpeechRecognition (lightweight alternative to Whisper)"""
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix=f".{audio_format}", delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            try:
                # Convert to WAV if necessary
                if audio_format.lower() != 'wav':
                    wav_path = temp_file_path.replace(f'.{audio_format}', '.wav')
                    try:
                        from pydub import AudioSegment
                        audio = AudioSegment.from_file(temp_file_path)
                        audio.export(wav_path, format="wav")
                        audio_file_path = wav_path
                    except ImportError:
                        logger.warning("pydub not available, using original file")
                        audio_file_path = temp_file_path
                else:
                    audio_file_path = temp_file_path
                
                # Use speech_recognition with Google Speech Recognition (free)
                with sr.AudioFile(audio_file_path) as source:
                    audio_data = self.speech_recognizer.record(source)
                
                try:
                    # Try Google (free, but requires internet)
                    text = self.speech_recognizer.recognize_google(audio_data, language='pt-BR')
                    if text.strip():
                        return text.strip()
                except sr.RequestError:
                    logger.warning("Google Speech Recognition not available")
                
                try:
                    # Fallback to offline recognition if available
                    text = self.speech_recognizer.recognize_sphinx(audio_data)
                    if text.strip():
                        return text.strip()
                except (sr.RequestError, ImportError):
                    logger.warning("Offline speech recognition not available")
                
                return "Não consegui processar o áudio. Tente enviar novamente ou digite sua pergunta."
                
            finally:
                # Clean up temporary files
                for path in [temp_file_path, temp_file_path.replace(f'.{audio_format}', '.wav')]:
                    if os.path.exists(path):
                        try:
                            os.unlink(path)
                        except:
                            pass
                    
        except Exception as e:
            logger.error(f"Error transcribing audio: {str(e)}")
            return "Desculpe, ocorreu um erro ao processar o áudio. Tente novamente ou digite sua pergunta."

# Global AI service instance
ai_service = AIService()