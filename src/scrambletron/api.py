"""Scrambletron API."""

from fastapi import FastAPI
from pydantic import BaseModel

from scrambletron.utils import create_batch_analyzer, create_batch_anonymizer

app = FastAPI()


class ScrambleData(BaseModel):
    """Dataclass for the scramble endpoint."""

    text: str
    language: str = "da"


def anonymize_file(input_str, language: str = "da"):
    """Anonymize a piece of text in a given language.

    Args:
        input_str: The text to be anonymized.
        language (str, optional): Language of the text. Used for selecting relevant models. Defaults to "da".
    """
    texts = input_str.split("\n")
    analyzer = create_batch_analyzer()
    analysis_result = analyzer.analyze_iterator(texts, language=language)

    # Create a mapping between entity types and counters
    # entity_mapping = dict()

    anonymizer = create_batch_anonymizer()
    results = anonymizer.anonymize_list(
        texts=texts,
        recognizer_results_list=analysis_result,
        # operators={
        #     "DEFAULT": OperatorConfig(
        #         "entity_replacer", {"entity_mapping": entity_mapping}
        #     )
        # },
    )
    return ScrambleData(text="\n".join(results), language=language)


@app.post("/scramble")
async def scramble(request: ScrambleData):
    """Scramble endpoint.

    Args:
        request (ScrambleRequest): The request object containing the text and language.

    Returns:
        The scrambled text.
    """
    return anonymize_file(request.text, request.language)
