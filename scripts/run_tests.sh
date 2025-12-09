#!/bin/bash
# Run tests and generate example outputs

echo "Running IC HDL Generator tests..."

# Create test directories
mkdir -p test_output/verilog
mkdir -p test_output/vhdl

# Test 1: Generate Verilog for basic ICs
echo "Test 1: Generating basic ICs in Verilog..."
python template_engine.py generate 7400 --output-dir test_output/verilog
python template_engine.py generate 7404 --output-dir test_output/verilog
python template_engine.py generate 7474 --output-dir test_output/verilog

# Test 2: Generate VHDL
echo "Test 2: Generating basic ICs in VHDL..."
python template_engine.py generate 7400 --language vhdl --output-dir test_output/vhdl

# Test 3: List all ICs
echo "Test 3: Listing all ICs..."
python template_engine.py list > test_output/ic_list.txt

# Test 4: Testbench generation
echo "Test 4: Generating testbenches..."
mkdir -p test_output/testbenches
python template_engine.py testbench 7400 --output-dir test_output/testbenches

echo "Tests completed!"
echo "Output in test_output/"
