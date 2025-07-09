import asyncio
import logging
from typing import Optional
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.dialog_model = None
        self.dialog_tokenizer = None
        self.gpt2_model = None
        self.gpt2_tokenizer = None
        self.dialog_pipeline = None
        self.gpt2_pipeline = None
        self.models_loaded = False
        
    async def initialize_models(self):
        """Initialize AI models asynchronously"""
        if self.models_loaded:
            return
            
        logger.info("Initializing AI models...")
        
        try:
            # Load DialoGPT-medium model
            logger.info("Loading DialoGPT-medium model...")
            self.dialog_tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
            self.dialog_model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")
            
            # Set padding token
            if self.dialog_tokenizer.pad_token is None:
                self.dialog_tokenizer.pad_token = self.dialog_tokenizer.eos_token
            
            logger.info("DialoGPT-medium model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load DialoGPT-medium: {str(e)}")
            self.dialog_model = None
            self.dialog_tokenizer = None
            
        try:
            # Load GPT-2 model as fallback
            logger.info("Loading GPT-2 model as fallback...")
            self.gpt2_tokenizer = AutoTokenizer.from_pretrained("gpt2")
            self.gpt2_model = AutoModelForCausalLM.from_pretrained("gpt2")
            
            # Set padding token
            if self.gpt2_tokenizer.pad_token is None:
                self.gpt2_tokenizer.pad_token = self.gpt2_tokenizer.eos_token
                
            logger.info("GPT-2 model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load GPT-2: {str(e)}")
            self.gpt2_model = None
            self.gpt2_tokenizer = None
            
        self.models_loaded = True
        logger.info("AI models initialization completed")
        
    async def generate_response(self, question: str, max_length: int = 150) -> str:
        """Generate AI response for a given question"""
        if not self.models_loaded:
            await self.initialize_models()
            
        # Try DialoGPT-medium first
        if self.dialog_model and self.dialog_tokenizer:
            try:
                response = await self._generate_dialog_response(question, max_length)
                if response:
                    return response
            except Exception as e:
                logger.error(f"DialoGPT-medium generation failed: {str(e)}")
                
        # Fallback to GPT-2
        if self.gpt2_model and self.gpt2_tokenizer:
            try:
                response = await self._generate_gpt2_response(question, max_length)
                if response:
                    return response
            except Exception as e:
                logger.error(f"GPT-2 generation failed: {str(e)}")
                
        # If all models fail, return fallback message
        return "Desculpe, não consigo processar sua pergunta no momento. Tente novamente mais tarde."
        
    async def _generate_dialog_response(self, question: str, max_length: int) -> Optional[str]:
        """Generate response using DialoGPT-medium"""
        try:
            # Tokenize input
            inputs = self.dialog_tokenizer.encode(question + self.dialog_tokenizer.eos_token, return_tensors="pt")
            
            # Generate response
            with torch.no_grad():
                outputs = self.dialog_model.generate(
                    inputs,
                    max_length=max_length,
                    num_return_sequences=1,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.dialog_tokenizer.pad_token_id,
                    eos_token_id=self.dialog_tokenizer.eos_token_id,
                    no_repeat_ngram_size=2
                )
            
            # Decode response
            response = self.dialog_tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Remove the input question from the response
            if question in response:
                response = response.replace(question, "").strip()
                
            # Clean up response
            response = self._clean_response(response)
            
            return response if response else None
            
        except Exception as e:
            logger.error(f"Error in DialoGPT generation: {str(e)}")
            return None
            
    async def _generate_gpt2_response(self, question: str, max_length: int) -> Optional[str]:
        """Generate response using GPT-2"""
        try:
            # Create a prompt for GPT-2
            prompt = f"Pergunta: {question}\nResposta:"
            
            # Tokenize input
            inputs = self.gpt2_tokenizer.encode(prompt, return_tensors="pt")
            
            # Generate response
            with torch.no_grad():
                outputs = self.gpt2_model.generate(
                    inputs,
                    max_length=len(inputs[0]) + 100,  # Add tokens for response
                    num_return_sequences=1,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.gpt2_tokenizer.pad_token_id,
                    eos_token_id=self.gpt2_tokenizer.eos_token_id,
                    no_repeat_ngram_size=2
                )
            
            # Decode response
            full_response = self.gpt2_tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract only the response part
            if "Resposta:" in full_response:
                response = full_response.split("Resposta:")[-1].strip()
            else:
                response = full_response.replace(prompt, "").strip()
                
            # Clean up response
            response = self._clean_response(response)
            
            return response if response else None
            
        except Exception as e:
            logger.error(f"Error in GPT-2 generation: {str(e)}")
            return None
            
    def _clean_response(self, response: str) -> str:
        """Clean and format the AI response"""
        if not response:
            return ""
            
        # Remove extra whitespace
        response = response.strip()
        
        # Remove incomplete sentences at the end
        sentences = response.split('.')
        if len(sentences) > 1 and sentences[-1] and not sentences[-1].endswith(('!', '?', '.')):
            response = '.'.join(sentences[:-1]) + '.'
            
        # Limit response length
        if len(response) > 300:
            response = response[:297] + "..."
            
        # Ensure minimum response length
        if len(response) < 10:
            return None
            
        return response

# Global AI service instance
ai_service = AIService()