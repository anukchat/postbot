"""
Unit tests for configuration module.
"""
import pytest
from src.backend.config import Config, ConfigLoader


class TestConfig:
    """Test Config dataclass."""
    
    def test_config_creation(self):
        """Test Config object creation."""
        config = Config(
            name="test",
            path="llm.test",
            class_params={"model": "gpt-4"},
            method_params={"temperature": 0.7}
        )
        assert config.name == "test"
        assert config.path == "llm.test"
        assert config.class_params["model"] == "gpt-4"
        assert config.method_params["temperature"] == 0.7


class TestConfigLoader:
    """Test ConfigLoader functionality."""
    
    def test_config_loader_initialization(self):
        """Test ConfigLoader can be initialized."""
        loader = ConfigLoader()
        assert loader.config_data is not None
    
    def test_list_configs(self):
        """Test listing available configurations."""
        loader = ConfigLoader()
        configs = loader.list_configs()
        assert isinstance(configs, list)
        assert len(configs) > 0
    
    def test_list_configs_with_prefix(self):
        """Test listing configs with prefix filter."""
        loader = ConfigLoader()
        llm_configs = loader.list_configs("llm")
        assert all(path.startswith("llm") for path in llm_configs)
    
    def test_get_config_invalid_path(self):
        """Test error on invalid config path."""
        loader = ConfigLoader()
        with pytest.raises(ValueError) as exc_info:
            loader.get_config("invalid.path.that.does.not.exist")
        assert "not found" in str(exc_info.value).lower()
    
    def test_config_has_expected_structure(self):
        """Test that valid configs have expected structure."""
        loader = ConfigLoader()
        configs = loader.list_configs()
        
        if configs:
            # Test first available config
            config = loader.get_config(configs[0])
            assert isinstance(config, Config)
            assert hasattr(config, 'name')
            assert hasattr(config, 'path')
            assert hasattr(config, 'class_params')
            assert hasattr(config, 'method_params')
