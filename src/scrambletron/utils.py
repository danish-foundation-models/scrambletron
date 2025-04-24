"""Utilities for anonymizing texts."""


def create_analyzer():
    """Create a analyzer engine using Presidio.

    Returns:
        AnalyzerEngine: Analyzer engine for finding PII in text.
    """
    from phonenumbers import SUPPORTED_REGIONS
    from presidio_analyzer import AnalyzerEngine
    from presidio_analyzer.nlp_engine import NlpEngineProvider
    from presidio_analyzer.predefined_recognizers import (
        DateRecognizer,
        EmailRecognizer,
        IpRecognizer,
        PhoneRecognizer,
    )

    hf_model = {
        "en": "FacebookAI/xlm-roberta-large-finetuned-conll03-english",
        "da": "alexandrainst/da-ner-base",
    }

    # Create configuration containing engine name and models
    configuration = {
        "nlp_engine_name": "transformers",
        "models": [
            {
                "lang_code": "da",
                "model_name": {
                    "spacy": "da_core_news_trf",
                    "transformers": hf_model["da"],
                },
            },
            {
                "lang_code": "en",
                "model_name": {
                    "spacy": "en_core_web_md",
                    "transformers": hf_model["en"],
                },
            },
        ],
    }

    # configuration = {
    #     "nlp_engine_name": "spacy",
    #     "models": [
    #         {"lang_code": "da", "model_name": "da_core_news_trf"},
    #         {"lang_code": "en", "model_name": "en_core_web_md"},
    #     ],
    # }

    # Create NLP engine based on configuration
    provider = NlpEngineProvider(nlp_configuration=configuration)
    nlp_engine_with_danish = provider.create_engine()

    # Pass the created NLP engine and supported_languages to the AnalyzerEngine
    analyzer = AnalyzerEngine(
        nlp_engine=nlp_engine_with_danish, supported_languages=["en", "da"]
    )
    analyzer.registry.add_recognizer(
        PhoneRecognizer(
            ["tlf.", "telefon", "tlf. nr."],
            supported_language="da",
            supported_regions=SUPPORTED_REGIONS,
        )
    )

    analyzer.registry.add_recognizer(
        EmailRecognizer(
            context=[
                "email",
                "mail",
                "e-mail",
                "e-mail adresse",
                "mailadresse",
                "emailadresse",
            ],
            supported_language="da",
        )
    )

    analyzer.registry.add_recognizer(IpRecognizer(supported_language="en"))
    analyzer.registry.add_recognizer(
        DateRecognizer(
            context=["dato", "d.", "d.d.", "fødselsdag"], supported_language="da"
        )
    )

    return analyzer


def create_anonymizer():
    """Create an anonymizer engine.

    Returns:
        AnonymizerEngine: Engine for anonymizing text.
    """
    from presidio_anonymizer import AnonymizerEngine

    # Initialize the engine:
    engine = AnonymizerEngine()
    # engine.add_anonymizer(InstanceReplacerAnonymizer)

    return engine
