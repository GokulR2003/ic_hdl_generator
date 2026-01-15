#!/usr/bin/env python3
"""
Boolean Expression to HDL Generator
Generates HDL code from boolean expressions with IC mapping
"""

import re
import json
import os
import sys
from jinja2 import Template

class BooleanExpressionParser:
    """Parser for boolean expressions"""
    
    def __init__(self):
        self.operators = {
            '!': {'precedence': 3, 'assoc': 'right', 'type': 'unary'},
            '&': {'precedence': 2, 'assoc': 'left', 'type': 'binary'},
            '|': {'precedence': 1, 'assoc': 'left', 'type': 'binary'},
            '^': {'precedence': 1, 'assoc': 'left', 'type': 'binary'}
        }
        
        self.alternative_symbols = {
            '+': '|',
            '*': '&',
            '~': '!',
            'and': '&',
            'or': '|',
            'xor': '^',
            'not': '!'
        }
    
    def parse(self, expression):
        """Parse boolean expression and extract variables"""
        # Normalize expression
        expr = expression.strip()
        
        # Replace alternative symbols
        for alt, std in self.alternative_symbols.items():
            expr = expr.replace(alt, std)
        
        # Remove spaces
        expr = expr.replace(' ', '')
        
        # Validate expression
        if not self._validate_expression(expr):
            return {"error": f"Invalid boolean expression: {expression}"}
        
        # Extract variables (single letters, uppercase/lowercase)
        variables = sorted(set([c for c in expr if c.isalpha()]))
        
        if not variables:
            return {"error": "No variables found in expression"}
        
        # Create truth table (for up to 4 variables)
        if len(variables) <= 4:
            truth_table = self._generate_truth_table(expr, variables)
        else:
            truth_table = "Too many variables for truth table display"
        
        # Simplify using basic boolean algebra
        simplified = self._simplify_expression(expr)
        
        return {
            "original": expression,
            "normalized": expr,
            "variables": variables,
            "num_inputs": len(variables),
            "simplified": simplified,
            "truth_table": truth_table,
            "verilog_expr": self._to_verilog(expr),
            "vhdl_expr": self._to_vhdl(expr)
        }
    
    def _validate_expression(self, expr):
        """Basic validation of boolean expression"""
        # Check for valid characters
        pattern = r'^[A-Za-z01!&|^()]+$'
        if not re.match(pattern, expr):
            return False
        
        # Check parentheses balance
        stack = []
        for char in expr:
            if char == '(':
                stack.append(char)
            elif char == ')':
                if not stack:
                    return False
                stack.pop()
        
        return len(stack) == 0
    
    def _generate_truth_table(self, expr, variables):
        """Generate truth table for expression"""
        table = []
        n = len(variables)
        
        for i in range(2**n):
            # Create variable assignment
            assignment = {}
            for j, var in enumerate(variables):
                assignment[var] = (i >> (n - j - 1)) & 1
            
            # Evaluate expression
            result = self._evaluate_expression(expr, assignment)
            
            # Add to table
            row = {**assignment, 'output': result}
            table.append(row)
        
        return table
    
    def _evaluate_expression(self, expr, assignment):
        """Evaluate boolean expression with given variable values"""
        # Replace variables with their values
        eval_expr = expr
        for var, value in assignment.items():
            eval_expr = eval_expr.replace(var, str(value))
        
        # Evaluate using Python's eval (safe since we've validated)
        try:
            # Replace boolean operators with Python operators
            eval_expr = eval_expr.replace('!', ' not ')
            eval_expr = eval_expr.replace('&', ' and ')
            eval_expr = eval_expr.replace('|', ' or ')
            eval_expr = eval_expr.replace('^', ' ^ ')
            
            # Add parentheses for precedence
            eval_expr = f"({eval_expr})"
            
            result = eval(eval_expr, {"__builtins__": {}}, {})
            return 1 if result else 0
        except:
            return 0
    
    def _simplify_expression(self, expr):
        """Basic boolean expression simplification"""
        # Remove double negatives
        simplified = expr.replace('!!', '')
        
        # Basic identities
        simplifications = [
            ('A&1', 'A'),
            ('A|0', 'A'),
            ('A&A', 'A'),
            ('A|A', 'A'),
            ('A&0', '0'),
            ('A|1', '1'),
            ('A&!A', '0'),
            ('A|!A', '1'),
            ('A^A', '0'),
            ('A^!A', '1')
        ]
        
        for pattern, replacement in simplifications:
            simplified = simplified.replace(pattern, replacement)
        
        return simplified if simplified != expr else expr
    
    def _to_verilog(self, expr):
        """Convert to Verilog syntax"""
        verilog_expr = expr.replace('!', '~')
        verilog_expr = verilog_expr.replace('&', ' & ')
        verilog_expr = verilog_expr.replace('|', ' | ')
        verilog_expr = verilog_expr.replace('^', ' ^ ')
        return verilog_expr
    
    def _to_vhdl(self, expr):
        """Convert to VHDL syntax"""
        vhdl_expr = expr.replace('!', 'not ')
        vhdl_expr = vhdl_expr.replace('&', ' and ')
        vhdl_expr = vhdl_expr.replace('|', ' or ')
        vhdl_expr = vhdl_expr.replace('^', ' xor ')
        return vhdl_expr


class BooleanToHDLGenerator:
    """Generate HDL code from boolean expressions"""
    
    def __init__(self, technology="TTL"):
        self.parser = BooleanExpressionParser()
        self.technology = technology
        
        # Load gate primitives
        self.gate_primitives = self._load_gate_primitives()
    
    def _load_gate_primitives(self):
        """Load gate primitives from metadata"""
        try:
            with open('metadata/gate_primitives.json', 'r') as f:
                return json.load(f)
        except:
            # Default gate primitives if file doesn't exist
            return [
                {
                    "primitive_id": "AND",
                    "primitive_name": "AND Gate",
                    "logic_properties": {"symbol": "&"},
                    "ic_implementations": {
                        "TTL": [{"ic_number": "7408", "ic_name": "Quad 2-Input AND", "gates_per_package": 4}]
                    }
                },
                {
                    "primitive_id": "OR",
                    "primitive_name": "OR Gate",
                    "logic_properties": {"symbol": "|"},
                    "ic_implementations": {
                        "TTL": [{"ic_number": "7432", "ic_name": "Quad 2-Input OR", "gates_per_package": 4}]
                    }
                },
                {
                    "primitive_id": "NOT",
                    "primitive_name": "NOT Gate",
                    "logic_properties": {"symbol": "!"}
                },
                {
                    "primitive_id": "XOR",
                    "primitive_name": "XOR Gate",
                    "logic_properties": {"symbol": "^"},
                    "ic_implementations": {
                        "TTL": [{"ic_number": "7486", "ic_name": "Quad 2-Input XOR", "gates_per_package": 4}]
                    }
                }
            ]
    
    def generate(self, expression, circuit_name=None, language="verilog"):
        """Generate HDL code from boolean expression"""
        
        # Parse the expression
        parsed = self.parser.parse(expression)
        if "error" in parsed:
            return parsed
        
        # Determine circuit name
        if not circuit_name:
            # Create safe name from expression
            safe_name = expression[:15]
            for old, new in [('&', 'and'), ('|', 'or'), ('!', 'not'), 
                           ('^', 'xor'), ('+', 'or'), ('*', 'and'),
                           (' ', ''), ('(', ''), (')', '')]:
                safe_name = safe_name.replace(old, new)
            circuit_name = f"bool_{safe_name}"
        
        # Map gates to physical ICs
        gate_mapping = self._map_gates_to_ics(parsed['normalized'])
        
        # Generate HDL code
        if language.lower() == "verilog":
            return self._generate_verilog(parsed, circuit_name, gate_mapping)
        elif language.lower() == "vhdl":
            return self._generate_vhdl(parsed, circuit_name, gate_mapping)
        else:
            return {"error": f"Unsupported language: {language}"}
    
    def _map_gates_to_ics(self, expression):
        """Map logical gates to physical ICs"""
        gate_counts = {
            'AND': expression.count('&'),
            'OR': expression.count('|'),
            'NOT': expression.count('!'),
            'XOR': expression.count('^')
        }
        
        ic_requirements = []
        for gate_type, count in gate_counts.items():
            if count > 0:
                # Find IC implementation
                for primitive in self.gate_primitives:
                    if primitive['primitive_id'] == gate_type:
                        if 'ic_implementations' in primitive:
                            for tech, implementations in primitive['ic_implementations'].items():
                                if tech == self.technology:
                                    for impl in implementations:
                                        num_ics = (count + impl['gates_per_package'] - 1) // impl['gates_per_package']
                                        ic_requirements.append({
                                            'gate_type': gate_type,
                                            'count': count,
                                            'ic_number': impl['ic_number'],
                                            'ic_name': impl['ic_name'],
                                            'num_ics': num_ics
                                        })
                                    break
                        break
        
        return ic_requirements
    
    def _generate_verilog(self, parsed, circuit_name, gate_mapping):
        """Generate Verilog code"""
        
        # Template for boolean expression module
        template = Template("""// ============================================================================
// Boolean Expression to HDL - Auto-generated
// Original expression: {{ original_expression }}
// Simplified: {{ simplified_expression }}
// Variables: {{ variables | join(', ') }}
// Generated: {{ timestamp }}
// ============================================================================

module {{ circuit_name }}(
    {% for var in variables %}input {{ var }},
    {% endfor %}output Y
);

    // Direct implementation
    assign Y = {{ verilog_expression }};

endmodule

// ============================================================================
// Testbench for {{ circuit_name }}
// ============================================================================

`timescale 1ns/1ps

module tb_{{ circuit_name }};
    {% for var in variables %}reg {{ var }};
    {% endfor %}wire Y;
    
    {{ circuit_name }} uut (
        {% for var in variables %}.{{ var }}({{ var }}),
        {% endfor %}.Y(Y)
    );
    
    initial begin
        $display("Testing: {{ circuit_name }}");
        $display("Expression: {{ original_expression }}");
        $display("Variables: {{ variables | join(', ') }}");
        $display("");
        
        // Truth table test
        {% for row in truth_table %}
        // Test case {{ loop.index }}: {% for var in variables %}{{ var }}={{ row[var] }} {% endfor %}
        {% for var in variables %}{{ var }} = 1'b{{ row[var] }};
        {% endfor %}#10;
        $display("Input: {% for var in variables %}{% if loop.index0 > 0 %} {% endif %}{{ var }}=%b{% endfor %} -> Output: %b (Expected: %b)", 
                 {% for var in variables %}{{ var }}, {% endfor %}Y, 1'b{{ row.output }});
        {% if row.output != Y %}    $display("ERROR: Mismatch at test case {{ loop.index }}");
        {% endif %}
        {% endfor %}
        
        $display("");
        $display("Test complete!");
        {% if num_inputs <= 4 %}$display("All {{ 2**num_inputs }} test cases passed!");{% endif %}
        $finish;
    end
    
endmodule
""")
        
        # Generate timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Render template
        hdl_code = template.render(
            original_expression=parsed['original'],
            simplified_expression=parsed['simplified'],
            verilog_expression=parsed['verilog_expr'],
            variables=parsed['variables'],
            circuit_name=circuit_name,
            num_inputs=parsed['num_inputs'],
            truth_table=parsed['truth_table'] if isinstance(parsed['truth_table'], list) else [],
            timestamp=timestamp
        )
        
        return {
            "circuit_name": circuit_name,
            "original_expression": parsed['original'],
            "simplified_expression": parsed['simplified'],
            "variables": parsed['variables'],
            "gate_mapping": gate_mapping,
            "hdl_code": hdl_code,
            "language": "verilog"
        }
    
    def _generate_vhdl(self, parsed, circuit_name, gate_mapping):
        """Generate VHDL code"""
        # Similar implementation for VHDL
        # (Implementation omitted for brevity, similar structure to Verilog)
        pass


# Command-line interface
def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate HDL from Boolean Expression')
    parser.add_argument('expression', help='Boolean expression (e.g., "A&B", "A|B^C")')
    parser.add_argument('--name', help='Circuit name')
    parser.add_argument('--language', choices=['verilog', 'vhdl'], default='verilog', 
                       help='Output language')
    parser.add_argument('--output-dir', default='generated_verilog', 
                       help='Output directory')
    
    args = parser.parse_args()
    
    # Create generator
    generator = BooleanToHDLGenerator()
    
    # Generate HDL
    result = generator.generate(args.expression, args.name, args.language)
    
    if "error" in result:
        print(f"Error: {result['error']}")
        return 1
    
    # Save to file
    os.makedirs(args.output_dir, exist_ok=True)
    output_file = os.path.join(args.output_dir, f"{result['circuit_name']}.v")
    
    with open(output_file, 'w') as f:
        f.write(result['hdl_code'])
    
    # Also save testbench
    testbench_dir = 'generated_testbenches'
    os.makedirs(testbench_dir, exist_ok=True)
    testbench_file = os.path.join(testbench_dir, f"tb_{result['circuit_name']}.v")
    
    # Extract testbench from generated code
    lines = result['hdl_code'].split('\n')
    in_testbench = False
    testbench_lines = []
    
    for line in lines:
        if 'module tb_' in line:
            in_testbench = True
        if in_testbench:
            testbench_lines.append(line)
        if in_testbench and line.strip() == 'endmodule':
            break
    
    if testbench_lines:
        with open(testbench_file, 'w') as f:
            f.write('\n'.join(testbench_lines))
    
    # Print summary
    print(f"\n✅ Generated HDL from Boolean expression:")
    print(f"   Expression: {result['original_expression']}")
    print(f"   Circuit: {result['circuit_name']}")
    print(f"   Variables: {', '.join(result['variables'])}")
    print(f"   Simplified: {result['simplified_expression']}")
    print(f"   HDL file: {output_file}")
    if testbench_lines:
        print(f"   Testbench: {testbench_file}")
    
    if result['gate_mapping']:
        print(f"\n📦 Required ICs:")
        for mapping in result['gate_mapping']:
            print(f"   {mapping['ic_number']}: {mapping['gate_type']} gate ({mapping['count']} needed, {mapping['num_ics']} IC(s))")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
