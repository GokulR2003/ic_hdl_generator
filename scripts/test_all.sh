#!/bin/bash
# Test all IC generation

echo "Testing IC HDL Generator..."
echo "================================"

# Clean old files
rm -rf generated_verilog generated_verilog_fixed

# Test 1: List ICs
echo "Test 1: Listing ICs"
python template_engine.py list

# Test 2: Generate single IC
echo -e "\nTest 2: Generating 7400"
python template_engine.py generate 7400

# Test 3: Generate all with basic generator
echo -e "\nTest 3: Generating all ICs (basic)"
python template_engine.py generate-all

# Test 4: Generate all with improved generator
echo -e "\nTest 4: Generating all ICs (improved)"
python working_generator.py generate-all

# Test 5: Check results
echo -e "\nTest 5: Checking generated files"
echo "Basic generator: $(ls generated_verilog/*.v 2>/dev/null | wc -l) files"
echo "Improved generator: $(ls generated_verilog_fixed/*.v 2>/dev/null | wc -l) files"

# Show file sizes
echo -e "\nFile sizes in improved generator:"
ls -la generated_verilog_fixed/*.v | head -5

echo -e "\n✅ Testing complete!"
