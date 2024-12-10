from presidio_anonymizer import OperatorConfig
import typer

from pii_removal.anonymizer import InstanceCounterAnonymizer, InstanceReplacerAnonymizer
from pii_removal.utils import create_analyzer, create_anonymizer

app = typer.Typer(name="PII-Removal CLI")



@app.command()
def anonymize(text: str, language: str = "da"):
    analyzer = create_analyzer()
    analysis_result = analyzer.analyze(text, language=language)
    

    entity_mapping = dict()
    anonymizer = create_anonymizer()
    anonymizer.add_anonymizer(InstanceReplacerAnonymizer)
    result = anonymizer.anonymize(text=text, analyzer_results=analysis_result, operators={
        "DEFAULT": OperatorConfig(
            "entity_replacer", {"entity_mapping": entity_mapping}
        )
    })
    print(result.text)