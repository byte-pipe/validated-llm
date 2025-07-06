regarding chatbot usage in this project, we assumed we are going to use vendor 'ollama' only, so there is no argument for vendor.

we should add vendor along with model, and pass vendor to the ChatBot class as well.

because we might use other vendors in the future.

```
❯ ag --hidden model
tests/test_llm_validation_integration.py
65:        return ValidationLoop(model=DEFAULT_MODEL, default_max_retries=MAX_ATTEMPTS)

examples/config_demo.py
105:    # Create ValidationLoop without specifying model or max_retries
110:    print(f"  model: {loop.model} (from config)")

src/validated_llm/validation_loop.py
33:        model: Optional[str] = None,
40:            model: Name of the Ollama model to use (defaults to config value)
48:        self.model = model or self.config.llm_model
116:            "model": self.model,
218:            "model": self.model,

src/validated_llm/async_validation_loop.py
34:        model: Optional[str] = None,
43:            model: Name of the Ollama model to use (defaults to config value)
52:        self.model = model or self.config.llm_model
136:            "model": self.model,
337:            "model": self.model,

src/validated_llm/integrations/langchain/examples/basic_conversion.py
55:        model="llama2"
```
