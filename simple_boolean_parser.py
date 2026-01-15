# simple_boolean_parser.py
import re

class SimpleBooleanParser:
    def __init__(self):
        self.operator_map = {'&': 'AND', '|': 'OR', '!': 'NOT', '^': 'XOR'}
    
    def parse(self, expression):
        expr = expression.strip()
        variables = sorted(set(re.findall(r'[A-Za-z]', expr)))
        
        if not variables:
            return {"error": "No variables found"}
        
        return {
            "expression": expression,
            "variables": variables,
            "num_inputs": len(variables)
        }
