# quick_boolean_fix.py
#!/usr/bin/env python3
"""Quick fix for boolean expression demo in presentation"""

import os

def create_simple_boolean_demo():
    """Create simple boolean expression demo files"""
    
    print("Creating boolean expression demo files...")
    
    # Create demo boolean expression files
    expressions = [
        ("A&B", "demo_and"),
        ("A|B", "demo_or"),
        ("A^B", "demo_xor"),
        ("!(A&B)", "demo_nand"),
        ("(A&B)|(C&D)", "demo_complex")
    ]
    
    for expr, name in expressions:
        # Create simple verilog file
        verilog_code = f"""// Boolean Expression Demo
// Generated from: {expr}
module {name}(
    input {', '.join(sorted(set(c for c in expr if c.isalpha())))},
    output Y
);
    assign Y = {expr.replace('&', ' && ').replace('|', ' || ').replace('^', ' ^ ').replace('!', ' ~')};
endmodule
"""
        
        # Save to generated_verilog directory
        with open(f"generated_verilog/{name}.v", "w") as f:
            f.write(verilog_code)
        
        # Create testbench
        vars = sorted(set(c for c in expr if c.isalpha()))
        tb_code = f"""// Testbench for {name}
`timescale 1ns/1ps
module tb_{name};
    reg {', '.join(vars)};
    wire Y;
    
    {name} uut({', '.join(['.' + v + '(' + v + ')' for v in vars])}, .Y(Y));
    
    initial begin
        $display("Testing: {name}");
        $display("Expression: {expr}");
        
        // Test all combinations
        for (int i = 0; i < {2**len(vars)}; i++) begin
            {create_tb_assignments(vars)}
            #10;
            $display("Input: {create_tb_format(vars)} -> Output: %b", Y);
        end
        $display("Test complete!");
        $finish;
    end
endmodule
"""
        
        # Save testbench
        with open(f"generated_testbenches/tb_{name}.v", "w") as f:
            f.write(tb_code)
        
        print(f"✓ Created: {name}.v")

def create_tb_assignments(variables):
    """Create testbench assignment statements"""
    assignments = []
    for i, var in enumerate(variables):
        assignments.append(f"{var} = i[{len(variables)-i-1}];")
    return "\n            ".join(assignments)

def create_tb_format(variables):
    """Create testbench format string"""
    return " ".join([f"%b" for _ in variables])

def main():
    # Create directories if they don't exist
    os.makedirs("generated_verilog", exist_ok=True)
    os.makedirs("generated_testbenches", exist_ok=True)
    
    create_simple_boolean_demo()
    print("\n✅ Boolean expression demo files created successfully!")
    print("\nFiles created in:")
    print("  - generated_verilog/")
    print("  - generated_testbenches/")

if __name__ == "__main__":
    main()
