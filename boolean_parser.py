#!/usr/bin/env python3
"""
Boolean Expression Parser
"""

import re
from typing import Dict, List, Optional, Union

class BooleanExpressionParser:
    def __init__(self):
        self.operators = {
            '&': 'AND', '·': 'AND',
            '|': 'OR', '+': 'OR',
            '!': 'NOT', "'": 'NOT',
            '^': 'XOR', '⊕': 'XOR',
            '~^': 'XNOR', '~&': 'NAND', '~|': 'NOR'
        }
    
    def parse_expression(self, expression: str) -> Dict:
        """Parse Boolean expression into structured format"""
        
        # Remove spaces and normalize
        expr = expression.replace(" ", "").replace("·", "&")
        
        # Find variables
        variables = sorted(set(re.findall(r'[A-Za-z]', expr)))
        
        # Parse expression tree
        ast = self._parse_to_ast(expr)
        
        # Generate truth table from expression
        truth_table = self._generate_truth_table(ast, variables)
        
        # Extract minterms
        minterms = self._extract_minterms(truth_table)
        
        return {
            "expression": expression,
            "variables": variables,
            "ast": ast,
            "truth_table": truth_table,
            "minterms": minterms,
            "num_inputs": len(variables),
            "num_outputs": 1  # For now, single output
        }
    
    def _parse_to_ast(self, expr: str) -> Dict:
        """Convert expression to Abstract Syntax Tree"""
        # This is a simplified parser - expand for complex expressions
        if expr.startswith("!(") or expr.startswith("~("):
            return {
                "type": "NOT",
                "operand": self._parse_to_ast(expr[2:-1])
            }
        
        # Handle parentheses first
        for op in ['&', '|', '^', '~^', '~&', '~|']:
            if op in expr:
                parts = expr.split(op, 1)
                return {
                    "type": self.operators[op],
                    "left": self._parse_to_ast(parts[0]),
                    "right": self._parse_to_ast(parts[1])
                }
        
        # Base case: variable or constant
        if expr in ['0', '1']:
            return {"type": "CONSTANT", "value": int(expr)}
        else:
            return {"type": "VARIABLE", "name": expr}
    
    def _evaluate_ast(self, ast: Dict, variable_values: Dict[str, int]) -> int:
        """Evaluate AST with given variable values"""
        if ast["type"] == "CONSTANT":
            return ast["value"]
        elif ast["type"] == "VARIABLE":
            return variable_values[ast["name"]]
        elif ast["type"] == "NOT":
            return 1 - self._evaluate_ast(ast["operand"], variable_values)
        else:
            # Binary operator
            left = self._evaluate_ast(ast["left"], variable_values)
            right = self._evaluate_ast(ast["right"], variable_values)
            
            # For now, handle basic operations
            if ast["type"] == "AND":
                return left & right
            elif ast["type"] == "OR":
                return left | right
            elif ast["type"] == "XOR":
                return left ^ right
            elif ast["type"] == "NAND":
                return 1 if not (left & right) else 0
            elif ast["type"] == "NOR":
                return 1 if not (left | right) else 0
            elif ast["type"] == "XNOR":
                return 1 if left == right else 0
        
        return 0
    
    def _generate_truth_table(self, ast: Dict, variables: List[str]) -> List[Dict]:
        """Generate complete truth table"""
        table = []
        num_combinations = 2 ** len(variables)
        
        for i in range(num_combinations):
            # Create variable assignment
            values = {}
            for j, var in enumerate(variables):
                values[var] = (i >> (len(variables) - j - 1)) & 1
            
            # Evaluate expression
            output = self._evaluate_ast(ast, values)
            
            table.append({
                "inputs": values,
                "output": output,
                "binary_str": format(i, f'0{len(variables)}b')
            })
        
        return table
    
    def _extract_minterms(self, truth_table: List[Dict]) -> List[int]:
        """Extract minterms where output is 1"""
        minterms = []
        for i, row in enumerate(truth_table):
            if row["output"] == 1:
                minterms.append(i)
        return minterms
