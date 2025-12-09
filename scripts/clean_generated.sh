#!/bin/bash
# Clean generated files

echo "Cleaning generated files..."

# Remove generated directories
rm -rf generated_verilog/
rm -rf generated_vhdl/
rm -rf testbenches/
rm -rf output/
rm -rf test_output/

# Remove any stray generated files
find . -name "*.v" -type f -delete
find . -name "*.vhd" -type f -delete
find . -name "*.vcd" -type f -delete
find . -name "*.log" -type f -delete

echo "Cleanup complete!"
