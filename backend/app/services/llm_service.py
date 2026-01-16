"""
LLM Service - Abstraction layer for different LLM providers
Supports both Gemini (free tier) and Ollama (local)
"""
import logging
from typing import Optional, Dict, Any
from app.utils.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    """
    Unified interface for LLM interactions
    Automatically switches between Gemini and Ollama based on configuration
    """
    
    def __init__(self):
        self.provider = settings.LLM_PROVIDER.lower()
        
        if self.provider == "gemini":
            self._init_gemini()
        elif self.provider == "ollama":
            self._init_ollama()
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")
    
    def _init_gemini(self):
        """Initialize Google Gemini"""
        try:
            import google.generativeai as genai
            
            if not settings.GEMINI_API_KEY:
                raise ValueError("GEMINI_API_KEY not set in environment")
            
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
            logger.info("Gemini Flash 2.0 initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {e}")
            raise
    
    def _init_ollama(self):
        """Initialize Ollama (local LLM)"""
        try:
            import ollama
            
            self.client = ollama.Client(host=settings.OLLAMA_BASE_URL)
            
            # Test connection
            self.client.list()
            
            self.model_name = settings.OLLAMA_MODEL
            logger.info(f"Ollama initialized with model: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Ollama: {e}")
            logger.error("Make sure Ollama is running: ollama serve")
            raise
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """
        Generate text from LLM
        
        Args:
            prompt: User prompt
            system_prompt: System instructions
            temperature: Randomness (0-1)
            max_tokens: Max response length
        
        Returns:
            Generated text
        """
        try:
            if self.provider == "gemini":
                return await self._generate_gemini(prompt, system_prompt, temperature, max_tokens)
            elif self.provider == "ollama":
                return await self._generate_ollama(prompt, system_prompt, temperature, max_tokens)
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return f"Error generating response: {str(e)}"
    
    async def _generate_gemini(
        self,
        prompt: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int
    ) -> str:
        """Generate using Gemini"""
        try:
            # Combine system prompt and user prompt
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            
            response = self.model.generate_content(
                full_prompt,
                generation_config={
                    'temperature': temperature,
                    'max_output_tokens': max_tokens,
                }
            )
            
            return response.text
        except Exception as e:
            logger.error(f"Gemini generation error: {e}")
            raise
    
    async def _generate_ollama(
        self,
        prompt: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int
    ) -> str:
        """Generate using Ollama"""
        try:
            messages = []
            
            if system_prompt:
                messages.append({
                    'role': 'system',
                    'content': system_prompt
                })
            
            messages.append({
                'role': 'user',
                'content': prompt
            })
            
            response = self.client.chat(
                model=self.model_name,
                messages=messages,
                options={
                    'temperature': temperature,
                    'num_predict': max_tokens,
                }
            )
            
            return response['message']['content']
        except Exception as e:
            logger.error(f"Ollama generation error: {e}")
            raise
    
    async def generate_structured(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        output_schema: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate structured output (JSON)
        
        Args:
            prompt: User prompt
            system_prompt: System instructions
            output_schema: Expected JSON schema
        
        Returns:
            Parsed JSON response
        """
        import json
        
        # Add JSON instruction to system prompt
        json_instruction = "\n\nYou must respond with valid JSON only. No explanations, no markdown, just JSON."
        enhanced_system = (system_prompt or "") + json_instruction
        
        if output_schema:
            enhanced_system += f"\n\nExpected JSON schema: {json.dumps(output_schema)}"
        
        response = await self.generate(prompt, enhanced_system, temperature=0.3)
        
        # Parse JSON response
        try:
            # Remove markdown code blocks if present
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            
            return json.loads(response.strip())
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Raw response: {response}")
            raise ValueError(f"LLM did not return valid JSON: {str(e)}")
