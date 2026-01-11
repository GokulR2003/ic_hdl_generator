# Create run_advanced_test.sh
#!/bin/bash

echo "=== Running Advanced Circuit Generator Test ==="
echo ""

# Step 1: Test the fixed generator
echo "Step 1: Testing circuit generator..."
python test_fix.py

echo ""
echo "Step 2: List supported circuits..."
python circuit_generator_advanced.py list

echo ""
echo "Step 3: Generate full adder..."
python circuit_generator_advanced.py generate full_adder_1bit

echo ""
echo "Step 4: Generate all circuits..."
python circuit_generator_advanced.py generate-all

echo ""
echo "=== Test Complete ==="
echo ""
echo "Generated circuits:"
ls -la generated_circuits/
