"""LLM Service for AI Assistant Module

Wraps ctransformers to provide LLM inference capabilities.
Handles model loading, inference, and error handling.

Note: Uses ctransformers instead of llama-cpp-python for better Windows compatibility.
"""

import os
from typing import Optional, Dict, Any, List
from pathlib import Path


class LLMService:
    """Service for LLM model inference using llama-cpp-python"""
    
    def __init__(self, config_service):
        """Initialize LLM service
        
        Args:
            config_service: Configuration service instance (DI)
        """
        self.config = config_service
        self._model = None
        self._model_loaded = False
    
    def load_model(self) -> tuple[bool, Optional[str]]:
        """Load the GGUF model into memory
        
        Returns:
            Tuple of (success, error_message)
        """
        try:
            from ctransformers import AutoModelForCausalLM
            
            model_path = self.config.get("model_path")
            
            # Check if model file exists
            if not os.path.exists(model_path):
                return False, f"Model file not found: {model_path}"
            
            # Load model with configuration
            # Try without model_type first (auto-detect from filename)
            self._model = AutoModelForCausalLM.from_pretrained(
                model_path,
                model_type="qwen",  # qwen2.5-coder uses "qwen" type in ctransformers
                context_length=self.config.get("context_length", 4096),
                gpu_layers=self.config.get("n_gpu_layers", 0)
            )
            
            self._model_loaded = True
            return True, None
            
        except ImportError:
            return False, "ctransformers not installed. Run: pip install ctransformers"
        except Exception as e:
            return False, f"Error loading model: {str(e)}"
    
    def is_loaded(self) -> bool:
        """Check if model is loaded
        
        Returns:
            True if model is loaded and ready
        """
        return self._model_loaded and self._model is not None
    
    def generate(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stop: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Generate text from prompt
        
        Args:
            prompt: Input prompt for the model
            temperature: Sampling temperature (overrides config)
            max_tokens: Maximum tokens to generate (overrides config)
            stop: Stop sequences (optional)
            
        Returns:
            Dictionary with 'text', 'tokens_used', 'error' (if any)
        """
        if not self.is_loaded():
            return {
                "text": None,
                "tokens_used": 0,
                "error": "Model not loaded. Call load_model() first."
            }
        
        try:
            # Use provided values or fall back to config
            temp = temperature if temperature is not None else self.config.get("temperature", 0.1)
            max_tok = max_tokens if max_tokens is not None else self.config.get("max_tokens", 500)
            
            # Generate response (ctransformers API)
            text = self._model(
                prompt,
                temperature=temp,
                max_new_tokens=max_tok,
                stop=stop
            )
            
            # ctransformers doesn't return token counts, estimate from text
            # Rough estimate: ~4 characters per token
            estimated_tokens = len(prompt + text) // 4
            
            return {
                "text": text.strip(),
                "tokens_used": estimated_tokens,
                "error": None
            }
            
        except Exception as e:
            return {
                "text": None,
                "tokens_used": 0,
                "error": f"Generation error: {str(e)}"
            }
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information
        
        Returns:
            Dictionary with model details
        """
        model_path = self.config.get("model_path")
        
        info = {
            "loaded": self.is_loaded(),
            "model_path": model_path,
            "model_exists": os.path.exists(model_path),
            "model_size_mb": 0
        }
        
        # Get file size if exists
        if info["model_exists"]:
            size_bytes = os.path.getsize(model_path)
            info["model_size_mb"] = round(size_bytes / (1024 * 1024), 2)
        
        return info
    
    def unload_model(self) -> None:
        """Unload model from memory"""
        if self._model is not None:
            del self._model
            self._model = None
            self._model_loaded = False