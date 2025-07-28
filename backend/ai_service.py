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
            # Try to load transformers if available
            try:
                from transformers import pipeline
                import torch
                
                logger.info("Loading lightweight text generation model...")
                
                # Try DistilGPT-2 first (very lightweight)
                self.text_generator = pipeline(
                    "text-generation",
                    model="distilgpt2",
                    device=-1,  # Force CPU usage
                    torch_dtype=torch.float32 if torch.cuda.is_available() else None
                )
                logger.info("DistilGPT-2 model loaded successfully")
                
            except Exception as e:
                logger.warning(f"Failed to load local models: {str(e)}")
                self.text_generator = None
            
        except ImportError:
            logger.warning("Transformers not available, using API fallbacks only")
            self.text_generator = None
            
        self.models_loaded = True
        logger.info("AI models initialization completed")
        
    async def generate_response(self, question: str, max_length: int = 100) -> str:
        """Generate AI response for a given question"""
        if not self.models_loaded:
            await self.initialize_models()
        
        # First try local model if available
        if self.text_generator:
            try:
                # Create a simple prompt
                prompt = f"Q: {question}\nA:"
                
                # Generate response
                result = self.text_generator(
                    prompt,
                    max_length=len(prompt.split()) + 25,
                    num_return_sequences=1,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=50256,
                    eos_token_id=50256
                )
                
                generated_text = result[0]['generated_text']
                # Extract just the answer part
                if "A:" in generated_text:
                    response = generated_text.split("A:")[-1].strip()
                    if response and len(response) > 5:
                        # Clean up the response
                        response = response.split('\n')[0].strip()
                        return response[:150] if response else self._get_contextual_response(question)
                        
            except Exception as e:
                logger.error(f"Error generating response with local model: {str(e)}")
        
        # Fallback to Hugging Face Inference API (free tier)
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
            "microsoft/DialoGPT-small",
            "gpt2",
            "facebook/blenderbot-400M-distill"
        ]
        
        for model_name in models_to_try:
            try:
                api_url = f"https://api-inference.huggingface.co/models/{model_name}"
                
                payload = {
                    "inputs": question,
                    "parameters": {
                        "max_length": 100,
                        "temperature": 0.8,
                        "do_sample": True,
                        "top_p": 0.9
                    }
                }
                
                response = requests.post(
                    api_url,
                    headers={"Content-Type": "application/json"},
                    json=payload,
                    timeout=15
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if isinstance(result, list) and len(result) > 0:
                        generated_text = result[0].get('generated_text', '').strip()
                        if generated_text and len(generated_text) > 10:
                            # Clean the response
                            clean_response = generated_text.replace(question, '').strip()
                            return clean_response[:150] if clean_response else generated_text[:150]
                    elif isinstance(result, dict) and 'generated_text' in result:
                        generated_text = result['generated_text'].strip()
                        if generated_text and len(generated_text) > 10:
                            return generated_text[:150]
                            
                logger.info(f"Model {model_name} response not suitable, trying next...")
                await asyncio.sleep(2)  # Rate limiting
                
            except Exception as e:
                logger.error(f"Error with model {model_name}: {str(e)}")
                await asyncio.sleep(1)
                continue
        
        raise Exception("All Hugging Face models failed")
        
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
        
        # Default intelligent responses
        return random.choice([
            "Interessante perspectiva! Esse é um tópico que sempre gera boas discussões.",
            "Essa é uma questão relevante. Há várias formas de abordar esse assunto.",
            "Obrigado por compartilhar isso! É sempre enriquecedor trocar ideias.",
            "Vou fazer o meu melhor para dar uma resposta útil e completa.",
            "Que pergunta instigante! Me faz refletir sobre várias possibilidades.",
            "Esse é um ponto importante que merece uma resposta cuidadosa."
        ])
        
    async def transcribe_audio(self, audio_data: bytes, audio_format: str = "webm") -> str:
        """Transcribe audio using SpeechRecognition (lightweight alternative to Whisper)"""
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix=f".{audio_format}", delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            try:
                # Try to convert to WAV format if needed
                audio_file_path = temp_file_path
                
                if audio_format.lower() != 'wav':
                    try:
                        # Try to use pydub if available
                        try:
                            from pydub import AudioSegment
                            wav_path = temp_file_path.replace(f'.{audio_format}', '.wav')
                            audio = AudioSegment.from_file(temp_file_path)
                            audio.export(wav_path, format="wav")
                            audio_file_path = wav_path
                        except ImportError:
                            logger.warning("pydub not available, trying with original format")
                            audio_file_path = temp_file_path
                    except Exception as e:
                        logger.warning(f"Audio conversion failed: {e}, using original file")
                        audio_file_path = temp_file_path
                
                # Use speech_recognition
                try:
                    with sr.AudioFile(audio_file_path) as source:
                        # Adjust for ambient noise
                        self.speech_recognizer.adjust_for_ambient_noise(source, duration=0.5)
                        audio_data = self.speech_recognizer.record(source)
                except Exception as e:
                    logger.error(f"Error reading audio file: {e}")
                    return "Não consegui ler o arquivo de áudio. Verifique o formato e tente novamente."
                
                # Try different recognition services
                recognition_attempts = [
                    ("Google (PT-BR)", lambda: self.speech_recognizer.recognize_google(audio_data, language='pt-BR')),
                    ("Google (EN)", lambda: self.speech_recognizer.recognize_google(audio_data, language='en-US')),
                ]
                
                for service_name, recognition_func in recognition_attempts:
                    try:
                        text = recognition_func()
                        if text and text.strip():
                            logger.info(f"Successfully transcribed using {service_name}: {text[:50]}...")
                            return text.strip()
                    except sr.UnknownValueError:
                        logger.warning(f"{service_name}: Could not understand audio")
                        continue
                    except sr.RequestError as e:
                        logger.warning(f"{service_name}: Service error - {e}")
                        continue
                    except Exception as e:
                        logger.warning(f"{service_name}: Unexpected error - {e}")
                        continue
                
                # If all recognition attempts failed
                return "Não consegui entender o áudio claramente. Tente falar mais devagar e com clareza, ou digite sua pergunta."
                
            finally:
                # Clean up temporary files
                for path in [temp_file_path, temp_file_path.replace(f'.{audio_format}', '.wav')]:
                    if os.path.exists(path):
                        try:
                            os.unlink(path)
                        except Exception as e:
                            logger.warning(f"Could not delete temp file {path}: {e}")
                    
        except Exception as e:
            logger.error(f"Error transcribing audio: {str(e)}")
            return "Desculpe, ocorreu um erro ao processar o áudio. Tente novamente ou digite sua pergunta diretamente."

# Global AI service instance
ai_service = AIService()