import json
import os
import argparse
from jinja2 import Template

model_template = """
from pydantic import BaseModel

class {{ class_name }}(BaseModel):
{% for prop, details in properties.items() %}
    {{ prop }}: {{ details['type'] }}
{% endfor %}
"""


def generate_model(class_name, properties, output_dir):
    template = Template(model_template)
    model_code = template.render(class_name=class_name, properties=properties)

    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, f"{class_name.lower()}.py")
    with open(file_path, 'w') as f:
        f.write(model_code)


def parse_properties(properties):
    parsed_properties = {}
    for prop, details in properties.items():
        prop_type = details['type']
        if prop_type == 'string':
            parsed_properties[prop] = {'type': 'str'}
        elif prop_type == 'integer':
            parsed_properties[prop] = {'type': 'int'}
        elif prop_type == 'object':
            parsed_properties[prop] = {'type': 'dict'}
        else:
            parsed_properties[prop] = {'type': 'Any'}
    return parsed_properties


def generate_models(json_schema_file, output_dir):
    with open(json_schema_file, 'r') as file:
        schema = json.load(file)

    root_properties = parse_properties(schema.get('properties', {}))
    generate_model('RootModel', root_properties, output_dir)

    if 'properties' in schema:
        for prop, details in schema['properties'].items():
            if details.get('type') == 'object':
                nested_properties = parse_properties(details.get('properties', {}))
                generate_model(prop.capitalize(), nested_properties, output_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate Pydantic models from JSON schema')
    parser.add_argument('--json-schema', required=True, help='Path to the JSON schema file')
    parser.add_argument('--output-dir', required=True, help='Directory to save generated models')
    args = parser.parse_args()

    generate_models(args.json_schema, args.output_dir)
