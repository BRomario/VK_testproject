import json
import jsonschema
from jsonschema import validate
import argparse


def validate_json_schema(json_schema_path):
    with open(json_schema_path, 'r') as file:
        schema = json.load(file)
    try:
        validate(instance=schema, schema={})
        print("JSON Schema is valid")
    except jsonschema.exceptions.ValidationError as err:
        print("JSON Schema is invalid", err)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate JSON schema")
    parser.add_argument('--json-schema', type=str, required=True, help="Path to JSON schema file")
    args = parser.parse_args()
    validate_json_schema(args.json_schema)
