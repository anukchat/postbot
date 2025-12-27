from typing import Any, List, Optional, Dict
from litellm import Router
from dotenv import load_dotenv
from src.backend.config import Config, ConfigLoader
import backoff
import logging

load_dotenv()
logger = logging.getLogger(__name__)
# litellm.set_verbose=True

class Message:
    def __init__(self, content: str):
        self.content = content

    def __call__(self):
        return self.to_dict()

    def to_dict(self):
        raise NotImplementedError

class HumanMessage(Message):
    def to_dict(self):
        return {"role": "user", "content": self.content}

class SystemMessage(Message):
    def to_dict(self):
        return {"role": "system", "content": self.content}

class LLMClient:
    def __init__(self, config_path: str = "llm.default"):
        """
        Initialize LLM client with a specific configuration
        Args:
            config_path: Configuration path (e.g., "llm.chat", "llm.completion")
        """
        self.loader = ConfigLoader()
        try:
            self.config = self.loader.get_config(config_path)
        except ValueError as e:
            available_configs = self.loader.list_configs("llm")
            raise ValueError(f"Invalid configuration: {config_path}. Available configs: {available_configs}")
        
        # Get retry configuration from config
        self.num_retries = self.config.class_params.get('num_retries', 3)
        
        # Build model_list for Router from config
        model = self.config.class_params.get('model', 'gpt-3.5-turbo')
        max_parallel_requests = self.config.class_params.get('max_parallel_requests', 10)  # Default to 10 if not set
        
        litellm_params = self.config.class_params.copy()
        
        model_list = [{
            "model_name": model,  # Use actual model as alias
            "litellm_params": litellm_params
        }]
        
        # Initialize Router with built-in concurrency control
        self.router = Router(
            model_list=model_list,
            num_retries=self.num_retries
        )
        self.model_name = model
        logger.info(f"Initialized LLMClient with model={model}, max_parallel_requests={max_parallel_requests}, num_retries={self.num_retries}")

    @classmethod
    def from_config(cls, config: Config) -> 'LLMClient':
        """Create LLMClient instance from existing config"""
        instance = cls.__new__(cls)
        instance.config = config
        return instance

    def _convert_messages(self, messages: List[Any]) -> List[Dict[str, Any]]:
        converted = []
        for msg in messages:
            if isinstance(msg, Message):
                converted.append(msg.to_dict())
            elif isinstance(msg, dict):
                converted.append(msg)
            else:
                raise ValueError(f"Unsupported message type: {type(msg)}")
        return converted
    
    @backoff.on_exception(
        backoff.expo,
        Exception,
        max_tries=3,
        giveup=lambda e: 'RateLimitError' not in type(e).__name__ and '429' not in str(e),
        on_backoff=lambda details: logger.warning(
            f"Retry attempt {details['tries']} after {details['wait']:.1f}s due to: {str(details['exception'])[:100]}"
        )
    )
    def invoke(self, messages: List[Any], **kwargs) -> str:
        """Invoke LLM via Router with automatic concurrency control and retry."""
        if not messages:
            raise ValueError("Messages cannot be empty")
        
        converted_messages = self._convert_messages(messages)
        
        # Router handles concurrency via max_parallel_requests automatically
        response = self.router.completion(
            model=self.model_name,
            messages=converted_messages,
            **kwargs
        )
        return response.choices[0].message.content
    
# Usage examples:
# llm = LLMClient()  # uses llm.default with Router (reads max_parallel_requests from config)
# chat_llm = LLMClient("llm.chat")
# completion_llm = LLMClient("llm.completion")