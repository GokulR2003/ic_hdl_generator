#!/usr/bin/env python3
"""
Example usage of the IC HDL Generator
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.hdl_generator import HDLGenerator

def main():
    """Run examples"""
    print("IC HDL Generator - Examples")
    print("=" * 50)
    
    # Initialize generator
    print("\n1. Initializing generator...")
    gen = HDLGenerator()
    
    # Example 1: Generate single IC
    print("\n2. Generating Verilog for 7400...")
    try:
        verilog_code = gen.generate_hdl('7400', 'verilog')
        print(f"Generated {len(verilog_code)} characters")
        print("\nFirst few lines:")
        print("-" * 40)
        for line in verilog_code.split('\n')[:10]:
            print(line)
        print("...")
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 2: Generate all ICs
    print("\n3. Generating all ICs in Verilog...")
    gen.generate_all('verilog', 'examples/output/verilog')
    
    # Example 3: Generate all in VHDL
    print("\n4. Generating all ICs in VHDL...")
    gen.generate_all('vhdl', 'examples/output/vhdl')
    
    # Example 4: List ICs
    print("\n5. Listing available ICs...")
    # This would normally print, but we'll just show count
    print(f"Total ICs in database: {len(gen.metadata)}")
    
    print("\n" + "=" * 50)
    print("Examples completed!")
    print("Check 'examples/output/' for generated files")

if __name__ == "__main__":
    main()
