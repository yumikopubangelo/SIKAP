#!/usr/bin/env python3

from app import create_app

app = create_app()

print('Available API routes:')
print('=' * 100)
print(f'{"Endpoint":<55} {"Methods":<15}')
print('=' * 100)

for rule in app.url_map.iter_rules():
    if '/api/v1/' in str(rule):
        methods = ','.join(sorted([m for m in rule.methods if m not in {'OPTIONS', 'HEAD'}]))
        endpoint = str(rule)
        print(f'{endpoint:<55} {methods:<15}')

print('=' * 100)
