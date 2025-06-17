"""Utilities for anonymizing texts."""

import typing as t

if t.TYPE_CHECKING:
    from presidio_analyzer import AnalyzerEngine, BatchAnalyzerEngine
    from presidio_anonymizer import AnonymizerEngine, BatchAnonymizerEngine


def create_analyzer() -> "AnalyzerEngine":
    """Create a analyzer engine using Presidio.

    Returns:
        AnalyzerEngine: Analyzer engine for finding PII in text.
    """
    from phonenumbers import SUPPORTED_REGIONS
    from presidio_analyzer import AnalyzerEngine
    from presidio_analyzer.nlp_engine import NlpEngineProvider
    from presidio_analyzer.pattern import Pattern
    from presidio_analyzer.pattern_recognizer import PatternRecognizer
    from presidio_analyzer.predefined_recognizers import (
        CreditCardRecognizer,
        DateRecognizer,
        EmailRecognizer,
        GLiNERRecognizer,
        IpRecognizer,
        PhoneRecognizer,
        UrlRecognizer,
    )

    from .recognizers.cpr_recognizer import CPRRecognizer

    configuration = {
        "nlp_engine_name": "spacy",
        "models": [
            {"lang_code": "da", "model_name": "da_core_news_trf"},
            {"lang_code": "en", "model_name": "en_core_web_md"},
        ],
    }

    # Create NLP engine based on configuration
    provider = NlpEngineProvider(nlp_configuration=configuration)
    nlp_engine_with_danish = provider.create_engine()

    # Pass the created NLP engine and supported_languages to the AnalyzerEngine
    analyzer = AnalyzerEngine(
        nlp_engine=nlp_engine_with_danish, supported_languages=["en", "da"]
    )

    analyzer.registry.add_recognizer(CPRRecognizer(supported_language="da"))

    analyzer.registry.add_recognizer(
        CreditCardRecognizer(
            supported_language="da",
            context=[
                "kreditkort",
                "kreditkortnummer",
                "kortnummer",
                "kort nr.",
                "kortnr.",
                "dankort",
                "dankortnummer",
                "dankort nr.",
                "dankortnr.",
            ],
        )
    )

    analyzer.registry.add_recognizer(
        PatternRecognizer(
            supported_language="da",
            supported_entity="DK_DRIVER_LICENSE",
            patterns=[  # Driver license number is just 8 numbers, so this pattern is very weak.
                Pattern("DK_DRIVER_LICENSE1 (very weak)", r"\b[0-9]{8}\b", 0.05)
            ],
            context=["kørekortnummer", "kørekort nr.", "kørekortnr.", "kørekort nr"],
        )
    )

    analyzer.registry.add_recognizer(
        PhoneRecognizer(
            ["tlf.", "telefon", "tlf. nr."],
            supported_language="da",
            supported_regions=SUPPORTED_REGIONS,
        )
    )
    entity_mapping = {
        "name": "PERSON",
        "person": "PERSON",
        "city": "LOCATION",
        "location": "LOCATION",
        "address": "LOCATION",
        "country": "LOCATION",
        "website": "URL",
    }

    gliner_recognizer = GLiNERRecognizer(
        model_name="urchade/gliner_multi-v2.1",
        supported_language="da",
        entity_mapping=entity_mapping,
        flat_ner=False,
        multi_label=True,
        map_location="cpu",
    )

    analyzer.registry.add_recognizer(gliner_recognizer)
    # remove spacy recognizer because we dont want it to interfere with gliner (as per presidio docs)
    analyzer.registry.remove_recognizer("SpacyRecognizer")

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

    analyzer.registry.add_recognizer(
        UrlRecognizer(context=["url", "website", "hjemmeside"], supported_language="da")
    )

    analyzer.registry.add_recognizer(IpRecognizer(supported_language="da"))
    analyzer.registry.add_recognizer(
        DateRecognizer(
            context=["dato", "d.", "d.d.", "fødselsdag"], supported_language="da"
        )
    )

    return analyzer


def create_anonymizer() -> "AnonymizerEngine":
    """Create an anonymizer engine.

    Returns:
        AnonymizerEngine: Engine for anonymizing text.
    """
    from presidio_anonymizer import AnonymizerEngine

    from .anonymizer import InstanceReplacerAnonymizer

    # Initialize the engine:
    engine = AnonymizerEngine()
    # engine.add_anonymizer(InstanceCounterAnonymizer)
    engine.add_anonymizer(InstanceReplacerAnonymizer)

    return engine


def create_batch_analyzer() -> "BatchAnalyzerEngine":
    """Create a batch analyzer engine.

    Returns:
        BatchAnalyzerEngine: Engine for analyzing text in batches.
    """
    from presidio_analyzer import BatchAnalyzerEngine

    engine = create_analyzer()

    return BatchAnalyzerEngine(engine)


def create_batch_anonymizer() -> "BatchAnonymizerEngine":
    """Create a batch anonymizer engine.

    Returns:
        BatchAnonymizerEngine: Engine for anonymizing text in batches.
    """
    from presidio_anonymizer import BatchAnonymizerEngine

    engine = create_anonymizer()

    return BatchAnonymizerEngine(engine)
