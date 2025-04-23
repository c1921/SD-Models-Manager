from src.core.translation_service import TranslationService

class PromptManager:
    def __init__(self, config_file="config.json"):
        self.translator = TranslationService() 