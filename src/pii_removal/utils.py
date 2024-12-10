def create_analyzer():
    from presidio_analyzer import AnalyzerEngine
    from presidio_analyzer.nlp_engine import NlpEngineProvider

    # Create configuration containing engine name and models
    configuration = {
        "nlp_engine_name": "spacy",
        "models": [{"lang_code": "da", "model_name": "da_core_news_trf"},
                    {"lang_code": "en", "model_name": "en_core_web_md"}],
    }

    # Create NLP engine based on configuration
    provider = NlpEngineProvider(nlp_configuration=configuration)
    nlp_engine_with_danish = provider.create_engine()

    # Pass the created NLP engine and supported_languages to the AnalyzerEngine
    analyzer = AnalyzerEngine(
        nlp_engine=nlp_engine_with_danish, 
        supported_languages=["en", "da"]
    )

    return analyzer


def create_anonymizer():
    from presidio_anonymizer import AnonymizerEngine

    # Initialize the engine:
    engine = AnonymizerEngine()

    return engine