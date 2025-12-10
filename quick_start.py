#!/usr/bin/env python3
"""
Quick Start Script - Sets up everything automatically
"""

import os
import json

def create_directories():
    """Create all required directories"""
    dirs = [
        'hdl_templates/verilog/combinational/basic_gates',
        'hdl_templates/verilog/combinational/decoders',
        'hdl_templates/verilog/combinational/multiplexers',
        'hdl_templates/verilog/combinational/encoders',
        'hdl_templates/verilog/combinational/special',
        'hdl_templates/verilog/sequential/flip_flops',
        'hdl_templates/verilog/sequential/counters',
        'hdl_templates/verilog/transceivers',
        'hdl_templates/verilog/special_analog',
        'testbench_templates/verilog',
        'generated_verilog',
        'examples',
        'scripts',
    ]
    
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
        print(f"Created: {dir_path}/")
    
    print("\n✅ Directory structure created!")

def check_dependencies():
    """Check if required packages are installed"""
    try:
        import jinja2
        print("✅ Jinja2 is installed")
        return True
    except ImportError:
        print("❌ Jinja2 not installed. Run: pip install jinja2")
        return False

def create_example():
    """Create example usage script"""
    example_code = '''#!/usr/bin/env python3
"""
Example: Generate Verilog for 7400 NAND gate
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Method 1: Using template_engine.py
print("Method 1: Using template_engine.py")
print("=" * 50)
os.system("python template_engine.py list")
print()
os.system("python template_engine.py generate 7400 --output-dir examples/output")

# Method 2: Using working_generator.py  
print("\nMethod 2: Using working_generator.py")
print("=" * 50)
os.system("python working_generator.py generate 7474 --output-dir examples/output")

print("\n✅ Examples generated in examples/output/")
'''

    with open('examples/example_usage.py', 'w') as f:
        f.write(example_code)
    
    print("✅ Created: examples/example_usage.py")

def main():
    print("IC HDL Generator - Quick Start")
    print("=" * 60)
    
    create_directories()
    
    if check_dependencies():
        create_example()
        
        print("\n" + "=" * 60)
        print("QUICK START COMPLETE!")
        print("\nNext steps:")
        print("1. Run: python template_engine.py list")
        print("2. Run: python template_engine.py generate 7400")
        print("3. Run: python working_generator.py generate-all")
        print("\nCheck examples/ for more usage examples")
    else:
        print("\nPlease install dependencies first:")
        print("pip install jinja2")

if __name__ == "__main__":
    main()
