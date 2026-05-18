import json
import time
from typing import Any, Optional


def validate_against_schema(data: dict, schema: dict) -> tuple[bool, list[str]]:
    errors = []

    def _validate(value, schema, path: str):
        if "type" in schema:
            expected = schema["type"]
            if expected == "object":
                if not isinstance(value, dict):
                    errors.append(f"{path}: expected object, got {type(value).__name__}")
                    return
                for prop, prop_schema in schema.get("properties", {}).items():
                    if prop in value:
                        _validate(value[prop], prop_schema, f"{path}.{prop}")
                    elif prop in schema.get("required", []):
                        errors.append(f"{path}: missing required property '{prop}'")
            elif expected == "array":
                if not isinstance(value, list):
                    errors.append(f"{path}: expected array, got {type(value).__name__}")
                    return
                item_schema = schema.get("items", {})
                for i, item in enumerate(value):
                    _validate(item, item_schema, f"{path}[{i}]")
            elif expected == "string":
                if not isinstance(value, str):
                    errors.append(f"{path}: expected string, got {type(value).__name__}")
                elif "enum" in schema and value not in schema["enum"]:
                    errors.append(f"{path}: '{value}' not in {schema['enum']}")
            elif expected == "number":
                if not isinstance(value, (int, float)):
                    errors.append(f"{path}: expected number, got {type(value).__name__}")
                elif isinstance(value, bool):
                    errors.append(f"{path}: expected number, got bool")
                else:
                    if "minimum" in schema and value < schema["minimum"]:
                        errors.append(f"{path}: {value} < minimum {schema['minimum']}")
                    if "maximum" in schema and value > schema["maximum"]:
                        errors.append(f"{path}: {value} > maximum {schema['maximum']}")
            elif expected == "integer":
                if not isinstance(value, int) or isinstance(value, bool):
                    errors.append(f"{path}: expected integer, got {type(value).__name__}")
                else:
                    if "minimum" in schema and value < schema["minimum"]:
                        errors.append(f"{path}: {value} < minimum {schema['minimum']}")
                    if "maximum" in schema and value > schema["maximum"]:
                        errors.append(f"{path}: {value} > maximum {schema['maximum']}")
            elif expected == "boolean":
                if not isinstance(value, bool):
                    errors.append(f"{path}: expected boolean, got {type(value).__name__}")

        if "minItems" in schema and isinstance(value, list):
            if len(value) < schema["minItems"]:
                errors.append(f"{path}: too few items ({len(value)} < {schema['minItems']})")
        if "maxItems" in schema and isinstance(value, list):
            if len(value) > schema["maxItems"]:
                errors.append(f"{path}: too many items ({len(value)} > {schema['maxItems']})")

    _validate(data, schema, "$")
    return len(errors) == 0, errors


def validate_or_retry(
    data_producer,
    schema: dict,
    max_retries: int = 3,
    delay: float = 1.0,
) -> Optional[dict[str, Any]]:
    for attempt in range(1, max_retries + 1):
        try:
            data = data_producer() if callable(data_producer) else data_producer
            if not isinstance(data, dict):
                data = json.loads(data) if isinstance(data, str) else None
        except Exception:
            data = None

        if data:
            valid, errors = validate_against_schema(data, schema)
            if valid:
                return data

        if attempt < max_retries:
            time.sleep(delay)

    return None
