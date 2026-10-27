#!/usr/bin/env python3
"""Validate a Resume Genie output against references/output-schema.json.

A small, dependency-free JSON Schema checker covering the keywords the schema uses:
type, required, properties, items, enum, minimum, maximum, minItems.

Usage:
  python validate_output.py OUTPUT.json [SCHEMA.json]
Exit code 0 = valid, 1 = invalid.

Author: Rahul Kashyap. MIT licence.
"""
import json
import os
import sys

TYPES = {'object': dict, 'array': list, 'string': str, 'boolean': bool, 'integer': int, 'number': (int, float)}
DEFAULT_SCHEMA = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'references', 'output-schema.json')


def validate(value, schema, path='$'):
    errors = []
    expected = schema.get('type')
    if expected:
        ok = isinstance(value, TYPES[expected]) and not (expected in ('integer', 'number') and isinstance(value, bool))
        if not ok:
            return [f'{path}: expected {expected}, got {type(value).__name__}']
    if 'enum' in schema and value not in schema['enum']:
        errors.append(f"{path}: {value!r} is not one of {schema['enum']}")
    if 'minimum' in schema and value < schema['minimum']:
        errors.append(f"{path}: {value} is below {schema['minimum']}")
    if 'maximum' in schema and value > schema['maximum']:
        errors.append(f"{path}: {value} is above {schema['maximum']}")
    if isinstance(value, dict):
        for key in schema.get('required', []):
            if key not in value:
                errors.append(f'{path}: missing required "{key}"')
        for key, sub in schema.get('properties', {}).items():
            if key in value:
                errors += validate(value[key], sub, f'{path}.{key}')
    if isinstance(value, list):
        if len(value) < schema.get('minItems', 0):
            errors.append(f"{path}: needs at least {schema['minItems']} item(s)")
        for i, item in enumerate(value):
            errors += validate(item, schema.get('items', {}), f'{path}[{i}]')
    return errors


def main(argv):
    if len(argv) not in (2, 3):
        print(__doc__)
        return 2
    output = json.load(open(argv[1], encoding='utf-8'))
    schema = json.load(open(argv[2] if len(argv) == 3 else DEFAULT_SCHEMA, encoding='utf-8'))
    errors = validate(output, schema)
    if errors:
        print(f'{len(errors)} problem(s):')
        print('\n'.join(f'- {e}' for e in errors))
        return 1
    print('Valid Resume Genie output.')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
