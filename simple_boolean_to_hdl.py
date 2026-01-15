# simple_boolean_to_hdl.py
from simple_boolean_parser import SimpleBooleanParser

class SimpleBooleanToHDLGenerator:
    def __init__(self, technology="TTL"):
        self.parser = SimpleBooleanParser()
    
    def generate(self, expression, circuit_name=None):
        parsed = self.parser.parse(expression)
        if "error" in parsed:
            return parsed
        
        if not circuit_name:
            circuit_name = f"bool_{expression[:10].replace('&','and').replace('|','or').replace('!','not').replace('^','xor')}"
        
        # Simple conversion
        verilog_expr = expression.replace('&', ' && ').replace('|', ' || ').replace('!', ' ~').replace('^', ' ^ ')
        
        hdl_code = f"""
module {circuit_name}(
    input {', '.join(parsed['variables'])},
    output Y
);
    assign Y = {verilog_expr};
endmodule
"""
        
        testbench = self._generate_testbench(circuit_name, parsed['variables'])
        
        return {
            "circuit_name": circuit_name,
            "original_expression": expression,
            "simplified_expression": expression,
            "variables": parsed['variables'],
            "hdl_code": hdl_code.strip(),
            "testbench": testbench
        }
    
    def _generate_testbench(self, name, inputs):
        return f"""
`timescale 1ns/1ps

module tb_{name};
    reg {', '.join(inputs)};
    wire Y;
    
    {name} uut ({', '.join(['.' + i + '(' + i + ')' for i in inputs])}, .Y(Y));
    
    initial begin
        $display("Testing {name}");
        // Add test cases here
        $finish;
    end
endmodule
"""
