"""Main entry point for anonymization methods."""

import typer
from presidio_anonymizer import OperatorConfig

from pii_removal.utils import create_analyzer, create_anonymizer

app = typer.Typer(name="PII-Removal CLI")


@app.command()
def anonymize(text: str, language: str = "da"):
    """Anonymize a piece of text in a given language.

    Args:
        text (str): The text to be anonymized.
        language (str, optional): Language of the text. Used for selecting relevant models. Defaults to "da".
    """
    analyzer = create_analyzer()
    analysis_result = analyzer.analyze(text, language=language)

    entity_mapping = dict()
    anonymizer = create_anonymizer()
    result = anonymizer.anonymize(
        text=text,
        analyzer_results=analysis_result,
        operators={
            "DEFAULT": OperatorConfig(
                "entity_replacer", {"entity_mapping": entity_mapping}
            )
        },
    )
    print(result.text)
