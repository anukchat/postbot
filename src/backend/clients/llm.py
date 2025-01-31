from typing import Any, List, Optional, Dict
from litellm import completion
from dotenv import load_dotenv
from src.backend.config import Config, ConfigLoader
import time

load_dotenv()
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
    
    def invoke(self, messages: List[Any], max_retries: int = 3, initial_delay: float = 1.0, **kwargs) -> str:
        if not messages:
            raise ValueError("Messages cannot be empty")
        
        converted_messages = self._convert_messages(messages)

        params = self.config.class_params.copy()
        params.update(kwargs)
        
        model_config = {
            "messages": converted_messages,
            **params
        }

        last_exception = None
        delay = initial_delay

        for attempt in range(max_retries):
            try:
                response = completion(**model_config)
                return response.choices[0].message.content
            except Exception as e:
                last_exception = e
                if attempt < max_retries - 1:
                    time.sleep(delay)
                    delay *= 2  # Exponential backoff
                    continue
                
        raise Exception(f"LLM invocation failed after {max_retries} attempts: {str(last_exception)}")

# Usage examples:
# llm = LLMClient()  # uses llm.default 
# chat_llm = LLMClient("llm.chat")
# completion_llm = LLMClient("llm.completion")