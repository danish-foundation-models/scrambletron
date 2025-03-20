"""Presidio Operators for Anonymization."""

from __future__ import annotations

from typing import Callable

from faker import Faker
from faker.providers import person
from gender_guesser.detector import Detector
from presidio_anonymizer.operators import Operator, OperatorType


class InstanceCounterAnonymizer(Operator):
    """Anonymizer which replaces the entity value with an instance counter per entity."""

    REPLACING_FORMAT = "<{entity_type}_{index}>"

    def operate(self, text: str, params: dict | None = None) -> str:
        """Anonymize the input text."""
        if not params:
            raise ValueError("You need to supply parameters.")

        entity_type: str = params["entity_type"]

        # entity_mapping is a dict of dicts containing mappings per entity type
        entity_mapping: dict[str, dict] = params["entity_mapping"]

        entity_mapping_for_type = entity_mapping.get(entity_type)
        if not entity_mapping_for_type:
            new_text = self.REPLACING_FORMAT.format(entity_type=entity_type, index=0)
            entity_mapping[entity_type] = {}

        else:
            if text in entity_mapping_for_type:
                return entity_mapping_for_type[text]

            previous_index = self._get_last_index(entity_mapping_for_type)
            new_text = self.REPLACING_FORMAT.format(
                entity_type=entity_type, index=previous_index + 1
            )

        entity_mapping[entity_type][text] = new_text
        return new_text

    @staticmethod
    def _get_last_index(entity_mapping_for_type: dict) -> int:
        """Get the last index for a given entity type."""

        def get_index(value: str) -> int:
            return int(value.split("_")[-1][:-1])

        indices = [get_index(v) for v in entity_mapping_for_type.values()]
        return max(indices)

    def validate(self, params: dict | None = None) -> None:
        """Validate operator parameters."""
        if not params:
            raise ValueError("You need to supply parameters.")
        if "entity_mapping" not in params:
            msg = "An input Dict called `entity_mapping` is required."
            raise ValueError(msg)
        if "entity_type" not in params:
            msg = "An entity_type param is required."
            raise ValueError(msg)

    def operator_name(self) -> str:
        """Return the name of the operator."""
        return "entity_counter"

    def operator_type(self) -> OperatorType:
        """Return the operator type."""
        return OperatorType.Anonymize


class InstanceReplacerAnonymizer(Operator):
    """Anonymizer which replaces the entity value with a fake replacement per entity."""

    REPLACING_FORMAT = "<{type}_{replacement}>"

    def __init__(self):
        """Initialize the Replacer Operator."""
        super().__init__()
        self.fake = Faker(locale="da_DK")
        self.fake.add_provider(person)
        self.d = Detector(case_sensitive=False)

    def operate(self, text: str, params: dict | None = None) -> str:
        """Anonymize the input text."""
        if not params:
            raise ValueError("You need to supply parameters.")

        entity_type: str = params["entity_type"]

        # entity_mapping is a dict of dicts containing mappings per entity type
        entity_mapping: dict[str, dict] = params["entity_mapping"]

        entity_mapping_for_type = entity_mapping.get(entity_type)
        if not entity_mapping_for_type:
            replacement = self._generate_replacement(entity_type, text)
            new_text = self.REPLACING_FORMAT.format(
                type=entity_type, replacement=replacement
            )
            entity_mapping[entity_type] = {}

        else:
            if text in entity_mapping_for_type:
                return entity_mapping_for_type[text]

            # previous_index = self._get_last_index(entity_mapping_for_type)
            replacement = self._generate_replacement(entity_type, text)
            new_text = self.REPLACING_FORMAT.format(
                type=entity_type, replacement=replacement
            )

        entity_mapping[entity_type][text] = new_text
        return new_text

    @staticmethod
    def _get_last_index(entity_mapping_for_type: dict) -> int:
        """Get the last index for a given entity type."""

        def get_index(value: str) -> int:
            return int(value.split("_")[-1][:-1])

        indices = [get_index(v) for v in entity_mapping_for_type.values()]
        return max(indices)

    def _generate_replacement(self, entity: str, value: str) -> str:
        if entity == "PERSON":
            return self._guess_gender(value.split()[0])()
        if entity == "LOCATION":
            return self.fake.address().replace("\n", " ")
        if entity == "PHONE_NUMBER":
            return self.fake.phone_number()
        return ""

    def _guess_gender(self, text: str) -> Callable[(...), str]:
        """Guess the gender of a given name. Return a method for generating a gender specific name."""
        label_to_gender = {
            "unknown": self.fake.name_nonbinary,
            "andy": self.fake.name_nonbinary,
            "male": self.fake.name_male,
            "mostly_male": self.fake.name_male,
            "female": self.fake.name_female,
            "mostly_female": self.fake.name_female,
        }
        gender = self.d.get_gender(text)
        name_generator = label_to_gender[gender]
        print(text, gender, name_generator)
        return name_generator

    def validate(self, params: dict | None = None) -> None:
        """Validate operator parameters."""
        if not params:
            raise ValueError("You need to supply parameters.")
        if "entity_mapping" not in params:
            msg = "An input Dict called `entity_mapping` is required."
            raise ValueError(msg)
        if "entity_type" not in params:
            msg = "An entity_type param is required."
            raise ValueError(msg)

    def operator_name(self) -> str:
        """Return the name of the operator."""
        return "entity_replacer"

    def operator_type(self) -> OperatorType:
        """Return the operator type."""
        return OperatorType.Anonymize
