# create_final_verification.sh
#!/bin/bash
echo "=== Final Verification Script ==="
echo ""

echo "1. Testing Boolean Expression Support..."
python3 -c "
try:
    from simple_boolean_to_hdl import SimpleBooleanToHDLGenerator
    print('✓ Boolean modules loaded successfully')
    
    # Test generation
    gen = SimpleBooleanToHDLGenerator()
    result = gen.generate('A & B', 'test_and')
    if 'hdl_code' in result:
        print('✓ Boolean expression generation works')
        
        # Save test file
        with open('test_boolean_and.v', 'w') as f:
            f.write(result['hdl_code'])
        print('✓ Saved test file: test_boolean_and.v')
    else:
        print('✗ Generation failed:', result.get('error', 'Unknown'))
except ImportError as e:
    print('✗ Boolean modules not available:', e)
"

echo ""
echo "2. Testing Circuit Simulation..."
# Use the test simulation script
if [ -f "test_simulation.sh" ]; then
    ./test_simulation.sh
else
    echo "⚠ test_simulation.sh not found"
fi

echo ""
echo "3. Verifying Generated Files..."
echo "File counts:"
echo "------------"
echo "Verilog ICs: $(find generated_verilog -name "*.v" -type f 2>/dev/null | wc -l)"
echo "VHDL ICs: $(find generated_vhdl -name "*.vhd" -type f 2>/dev/null | wc -l)"
echo "Testbenches: $(find generated_testbenches -name "*.v" -type f 2>/dev/null | wc -l)"
echo "Circuits: $(find generated_circuits -name "*.v" -type f 2>/dev/null | wc -l)"

echo ""
echo "4. Sample Output Files..."
echo "First few lines of generated full adder:"
echo "----------------------------------------"
if [ -f "generated_circuits/full_adder_1bit.v" ]; then
    head -15 generated_circuits/full_adder_1bit.v
else
    echo "File not found"
fi

echo ""
echo "=== Verification Complete ==="
