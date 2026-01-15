# test_boolean_simple.py
#!/usr/bin/env python3
"""Simple test script for boolean expression demo"""

import subprocess
import os

def test_boolean_expressions():
    print("Testing Boolean Expression to HDL Generation")
    print("=" * 50)
    
    expressions = [
        ("A&B", "simple_and"),
        ("A|B", "simple_or"),
        ("A^B", "simple_xor"),
        ("!(A&B)", "nand_example"),
        ("A&B | C&D", "complex_and_or")
    ]
    
    for expr, name in expressions:
        print(f"\nGenerating: {expr} -> {name}")
        cmd = ["python3", "boolean_to_hdl.py", expr, "--name", name]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✓ Success: {name}")
                # Show first few lines of generated file
                if os.path.exists(f"generated_verilog/{name}.v"):
                    with open(f"generated_verilog/{name}.v", 'r') as f:
                        lines = f.readlines()[:15]
                        print("Generated code (first 15 lines):")
                        for line in lines:
                            print(f"  {line.rstrip()}")
            else:
                print(f"✗ Failed: {result.stderr}")
        except Exception as e:
            print(f"✗ Error: {e}")
    
    print("\n" + "=" * 50)
    print("Boolean expression test complete!")

if __name__ == "__main__":
    test_boolean_expressions()
