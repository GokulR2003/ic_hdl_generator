#!/bin/bash
# complete_setup.sh - Complete IC HDL Generator Setup and Demo
# ============================================================
# Author: Gokul R
# Email: gokulr200305@gmail.com
# Phone: +91 90929 43337

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "\n${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${NC}${YELLOW}         IC HDL GENERATOR - COMPLETE SETUP         ${NC}${BLUE}║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
    echo -e "${YELLOW}Author: Gokul R${NC}"
    echo -e "${YELLOW}Email: gokulr200305@gmail.com${NC}"
    echo -e "${YELLOW}Phone: +91 90929 43337${NC}"
    echo ""
}

print_step() {
    echo -e "\n${GREEN}▶ Step $1: $2${NC}"
    echo "──────────────────────────────────────────────────────────────"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# ============================================================================
# START SETUP
# ============================================================================
clear
print_header

# ============================================================================
# STEP 1: INSTALL DEPENDENCIES
# ============================================================================
print_step "1" "Installing Dependencies"

echo "Updating package list..."
sudo apt-get update > /dev/null 2>&1
print_success "Package list updated"

echo "Installing Python3 and pip3..."
sudo apt-get install -y python3 python3-pip > /dev/null 2>&1
print_success "Python3 and pip3 installed"

echo "Installing Icarus Verilog (iverilog) for simulation..."
sudo apt-get install -y iverilog > /dev/null 2>&1
print_success "Icarus Verilog installed"

echo "Installing Jinja2 template engine..."
pip3 install jinja2 > /dev/null 2>&1
print_success "Jinja2 installed"

# Verify installations
echo "Verifying installations..."
python3 --version
pip3 --version | head -1
iverilog -v 2>&1 | head -1
python3 -c "import jinja2; print(f'Jinja2: {jinja2.__version__}')"

# ============================================================================
# STEP 2: SETUP DIRECTORIES AND TEMPLATES
# ============================================================================
print_step "2" "Setting up Project Structure"

echo "Running setup_complete.py..."
python3 setup_complete.py
print_success "Project structure created"

# ============================================================================
# STEP 3: LIST SUPPORTED ICS
# ============================================================================
print_step "3" "Listing Supported ICs"

echo "IC Support Matrix:"
python3 advanced_generator.py list-supported

# ============================================================================
# STEP 4: GENERATE ALL VERILOG ICS
# ============================================================================
print_step "4" "Generating All Verilog ICs"

echo "Generating Verilog for all ICs..."
python3 advanced_generator.py generate-all --language verilog
print_success "Verilog ICs generated"

# Count generated files
verilog_count=$(find generated_verilog -name "*.v" -type f 2>/dev/null | wc -l)
echo "Generated $verilog_count Verilog files"

# ============================================================================
# STEP 5: GENERATE ALL VHDL ICS
# ============================================================================
print_step "5" "Generating All VHDL ICs"

echo "Generating VHDL for all ICs..."
python3 advanced_generator.py generate-all --language vhdl
print_success "VHDL ICs generated"

# Count generated files
vhdl_count=$(find generated_vhdl -name "*.vhd" -type f 2>/dev/null | wc -l)
echo "Generated $vhdl_count VHDL files"

# ============================================================================
# STEP 6: GENERATE ALL TESTBENCHES
# ============================================================================
print_step "6" "Generating All Testbenches"

echo "Generating testbenches for all ICs..."
python3 advanced_generator.py generate-all --testbenches
print_success "Testbenches generated"

# Count generated testbenches
tb_count=$(find generated_testbenches -name "*.v" -type f 2>/dev/null | wc -l)
echo "Generated $tb_count testbench files"

# ============================================================================
# STEP 7: CIRCUIT COMPOSITION
# ============================================================================
print_step "7" "Circuit Composition Setup"

echo "Listing available circuits..."
python3 circuit_generator_advanced.py list

echo "Generating all circuits..."
python3 circuit_generator_advanced.py generate-all
print_success "All circuits generated"

# Count generated circuits
circuit_count=$(find generated_circuits -name "*.v" -type f 2>/dev/null | wc -l)
echo "Generated $circuit_count circuit files"

# ============================================================================
# STEP 8: BOOLEAN EXPRESSION DEMO
# ============================================================================
print_step "8" "Boolean Expression to HDL Demo"

# Create boolean_to_hdl.py if it doesn't exist
if [ ! -f "boolean_to_hdl.py" ]; then
    print_info "Creating boolean_to_hdl.py..."
    cat > boolean_to_hdl.py << 'EOF'
#!/usr/bin/env python3
"""Simple Boolean to HDL Generator"""
import sys
import os

def generate_boolean_hdl(expression, name="bool_circuit"):
    """Generate simple HDL from boolean expression"""
    # Extract variables
    variables = sorted(set(c for c in expression if c.isalpha()))
    
    verilog_code = f"""// Boolean Expression: {expression}
module {name}(
    input {', '.join(variables)},
    output Y
);
    assign Y = {expression.replace('&', ' && ').replace('|', ' || ').replace('^', ' ^ ').replace('!', '~')};
endmodule
"""
    
    # Create directories
    os.makedirs('generated_verilog', exist_ok=True)
    os.makedirs('generated_testbenches', exist_ok=True)
    
    # Save module
    with open(f'generated_verilog/{name}.v', 'w') as f:
        f.write(verilog_code)
    
    # Generate testbench
    tb_code = f"""// Testbench for {name}
`timescale 1ns/1ps
module tb_{name};
    reg {', '.join(variables)};
    wire Y;
    
    {name} uut({', '.join(['.' + v + '(' + v + ')' for v in variables])}, .Y(Y));
    
    initial begin
        $display("Testing {name}: {expression}");
        // Test all combinations
        for (int i = 0; i < {2**len(variables)}; i++) begin
            {create_assignments(variables)}
            #10;
            $display("Input: {format_string(variables)} -> Output: %b", Y);
        end
        $display("Test complete!");
        $finish;
    end
endmodule
"""
    
    with open(f'generated_testbenches/tb_{name}.v', 'w') as f:
        f.write(tb_code)
    
    return name

def create_assignments(variables):
    """Create testbench assignments"""
    lines = []
    for i, var in enumerate(variables):
        lines.append(f"{var} = i[{len(variables)-i-1}];")
    return "\n            ".join(lines)

def format_string(variables):
    """Create format string for display"""
    return " ".join(["%b" for _ in variables])

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 boolean_to_hdl.py <expression> [--name circuit_name]")
        sys.exit(1)
    
    expression = sys.argv[1]
    name = "bool_circuit"
    
    if "--name" in sys.argv:
        idx = sys.argv.index("--name")
        if idx + 1 < len(sys.argv):
            name = sys.argv[idx + 1]
    
    circuit_name = generate_boolean_hdl(expression, name)
    print(f"Generated: {circuit_name}.v")
    print(f"Testbench: tb_{circuit_name}.v")
EOF
    print_success "boolean_to_hdl.py created"
fi

# Generate boolean expression examples
echo "Generating boolean expression examples..."
python3 boolean_to_hdl.py "A&B" --name demo_and
python3 boolean_to_hdl.py "A|B" --name demo_or
python3 boolean_to_hdl.py "A^B" --name demo_xor
python3 boolean_to_hdl.py "!(A&B)" --name demo_nand
python3 boolean_to_hdl.py "(A&B)|(C&D)" --name demo_complex
print_success "Boolean expression examples generated"

# ============================================================================
# STEP 9: DEMO SPECIFIC GENERATIONS
# ============================================================================
print_step "9" "Demo Specific Generations"

echo "Generating specific IC with all options (7400)..."
python3 advanced_generator.py generate 7400 --language verilog --language vhdl --testbenches
print_success "7400 generated in both languages with testbench"

echo "Generating specific circuit (full_adder_1bit)..."
python3 circuit_generator_advanced.py generate full_adder_1bit
print_success "Full adder generated"

# ============================================================================
# STEP 10: VERIFICATION AND SUMMARY
# ============================================================================
print_step "10" "Verification and Summary"

echo "Checking generated files..."
echo "──────────────────────────────────────────────────────────────"

# List all generated directories and files
echo "Generated Directories:"
ls -la | grep generated_

echo -e "\nFile Counts:"
echo "Verilog ICs:      $(find generated_verilog -name '*.v' -type f 2>/dev/null | wc -l)"
echo "VHDL ICs:         $(find generated_vhdl -name '*.vhd' -type f 2>/dev/null | wc -l)"
echo "Testbenches:      $(find generated_testbenches -name '*.v' -type f 2>/dev/null | wc -l)"
echo "Circuits:         $(find generated_circuits -name '*.v' -type f 2>/dev/null | wc -l)"
echo "Boolean Demos:    $(find generated_verilog -name 'demo_*.v' -type f 2>/dev/null | wc -l)"

echo -e "\nTotal Files Generated: $(find generated_* -name '*.v' -o -name '*.vhd' 2>/dev/null | wc -l)"

echo -e "\nDisk Usage:"
du -sh generated_* 2>/dev/null || echo "No generated directories found"

# ============================================================================
# STEP 11: SIMULATION TEST (Optional)
# ============================================================================
print_step "11" "Simulation Test (Optional)"

read -p "Do you want to run a simulation test? (y/n): " run_sim

if [[ $run_sim == "y" || $run_sim == "Y" ]]; then
    echo "Compiling and simulating 7400 testbench..."
    
    if [ -f "generated_testbenches/tb_7400.v" ]; then
        # Compile
        iverilog -o sim_7400 generated_testbenches/tb_7400.v generated_verilog/IC_7400.v 2>&1
        
        if [ $? -eq 0 ]; then
            echo "Simulation output:"
            vvp sim_7400 2>&1 | head -20
            print_success "Simulation completed successfully"
            rm -f sim_7400
        else
            print_error "Compilation failed"
        fi
    else
        print_error "Testbench file not found"
    fi
fi

# ============================================================================
# COMPLETION
# ============================================================================
echo -e "\n${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${NC}${YELLOW}               SETUP COMPLETED SUCCESSFULLY!               ${NC}${BLUE}║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"

echo -e "\n${GREEN}✅ All commands executed successfully!${NC}"
echo ""
echo "${YELLOW}📁 GENERATED CONTENT:${NC}"
echo "  • generated_verilog/     - $(find generated_verilog -name '*.v' -type f 2>/dev/null | wc -l) Verilog files"
echo "  • generated_vhdl/        - $(find generated_vhdl -name '*.vhd' -type f 2>/dev/null | wc -l) VHDL files"
echo "  • generated_testbenches/ - $(find generated_testbenches -name '*.v' -type f 2>/dev/null | wc -l) testbenches"
echo "  • generated_circuits/    - $(find generated_circuits -name '*.v' -type f 2>/dev/null | wc -l) complex circuits"
echo ""
echo "${YELLOW}🔧 FEATURES INSTALLED:${NC}"
echo "  • Python 3 with Jinja2 templates"
echo "  • Icarus Verilog simulator"
echo "  • 20+ ICs in Verilog and VHDL"
echo "  • Automatic testbench generation"
echo "  • Circuit composition system"
echo "  • Boolean expression parser"
echo ""
echo "${YELLOW}🚀 READY TO USE:${NC}"
echo "  Run the presentation script:"
echo "    $ bash presentation_script.sh"
echo ""
echo "${YELLOW}📞 CONTACT INFORMATION:${NC}"
echo "  📧 Email:   gokulr200305@gmail.com"
echo "  📱 Phone:   +91 90929 43337"
echo "  👨‍💻 Author:  Gokul R"
echo "  🔗 GitHub:  https://github.com/GokulR2003/ic_hdl_generator"
echo ""
echo "${GREEN}Thank you for using IC HDL Generator! 🎉${NC}"
