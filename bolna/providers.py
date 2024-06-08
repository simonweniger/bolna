from .synthesizer import DeepgramSynthesizer
from .transcriber import DeepgramTranscriber
from .input_handlers import DefaultInputHandler, TwilioInputHandler
from .output_handlers import DefaultOutputHandler, TwilioOutputHandler
from .llms import OpenAiLLM, LiteLLM

SUPPORTED_SYNTHESIZER_MODELS = {
    'deepgram': DeepgramSynthesizer
}
SUPPORTED_TRANSCRIBER_MODELS = {
    'deepgram': DeepgramTranscriber,
}

SUPPORTED_LLM_PROVIDERS = {
    'openai': OpenAiLLM,
    'cohere': LiteLLM,
    'ollama': LiteLLM,
    'deepinfra': LiteLLM,
    'together': LiteLLM,
    'fireworks': LiteLLM,
    'azure-openai': LiteLLM,
    'perplexity': LiteLLM,
    'vllm': LiteLLM,
    'anyscale': LiteLLM,
    'custom': OpenAiLLM,
    'ola': OpenAiLLM,
    'groq': LiteLLM
}
SUPPORTED_INPUT_HANDLERS = {
    'default': DefaultInputHandler,
    'twilio': TwilioInputHandler,
}
SUPPORTED_INPUT_TELEPHONY_HANDLERS = {
    'twilio': TwilioInputHandler,
}
SUPPORTED_OUTPUT_HANDLERS = {
    'default': DefaultOutputHandler,
    'twilio': TwilioOutputHandler,
}
SUPPORTED_OUTPUT_TELEPHONY_HANDLERS = {
    'twilio': TwilioOutputHandler,
}
