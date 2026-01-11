#!/bin/bash
# run_quick_test.sh - Final version

echo "=== IC HDL Generator Complete Test Suite ==="
echo ""

# 1. Setup
echo "[1/5] Running setup..."
python setup_complete.py

# 2. Generate individual ICs
echo "[2/5] Generating individual ICs..."
python advanced_generator.py generate-all --language verilog --testbenches
python advanced_generator.py generate-all --language vhdl

# 3. Generate advanced circuits
echo "[3/5] Generating advanced circuits..."
python circuit_generator_advanced.py

# 4. Create a combined simulation test
echo "[4/5] Creating simulation package..."
cat > test_simulation.sh << 'EOF'
#!/bin/bash
echo "=== Simulation Test ==="
cd generated_circuits_advanced

# Copy needed IC modules
cp ../generated_verilog/IC_7486.v .
cp ../generated_verilog/IC_7408.v .  
cp ../generated_verilog/IC_7432.v .

# Compile and simulate full adder
echo "Simulating full_adder_1bit..."
iverilog -o full_adder_sim full_adder_1bit.v full_adder_1bit_tb.sv IC_7486.v IC_7408.v IC_7432.v
vvp full_adder_sim

echo ""
echo "To view waveform: gtkwave full_adder_1bit.vcd"
EOF

chmod +x test_simulation.sh

# 5. Summary
echo "[5/5] Generated files summary:"
echo ""
echo "Individual ICs:"
echo "  Verilog: generated_verilog/ (20 files)"
echo "  VHDL:    generated_vhdl/ (20 files)"
echo "  Testbenches: generated_testbenches/ (20 files)"
echo ""
echo "Complex Circuits:"
ls -la generated_circuits_advanced/
echo ""
echo "=== Test Complete ==="
echo ""
echo "To run simulation test:"
echo "  ./test_simulation.sh"
