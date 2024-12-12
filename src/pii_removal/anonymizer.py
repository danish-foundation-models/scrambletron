"""Presidio Operators for Anonymization."""

from __future__ import annotations

from faker import Faker
from presidio_anonymizer.operators import Operator, OperatorType


class InstanceCounterAnonymizer(Operator):
    """Anonymizer which replaces the entity value with an instance counter per entity."""

    REPLACING_FORMAT = "<{entity_type}_{index}>"

    def operate(self, text: str, params: dict | None = None) -> str:
        """Anonymize the input text."""
        entity_type: str = params["entity_type"]

        # entity_mapping is a dict of dicts containing mappings per entity type
        entity_mapping: dict[dict:str] = params["entity_mapping"]

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

    REPLACING_FORMAT = "<{entity_type}_'{replacement}'_{index}>"

    def operate(self, text: str, params: dict | None = None) -> str:
        """Anonymize the input text."""
        entity_type: str = params["entity_type"]

        # entity_mapping is a dict of dicts containing mappings per entity type
        entity_mapping: dict[dict:str] = params["entity_mapping"]

        entity_mapping_for_type = entity_mapping.get(entity_type)
        if not entity_mapping_for_type:
            replacement = self._generate_replacement(entity_type)
            new_text = self.REPLACING_FORMAT.format(
                entity_type=entity_type, index=0, replacement=replacement
            )
            entity_mapping[entity_type] = {}

        else:
            if text in entity_mapping_for_type:
                return entity_mapping_for_type[text]

            previous_index = self._get_last_index(entity_mapping_for_type)
            replacement = self._generate_replacement(entity_type)
            new_text = self.REPLACING_FORMAT.format(
                entity_type=entity_type,
                index=previous_index + 1,
                replacement=replacement,
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

    @staticmethod
    def _generate_replacement(entity: str) -> str:
        fake = Faker(locale="da_DK")
        if entity == "PERSON":
            return fake.name()
        if entity == "LOCATION":
            return fake.address()
        return ""

    def validate(self, params: dict | None = None) -> None:
        """Validate operator parameters."""
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
