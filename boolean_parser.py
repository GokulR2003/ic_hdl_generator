#!/usr/bin/env python3
"""Improved Boolean Expression Parser for Demo"""

import re
import json

class ImprovedBooleanParser:
    def __init__(self):
        self.operator_map = {
            '&': 'AND', 
            '|': 'OR', 
            '!': 'NOT', 
            '^': 'XOR',
            '+': 'OR',
            '*': 'AND'
        }
        self.precedence = {
            '!': 3,  # Highest
            '&': 2,
            '*': 2,
            '^': 1,
            '|': 0,
            '+': 0   # Lowest
        }
    
    def parse(self, expression):
        expr = expression.strip()
        
        # Replace common alternative symbols
        expr = expr.replace('+', '|').replace('*', '&')
        
        # Validate expression
        if not re.match(r'^[A-Za-z01!&|^()\s]+$', expr):
            return {"error": f"Invalid characters in expression: {expr}"}
        
        # Extract variables
        variables = sorted(set(re.findall(r'[A-Za-z]', expr)))
        
        if not variables:
            return {"error": "No variables found"}
        
        # Parse expression tree (simplified)
        try:
            parsed_tree = self._parse_expression(expr)
        except Exception as e:
            return {"error": f"Parsing failed: {str(e)}"}
        
        return {
            "expression": expression,
            "variables": variables,
            "num_inputs": len(variables),
            "parsed_tree": parsed_tree,
            "valid": True
        }
    
    def _parse_expression(self, expr):
        """Simple recursive descent parser"""
        expr = expr.replace(' ', '')
        
        # Handle parentheses
        if '(' in expr:
            # Find matching parentheses
            depth = 0
            start = expr.find('(')
            for i, char in enumerate(expr[start:]):
                if char == '(':
                    depth += 1
                elif char == ')':
                    depth -= 1
                    if depth == 0:
                        end = start + i
                        inner = expr[start+1:end]
                        return {
                            "type": "group",
                            "inner": self._parse_expression(inner)
                        }
        
        # Handle operators with precedence
        # Check for lowest precedence first
        for op in ['|', '^', '&', '!']:
            if op in expr:
                if op == '!':  # Unary operator
                    return {
                        "type": "unary",
                        "operator": op,
                        "operand": self._parse_expression(expr[1:])
                    }
                else:  # Binary operator
                    # Split by operator (handle multiple instances)
                    parts = expr.split(op)
                    if len(parts) > 1:
                        return {
                            "type": "binary",
                            "operator": op,
                            "left": self._parse_expression(parts[0]),
                            "right": self._parse_expression(op.join(parts[1:]))
                        }
        
        # Handle single variable or constant
        if len(expr) == 1 and expr.isalpha():
            return {"type": "variable", "value": expr}
        elif expr in ['0', '1']:
            return {"type": "constant", "value": expr}
        
        return {"type": "unknown", "value": expr}

def test_parser():
    parser = ImprovedBooleanParser()
    
    test_expressions = [
        "A&B",
        "A|B",
        "A^B",
        "!(A&B)",
        "A&(B|C)",
        "A^B + C&D",
        "(A+B)&(C+D)"
    ]
    
    results = []
    for expr in test_expressions:
        result = parser.parse(expr)
        results.append({
            "expression": expr,
            "result": result
        })
        print(f"Expression: {expr}")
        print(f"Result: {json.dumps(result, indent=2)[:200]}...")
        print("-" * 50)
    
    return results

if __name__ == "__main__":
    test_parser()
