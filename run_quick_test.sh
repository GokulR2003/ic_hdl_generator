#!/bin/bash
# Quick test of the complete system

echo "IC HDL Generator - Complete System Test"
echo "========================================"

# Clean old outputs
echo "1. Cleaning old outputs..."
rm -rf generated_verilog generated_vhdl generated_testbenches examples/output

# Run setup
echo "2. Running setup..."
python setup_complete.py

# Test basic functionality
echo -e "\n3. Testing basic functionality..."
echo "3.1 Listing supported ICs:"
python advanced_generator.py list-supported

echo -e "\n3.2 Generating Verilog for 7400:"
python advanced_generator.py generate 7400 --language verilog

echo -e "\n3.3 Generating testbench for 7400:"
python advanced_generator.py testbench 7400

echo -e "\n3.4 Generating VHDL for 7474:"
python advanced_generator.py generate 7474 --language vhdl

# Test batch generation
echo -e "\n4. Testing batch generation..."
echo "4.1 Generating all Verilog ICs:"
python advanced_generator.py generate-all --language verilog

echo -e "\n4.2 Generating all testbenches:"
python advanced_generator.py testbench-all

# Check results
echo -e "\n5. Checking results..."
echo "Verilog files generated: $(ls generated_verilog/*.v 2>/dev/null | wc -l)"
echo "VHDL files generated: $(ls generated_vhdl/*.vhd 2>/dev/null | wc -l)"
echo "Testbenches generated: $(ls generated_testbenches/*.v 2>/dev/null | wc -l)"

# Show sample files
echo -e "\n6. Sample generated files:"
ls -la generated_verilog/IC_7400.v generated_vhdl/IC_7474.vhd generated_testbenches/tb_7400.v 2>/dev/null

echo -e "\n✅ Test complete!"
echo -e "\nTo run the full example:"
echo "python examples/advanced_example.py"
