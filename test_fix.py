# Create test_fix.py
#!/usr/bin/env python3
"""
Test script for the fixed circuit generator
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from circuit_generator_advanced import (
    convert_ic_list_to_dict,
    generate_circuit_from_ics,
    CIRCUIT_CONFIGS,
    IC_DATABASE
)

def test_full_adder():
    print("Testing Full Adder Generation...")
    
    # Convert IC database to dictionary
    ic_db = convert_ic_list_to_dict(IC_DATABASE)
    
    # Generate full adder
    circuit_name = "full_adder_1bit"
    circuit_config = CIRCUIT_CONFIGS[circuit_name]
    
    try:
        verilog_code, testbench_code = generate_circuit_from_ics(
            circuit_name,
            circuit_config,
            ic_db
        )
        
        print("✅ Successfully generated full adder!")
        print("\n=== Generated Verilog Code (first 20 lines) ===")
        lines = verilog_code.split('\n')
        for i in range(min(20, len(lines))):
            print(lines[i])
        
        # Save to file
        os.makedirs("generated_circuits", exist_ok=True)
        with open("generated_circuits/full_adder_1bit.v", "w") as f:
            f.write(verilog_code)
        
        with open("generated_circuits/tb_full_adder_1bit.v", "w") as f:
            f.write(testbench_code)
        
        print(f"\n✅ Files saved to generated_circuits/")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def test_all_circuits():
    print("\n=== Testing All Circuits ===")
    
    from circuit_generator_advanced import generate_all_circuits
    
    ic_db = convert_ic_list_to_dict(IC_DATABASE)
    generated = generate_all_circuits(ic_db)
    
    print(f"\n✅ Generated {len(generated)} circuits:")
    for circuit in generated:
        print(f"  - {circuit}")

if __name__ == "__main__":
    print("=== Testing Fixed Circuit Generator ===")
    
    # Test 1: Full adder
    test_full_adder()
    
    # Test 2: All circuits
    # Uncomment to test all
    # test_all_circuits()
