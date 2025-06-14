
import importlib

from ..framework import Sys


def system_language():
    culture = Sys.Globalization.CultureInfo.CurrentUICulture
    return culture.TwoLetterISOLanguageName


class Translations:
    def __init__(self, settings):
        super().__init__()

        self.settings = settings
        
        self.languages = {
            "English": "BTCZWallet.translations.en",
            "French": "BTCZWallet.translations.fr",
            "Arabic": "BTCZWallet.translations.ar"
        }

        sys_lang = system_language()
        default_lang = {
            "en": "English",
            "fr": "French",
            "ar": "Arabic"
        }.get(sys_lang, "English")

        self.current_language = self.settings.language() or default_lang
        self.labels = self.load_language(self.current_language)


    def load_language(self, language: str) -> dict:
        lang_module = self.languages.get(language, self.languages["English"])
        try:
            lang_translations = importlib.import_module(lang_module)
            return lang_translations.translations
        except ModuleNotFoundError:
            print(f"Translation module '{lang_module}' not found. Falling back to English")
            lang_translations = importlib.import_module(self.languages["English"])
            return lang_translations.translations
        
        

    def text(self, key: str) -> str:
        return self.labels.get(key, {}).get("text", f"Missing text for {key}")
    
    def title(self, key: str) -> str:
        return self.labels.get(key, {}).get("title", f"Missing title for {key}")
    
    def message(self, key: str) -> str:
        return self.labels.get(key, {}).get("message", f"Missing message for {key}")
    
    def size(self, key: str) -> str:
        return self.labels.get(key, {}).get("size", f"Missing size for {key}")
    
    def tooltip(self, key: str) -> str:
        return self.labels.get(key, {}).get("tooltip", f"Missing tooltip for {key}")
    
    def padding(self, key: str) -> str:
        return self.labels.get(key, {}).get("padding", f"Missing padding for {key}")
    
    def align(self, key: str) -> str:
        return self.labels.get(key, {}).get("align", f"Missing align for {key}")
