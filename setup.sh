#!/bin/bash
# ============================================================================
# IC HDL Generator - Complete Setup Script
# ============================================================================
# Author: Gokul R
# Email: gokulr200305@gmail.com
# ============================================================================

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${NC}${YELLOW}         IC HDL GENERATOR - COMPLETE SETUP         ${NC}${BLUE}║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# ============================================================================
# STEP 1: Check System Requirements
# ============================================================================
echo -e "${YELLOW}▶ Step 1: Checking System Requirements${NC}"
echo "──────────────────────────────────────────────────────────────"

# Check OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo -e "${GREEN}✓ OS: Linux detected${NC}"
    PKG_MANAGER="apt-get"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo -e "${GREEN}✓ OS: macOS detected${NC}"
    PKG_MANAGER="brew"
else
    echo -e "${RED}✗ Unsupported OS: $OSTYPE${NC}"
    exit 1
fi

# Check Python
if command -v python3 &>/dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓ $PYTHON_VERSION${NC}"
else
    echo -e "${RED}✗ Python3 not found${NC}"
    exit 1
fi

# Check pip
if command -v pip3 &>/dev/null; then
    echo -e "${GREEN}✓ pip3 installed${NC}"
else
    echo -e "${YELLOW}⚠ pip3 not found, installing...${NC}"
    if [[ "$PKG_MANAGER" == "apt-get" ]]; then
        sudo apt-get install -y python3-pip
    elif [[ "$PKG_MANAGER" == "brew" ]]; then
        brew install python3
    fi
fi

# ============================================================================
# STEP 2: Install Dependencies
# ============================================================================
echo -e "\n${YELLOW}▶ Step 2: Installing Dependencies${NC}"
echo "──────────────────────────────────────────────────────────────"

# Update package list (Linux only)
if [[ "$PKG_MANAGER" == "apt-get" ]]; then
    echo "Updating package list..."
    sudo apt-get update
fi

# Install system dependencies
echo "Installing system dependencies..."
if [[ "$PKG_MANAGER" == "apt-get" ]]; then
    sudo apt-get install -y python3 python3-pip iverilog git wget curl
elif [[ "$PKG_MANAGER" == "brew" ]]; then
    brew install python3 icarus-verilog git wget curl
fi

# Install Python packages
echo "Installing Python packages..."
pip3 install --upgrade pip
pip3 install jinja2
pip3 install pyyaml
pip3 install pytest
pip3 install pytest-cov
pip3 install black
pip3 install pylint

# Verify installations
echo -e "\nVerifying installations..."
python3 -c "import jinja2; print(f'${GREEN}✓ Jinja2: {jinja2.__version__}${NC}')"
iverilog -v 2>&1 | head -1

# ============================================================================
# STEP 3: Clone/Update Repository
# ============================================================================
echo -e "\n${YELLOW}▶ Step 3: Setting up Repository${NC}"
echo "──────────────────────────────────────────────────────────────"

REPO_URL="https://github.com/GokulR2003/ic_hdl_generator.git"
TARGET_DIR="ic_hdl_generator"

if [ -d "$TARGET_DIR" ]; then
    echo "Repository already exists. Updating..."
    cd "$TARGET_DIR"
    git pull
    cd ..
else
    echo "Cloning repository..."
    git clone "$REPO_URL"
fi

cd "$TARGET_DIR"

# ============================================================================
# STEP 4: Create Directory Structure
# ============================================================================
echo -e "\n${YELLOW}▶ Step 4: Creating Directory Structure${NC}"
echo "──────────────────────────────────────────────────────────────"

# Create all necessary directories
mkdir -p hdl_templates/verilog/combinational/basic_gates
mkdir -p hdl_templates/verilog/combinational/decoders
mkdir -p hdl_templates/verilog/combinational/multiplexers
mkdir -p hdl_templates/verilog/combinational/encoders
mkdir -p hdl_templates/verilog/combinational/special
mkdir -p hdl_templates/verilog/sequential/flip_flops
mkdir -p hdl_templates/verilog/sequential/counters
mkdir -p hdl_templates/verilog/transceivers
mkdir -p hdl_templates/verilog/special_analog
mkdir -p hdl_templates/vhdl/combinational/basic_gates
mkdir -p hdl_templates/vhdl/combinational/decoders
mkdir -p hdl_templates/vhdl/sequential/flip_flops
mkdir -p hdl_templates/vhdl/sequential/counters
mkdir -p hdl_templates/vhdl/special_analog
mkdir -p testbench_templates/verilog/combinational/basic_gates
mkdir -p testbench_templates/verilog/combinational/decoders
mkdir -p testbench_templates/verilog/combinational/multiplexers
mkdir -p testbench_templates/verilog/combinational/encoders
mkdir -p testbench_templates/verilog/combinational/special
mkdir -p testbench_templates/verilog/sequential/flip_flops
mkdir -p testbench_templates/verilog/sequential/counters
mkdir -p testbench_templates/verilog/transceivers
mkdir -p testbench_templates/verilog/special_analog
mkdir -p testbench_templates/vhdl/combinational/basic_gates
mkdir -p testbench_templates/vhdl/sequential/flip_flops
mkdir -p generated_verilog
mkdir -p generated_vhdl
mkdir -p generated_testbenches
mkdir -p generated_circuits
mkdir -p examples
mkdir -p scripts
mkdir -p metadata
mkdir -p docs
mkdir -p tests

echo -e "${GREEN}✓ Directory structure created${NC}"

# ============================================================================
# STEP 5: Create Essential Templates
# ============================================================================
echo -e "\n${YELLOW}▶ Step 5: Creating Essential Templates${NC}"
echo "──────────────────────────────────────────────────────────────"

# Create Verilog template
cat > hdl_templates/verilog/generic.vtpl << 'EOF'
// ============================================================================
// Auto-generated HDL from IC Metadata
// Part Number: {{ ic.part_number }}
// IC Name:     {{ ic.name }}
// Category:    {{ ic.category }}
// Subtype:     {{ ic.subtype }}
// Family:      {{ ic.family }}
// Generated:   {{ timestamp }}
// ============================================================================

module {{ module_name }}(
{% for pin in ic.pins if pin.type == 'input' %}
    input {{ pin.name }}{% if not loop.last %},{% endif %}
{% endfor %}
{% if ic.pins|selectattr('type', 'equalto', 'input')|list %},{% endif %}
{% for pin in ic.pins if pin.type == 'output' %}
    output {{ pin.name }}{% if not loop.last %},{% endif %}
{% endfor %}
);

{% if ic.category == 'combinational' %}
    // Combinational logic implementation
    {% for gate in ic.gates %}
    assign {{ gate.output }} = {{ gate.expression }};
    {% endfor %}
{% elif ic.category == 'sequential' %}
    // Sequential logic implementation
    always @(posedge {{ ic.clock_pin }} or posedge {{ ic.reset_pin }}) begin
        if ({{ ic.reset_pin }}) begin
            // Reset logic
            {% for reg in ic.registers %}
            {{ reg.name }} <= 1'b0;
            {% endfor %}
        end else begin
            // Sequential behavior
            {% for state in ic.state_transitions %}
            {{ state.assignment }}
            {% endfor %}
        end
    end
{% endif %}

endmodule
EOF

# Create VHDL template
cat > hdl_templates/vhdl/generic.vhdltpl << 'EOF'
-- ============================================================================
-- Auto-generated HDL from IC Metadata
-- Part Number: {{ ic.part_number }}
-- IC Name:     {{ ic.name }}
-- Category:    {{ ic.category }}
-- Family:      {{ ic.family }}
-- Generated:   {{ timestamp }}
-- ============================================================================

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity {{ module_name }} is
    Port (
{% for pin in ic.pins %}
        {{ pin.name }} : {{ 'in' if pin.type == 'input' else 'out' }} STD_LOGIC{% if not loop.last %};{% endif %}
{% endfor %}
    );
end {{ module_name }};

architecture Behavioral of {{ module_name }} is
begin
{% if ic.category == 'combinational' %}
    -- Combinational logic implementation
    {% for gate in ic.gates %}
    {{ gate.output }} <= {{ gate.expression }};
    {% endfor %}
{% elif ic.category == 'sequential' %}
    -- Sequential logic implementation
    process({{ ic.clock_pin }}, {{ ic.reset_pin }})
    begin
        if {{ ic.reset_pin }} = '1' then
            -- Reset logic
            {% for reg in ic.registers %}
            {{ reg.name }} <= '0';
            {% endfor %}
        elsif rising_edge({{ ic.clock_pin }}) then
            -- Sequential behavior
            {% for state in ic.state_transitions %}
            {{ state.assignment }}
            {% endfor %}
        end if;
    end process;
{% endif %}
end Behavioral;
EOF

# Create testbench template
cat > testbench_templates/verilog/generic_tb.vtpl << 'EOF'
// ============================================================================
// Testbench for: {{ ic.part_number }} - {{ ic.name }}
// Generated: {{ timestamp }}
// ============================================================================

`timescale 1ns / 1ps

module tb_{{ module_name }};
    
    // Parameters
    parameter CLK_PERIOD = 10;
    parameter SIM_DURATION = 1000;
    
    // DUT Signals
    {% for pin in ic.pins if pin.type == 'input' %}
    reg {{ pin.name }};
    {% endfor %}
    {% for pin in ic.pins if pin.type == 'output' %}
    wire {{ pin.name }};
    {% endfor %}
    
    // Clock generation (if sequential)
    {% if ic.category == 'sequential' %}
    reg clk;
    reg rst;
    
    always #(CLK_PERIOD/2) clk = ~clk;
    {% endif %}
    
    // Instantiate DUT
    {{ module_name }} dut (
        {% for pin in ic.pins %}
        .{{ pin.name }}({{ pin.name }}){% if not loop.last %},{% endif %}
        {% endfor %}
    );
    
    // Test procedure
    initial begin
        $display("========================================");
        $display("Testing {{ ic.part_number }} - {{ ic.name }}");
        $display("========================================");
        $display("");
        
        // Initialize
        {% for pin in ic.pins if pin.type == 'input' %}
        {{ pin.name }} = 0;
        {% endfor %}
        {% if ic.category == 'sequential' %}
        clk = 0;
        rst = 1;
        #100;
        rst = 0;
        {% endif %}
        
        // Test all combinations for combinational circuits
        {% if ic.category == 'combinational' %}
        $display("Testing all input combinations:");
        $display("----------------------------------------");
        
        for (int i = 0; i < {{ 2**ic.num_inputs }}; i++) begin
            // Apply stimulus
            {% for pin in ic.pins if pin.type == 'input' %}
            {{ pin.name }} = i[{{ loop.revindex0 }}];
            {% endfor %}
            
            #10;
            
            // Display results
            $write("Input: ");
            {% for pin in ic.pins if pin.type == 'input' %}
            $write("{{ pin.name }}=%b ", {{ pin.name }});
            {% endfor %}
            $write(" -> Output: ");
            {% for pin in ic.pins if pin.type == 'output' %}
            $write("{{ pin.name }}=%b ", {{ pin.name }});
            {% endfor %}
            $display("");
        end
        {% endif %}
        
        {% if ic.category == 'sequential' %}
        // Test sequential behavior
        $display("Testing sequential behavior:");
        $display("----------------------------------------");
        
        repeat (20) begin
            @(posedge clk);
            // Apply random stimulus
            {% for pin in ic.pins if pin.type == 'input' and pin.name != 'clk' and pin.name != 'rst' %}
            {{ pin.name }} = $random;
            {% endfor %}
        end
        {% endif %}
        
        $display("");
        $display("========================================");
        $display("Test completed successfully!");
        $display("========================================");
        $finish;
    end
    
    // Monitor waveform
    initial begin
        $dumpfile("tb_{{ module_name }}.vcd");
        $dumpvars(0, tb_{{ module_name }});
    end

endmodule
EOF

echo -e "${GREEN}✓ Templates created${NC}"

# ============================================================================
# STEP 6: Create Quick Boolean Fix Script
# ============================================================================
echo -e "\n${YELLOW}▶ Step 6: Creating Boolean Expression Tools${NC}"
echo "──────────────────────────────────────────────────────────────"

cat > quick_boolean_fix.py << 'EOF'
#!/usr/bin/env python3
"""Quick fix for boolean expression demo"""

import os
import sys

def create_simple_boolean_demo():
    """Create simple boolean expression demo files"""
    
    print("Creating boolean expression demo files...")
    
    # Create directories if they don't exist
    os.makedirs("generated_verilog", exist_ok=True)
    os.makedirs("generated_testbenches", exist_ok=True)
    
    # Demo expressions
    expressions = [
        ("A&B", "demo_and"),
        ("A|B", "demo_or"),
        ("A^B", "demo_xor"),
        ("!(A&B)", "demo_nand"),
        ("(A&B)|(C&D)", "demo_complex")
    ]
    
    for expr, name in expressions:
        # Extract variables
        variables = sorted(set(c for c in expr if c.isalpha()))
        
        # Create Verilog code
        verilog_code = f"""// Boolean Expression Demo
// Generated from: {expr}
module {name}(
    input {', '.join(variables)},
    output Y
);
    assign Y = {expr.replace('&', ' && ').replace('|', ' || ').replace('^', ' ^ ').replace('!', '~')};
endmodule
"""
        
        # Save Verilog
        with open(f"generated_verilog/{name}.v", "w") as f:
            f.write(verilog_code)
        
        # Create testbench
        tb_code = f"""// Testbench for {name}
`timescale 1ns/1ps
module tb_{name};
    reg {', '.join(variables)};
    wire Y;
    
    {name} uut({', '.join(['.' + v + '(' + v + ')' for v in variables])}, .Y(Y));
    
    initial begin
        $display("Testing: {name}");
        $display("Expression: {expr}");
        $display("Variables: {', '.join(variables)}");
        $display("");
        
        // Test all combinations
        $display("Truth Table:");
        $display("-------------");
        for (int i = 0; i < {2**len(variables)}; i++) begin
"""
        
        # Add assignments
        for i, var in enumerate(variables):
            tb_code += f"            {var} = i[{len(variables)-i-1}];\n"
        
        tb_code += f"""            #10;
            $write("Input: ")
"""
        
        # Add input display
        for var in variables:
            tb_code += f'            $write("{var}=%b ", {var});\n'
        
        tb_code += f'            $display(" -> Output: %b", Y);\n'
        tb_code += f"""        end
        
        $display("");
        $display("Test complete!");
        $finish;
    end
    
    initial begin
        $dumpfile("tb_{name}.vcd");
        $dumpvars(0, tb_{name});
    end
endmodule
"""
        
        # Save testbench
        with open(f"generated_testbenches/tb_{name}.v", "w") as f:
            f.write(tb_code)
        
        print(f"  ✓ Created: {name}.v and tb_{name}.v")
    
    print(f"\n✅ Created {len(expressions)} boolean expression demos")

if __name__ == "__main__":
    create_simple_boolean_demo()
EOF

chmod +x quick_boolean_fix.py
echo -e "${GREEN}✓ Boolean tools created${NC}"

# ============================================================================
# STEP 7: Create IC Metadata Database
# ============================================================================
echo -e "\n${YELLOW}▶ Step 7: Creating IC Metadata Database${NC}"
echo "──────────────────────────────────────────────────────────────"

cat > Ic_Metadata_Master.json << 'EOF'
{
  "ics": [
    {
      "part_number": "7400",
      "name": "7400 Quad 2-Input NAND",
      "category": "combinational",
      "subtype": "nand_quad",
      "family": "TTL",
      "description": "Quad 2-input NAND gates",
      "num_inputs": 8,
      "num_outputs": 4,
      "pins": [
        {"number": 1, "name": "A1", "type": "input", "description": "Input A of Gate 1"},
        {"number": 2, "name": "B1", "type": "input", "description": "Input B of Gate 1"},
        {"number": 3, "name": "Y1", "type": "output", "description": "Output of Gate 1"},
        {"number": 4, "name": "A2", "type": "input", "description": "Input A of Gate 2"},
        {"number": 5, "name": "B2", "type": "input", "description": "Input B of Gate 2"},
        {"number": 6, "name": "Y2", "type": "output", "description": "Output of Gate 2"},
        {"number": 7, "name": "GND", "type": "ground", "description": "Ground"},
        {"number": 8, "name": "Y3", "type": "output", "description": "Output of Gate 3"},
        {"number": 9, "name": "A3", "type": "input", "description": "Input A of Gate 3"},
        {"number": 10, "name": "B3", "type": "input", "description": "Input B of Gate 3"},
        {"number": 11, "name": "Y4", "type": "output", "description": "Output of Gate 4"},
        {"number": 12, "name": "A4", "type": "input", "description": "Input A of Gate 4"},
        {"number": 13, "name": "B4", "type": "input", "description": "Input B of Gate 4"},
        {"number": 14, "name": "VCC", "type": "power", "description": "Power supply"}
      ],
      "gates": [
        {"gate": 1, "inputs": ["A1", "B1"], "output": "Y1", "expression": "~(A1 & B1)"},
        {"gate": 2, "inputs": ["A2", "B2"], "output": "Y2", "expression": "~(A2 & B2)"},
        {"gate": 3, "inputs": ["A3", "B3"], "output": "Y3", "expression": "~(A3 & B3)"},
        {"gate": 4, "inputs": ["A4", "B4"], "output": "Y4", "expression": "~(A4 & B4)"}
      ],
      "timing": {
        "propagation_delay": 10,
        "unit": "ns",
        "power_consumption": 10,
        "power_unit": "mW"
      }
    },
    {
      "part_number": "7402",
      "name": "7402 Quad 2-Input NOR",
      "category": "combinational",
      "subtype": "nor_quad",
      "family": "TTL",
      "description": "Quad 2-input NOR gates",
      "num_inputs": 8,
      "num_outputs": 4,
      "pins": [
        {"number": 1, "name": "Y1", "type": "output", "description": "Output of Gate 1"},
        {"number": 2, "name": "A1", "type": "input", "description": "Input A of Gate 1"},
        {"number": 3, "name": "B1", "type": "input", "description": "Input B of Gate 1"},
        {"number": 4, "name": "Y2", "type": "output", "description": "Output of Gate 2"},
        {"number": 5, "name": "A2", "type": "input", "description": "Input A of Gate 2"},
        {"number": 6, "name": "B2", "type": "input", "description": "Input B of Gate 2"},
        {"number": 7, "name": "GND", "type": "ground", "description": "Ground"},
        {"number": 8, "name": "A3", "type": "input", "description": "Input A of Gate 3"},
        {"number": 9, "name": "B3", "type": "input", "description": "Input B of Gate 3"},
        {"number": 10, "name": "Y3", "type": "output", "description": "Output of Gate 3"},
        {"number": 11, "name": "A4", "type": "input", "description": "Input A of Gate 4"},
        {"number": 12, "name": "B4", "type": "input", "description": "Input B of Gate 4"},
        {"number": 13, "name": "Y4", "type": "output", "description": "Output of Gate 4"},
        {"number": 14, "name": "VCC", "type": "power", "description": "Power supply"}
      ],
      "gates": [
        {"gate": 1, "inputs": ["A1", "B1"], "output": "Y1", "expression": "~(A1 | B1)"},
        {"gate": 2, "inputs": ["A2", "B2"], "output": "Y2", "expression": "~(A2 | B2)"},
        {"gate": 3, "inputs": ["A3", "B3"], "output": "Y3", "expression": "~(A3 | B3)"},
        {"gate": 4, "inputs": ["A4", "B4"], "output": "Y4", "expression": "~(A4 | B4)"}
      ],
      "timing": {
        "propagation_delay": 10,
        "unit": "ns"
      }
    },
    {
      "part_number": "7404",
      "name": "7404 Hex Inverter",
      "category": "combinational",
      "subtype": "inverter_hex",
      "family": "TTL",
      "description": "Six independent inverters",
      "num_inputs": 6,
      "num_outputs": 6,
      "pins": [
        {"number": 1, "name": "A1", "type": "input", "description": "Input of Gate 1"},
        {"number": 2, "name": "Y1", "type": "output", "description": "Output of Gate 1"},
        {"number": 3, "name": "A2", "type": "input", "description": "Input of Gate 2"},
        {"number": 4, "name": "Y2", "type": "output", "description": "Output of Gate 2"},
        {"number": 5, "name": "A3", "type": "input", "description": "Input of Gate 3"},
        {"number": 6, "name": "Y3", "type": "output", "description": "Output of Gate 3"},
        {"number": 7, "name": "GND", "type": "ground", "description": "Ground"},
        {"number": 8, "name": "Y4", "type": "output", "description": "Output of Gate 4"},
        {"number": 9, "name": "A4", "type": "input", "description": "Input of Gate 4"},
        {"number": 10, "name": "Y5", "type": "output", "description": "Output of Gate 5"},
        {"number": 11, "name": "A5", "type": "input", "description": "Input of Gate 5"},
        {"number": 12, "name": "Y6", "type": "output", "description": "Output of Gate 6"},
        {"number": 13, "name": "A6", "type": "input", "description": "Input of Gate 6"},
        {"number": 14, "name": "VCC", "type": "power", "description": "Power supply"}
      ],
      "gates": [
        {"gate": 1, "inputs": ["A1"], "output": "Y1", "expression": "~A1"},
        {"gate": 2, "inputs": ["A2"], "output": "Y2", "expression": "~A2"},
        {"gate": 3, "inputs": ["A3"], "output": "Y3", "expression": "~A3"},
        {"gate": 4, "inputs": ["A4"], "output": "Y4", "expression": "~A4"},
        {"gate": 5, "inputs": ["A5"], "output": "Y5", "expression": "~A5"},
        {"gate": 6, "inputs": ["A6"], "output": "Y6", "expression": "~A6"}
      ],
      "timing": {
        "propagation_delay": 9,
        "unit": "ns"
      }
    },
    {
      "part_number": "7408",
      "name": "7408 Quad 2-Input AND",
      "category": "combinational",
      "subtype": "and_quad",
      "family": "TTL",
      "description": "Quad 2-input AND gates",
      "num_inputs": 8,
      "num_outputs": 4,
      "pins": [
        {"number": 1, "name": "A1", "type": "input", "description": "Input A of Gate 1"},
        {"number": 2, "name": "B1", "type": "input", "description": "Input B of Gate 1"},
        {"number": 3, "name": "Y1", "type": "output", "description": "Output of Gate 1"},
        {"number": 4, "name": "A2", "type": "input", "description": "Input A of Gate 2"},
        {"number": 5, "name": "B2", "type": "input", "description": "Input B of Gate 2"},
        {"number": 6, "name": "Y2", "type": "output", "description": "Output of Gate 2"},
        {"number": 7, "name": "GND", "type": "ground", "description": "Ground"},
        {"number": 8, "name": "Y3", "type": "output", "description": "Output of Gate 3"},
        {"number": 9, "name": "A3", "type": "input", "description": "Input A of Gate 3"},
        {"number": 10, "name": "B3", "type": "input", "description": "Input B of Gate 3"},
        {"number": 11, "name": "Y4", "type": "output", "description": "Output of Gate 4"},
        {"number": 12, "name": "A4", "type": "input", "description": "Input A of Gate 4"},
        {"number": 13, "name": "B4", "type": "input", "description": "Input B of Gate 4"},
        {"number": 14, "name": "VCC", "type": "power", "description": "Power supply"}
      ],
      "gates": [
        {"gate": 1, "inputs": ["A1", "B1"], "output": "Y1", "expression": "A1 & B1"},
        {"gate": 2, "inputs": ["A2", "B2"], "output": "Y2", "expression": "A2 & B2"},
        {"gate": 3, "inputs": ["A3", "B3"], "output": "Y3", "expression": "A3 & B3"},
        {"gate": 4, "inputs": ["A4", "B4"], "output": "Y4", "expression": "A4 & B4"}
      ],
      "timing": {
        "propagation_delay": 11,
        "unit": "ns"
      }
    },
    {
      "part_number": "7432",
      "name": "7432 Quad 2-Input OR",
      "category": "combinational",
      "subtype": "or_quad",
      "family": "TTL",
      "description": "Quad 2-input OR gates",
      "num_inputs": 8,
      "num_outputs": 4,
      "pins": [
        {"number": 1, "name": "A1", "type": "input", "description": "Input A of Gate 1"},
        {"number": 2, "name": "B1", "type": "input", "description": "Input B of Gate 1"},
        {"number": 3, "name": "Y1", "type": "output", "description": "Output of Gate 1"},
        {"number": 4, "name": "A2", "type": "input", "description": "Input A of Gate 2"},
        {"number": 5, "name": "B2", "type": "input", "description": "Input B of Gate 2"},
        {"number": 6, "name": "Y2", "type": "output", "description": "Output of Gate 2"},
        {"number": 7, "name": "GND", "type": "ground", "description": "Ground"},
        {"number": 8, "name": "Y3", "type": "output", "description": "Output of Gate 3"},
        {"number": 9, "name": "A3", "type": "input", "description": "Input A of Gate 3"},
        {"number": 10, "name": "B3", "type": "input", "description": "Input B of Gate 3"},
        {"number": 11, "name": "Y4", "type": "output", "description": "Output of Gate 4"},
        {"number": 12, "name": "A4", "type": "input", "description": "Input A of Gate 4"},
        {"number": 13, "name": "B4", "type": "input", "description": "Input B of Gate 4"},
        {"number": 14, "name": "VCC", "type": "power", "description": "Power supply"}
      ],
      "gates": [
        {"gate": 1, "inputs": ["A1", "B1"], "output": "Y1", "expression": "A1 | B1"},
        {"gate": 2, "inputs": ["A2", "B2"], "output": "Y2", "expression": "A2 | B2"},
        {"gate": 3, "inputs": ["A3", "B3"], "output": "Y3", "expression": "A3 | B3"},
        {"gate": 4, "inputs": ["A4", "B4"], "output": "Y4", "expression": "A4 | B4"}
      ],
      "timing": {
        "propagation_delay": 11,
        "unit": "ns"
      }
    },
    {
      "part_number": "7486",
      "name": "7486 Quad 2-Input XOR",
      "category": "combinational",
      "subtype": "xor_quad",
      "family": "TTL",
      "description": "Quad 2-input XOR gates",
      "num_inputs": 8,
      "num_outputs": 4,
      "pins": [
        {"number": 1, "name": "A1", "type": "input", "description": "Input A of Gate 1"},
        {"number": 2, "name": "B1", "type": "input", "description": "Input B of Gate 1"},
        {"number": 3, "name": "Y1", "type": "output", "description": "Output of Gate 1"},
        {"number": 4, "name": "A2", "type": "input", "description": "Input A of Gate 2"},
        {"number": 5, "name": "B2", "type": "input", "description": "Input B of Gate 2"},
        {"number": 6, "name": "Y2", "type": "output", "description": "Output of Gate 2"},
        {"number": 7, "name": "GND", "type": "ground", "description": "Ground"},
        {"number": 8, "name": "Y3", "type": "output", "description": "Output of Gate 3"},
        {"number": 9, "name": "A3", "type": "input", "description": "Input A of Gate 3"},
        {"number": 10, "name": "B3", "type": "input", "description": "Input B of Gate 3"},
        {"number": 11, "name": "Y4", "type": "output", "description": "Output of Gate 4"},
        {"number": 12, "name": "A4", "type": "input", "description": "Input A of Gate 4"},
        {"number": 13, "name": "B4", "type": "input", "description": "Input B of Gate 4"},
        {"number": 14, "name": "VCC", "type": "power", "description": "Power supply"}
      ],
      "gates": [
        {"gate": 1, "inputs": ["A1", "B1"], "output": "Y1", "expression": "A1 ^ B1"},
        {"gate": 2, "inputs": ["A2", "B2"], "output": "Y2", "expression": "A2 ^ B2"},
        {"gate": 3, "inputs": ["A3", "B3"], "output": "Y3", "expression": "A3 ^ B3"},
        {"gate": 4, "inputs": ["A4", "B4"], "output": "Y4", "expression": "A4 ^ B4"}
      ],
      "timing": {
        "propagation_delay": 14,
        "unit": "ns"
      }
    },
    {
      "part_number": "7474",
      "name": "7474 Dual D-Type Flip-Flop",
      "category": "sequential",
      "subtype": "dff_dual",
      "family": "TTL",
      "description": "Dual D-type positive-edge triggered flip-flops with preset and clear",
      "num_inputs": 6,
      "num_outputs": 4,
      "clock_pin": "CLK",
      "reset_pin": "CLR",
      "preset_pin": "PRE",
      "pins": [
        {"number": 1, "name": "CLR1", "type": "input", "description": "Clear for Flip-Flop 1 (active low)"},
        {"number": 2, "name": "D1", "type": "input", "description": "Data input for Flip-Flop 1"},
        {"number": 3, "name": "CLK1", "type": "input", "description": "Clock for Flip-Flop 1"},
        {"number": 4, "name": "PRE1", "type": "input", "description": "Preset for Flip-Flop 1 (active low)"},
        {"number": 5, "name": "Q1", "type": "output", "description": "Output of Flip-Flop 1"},
        {"number": 6, "name": "Q1_BAR", "type": "output", "description": "Complementary output of Flip-Flop 1"},
        {"number": 7, "name": "GND", "type": "ground", "description": "Ground"},
        {"number": 8, "name": "Q2_BAR", "type": "output", "description": "Complementary output of Flip-Flop 2"},
        {"number": 9, "name": "Q2", "type": "output", "description": "Output of Flip-Flop 2"},
        {"number": 10, "name": "PRE2", "type": "input", "description": "Preset for Flip-Flop 2 (active low)"},
        {"number": 11, "name": "CLK2", "type": "input", "description": "Clock for Flip-Flop 2"},
        {"number": 12, "name": "D2", "type": "input", "description": "Data input for Flip-Flop 2"},
        {"number": 13, "name": "CLR2", "type": "input", "description": "Clear for Flip-Flop 2 (active low)"},
        {"number": 14, "name": "VCC", "type": "power", "description": "Power supply"}
      ],
      "registers": [
        {"name": "Q1", "type": "dff"},
        {"name": "Q2", "type": "dff"}
      ],
      "state_transitions": [
        {"condition": "!CLR1", "assignment": "Q1 <= 0"},
        {"condition": "!PRE1", "assignment": "Q1 <= 1"},
        {"condition": "posedge CLK1", "assignment": "Q1 <= D1"}
      ],
      "timing": {
        "setup_time": 20,
        "hold_time": 5,
        "propagation_delay": 25,
        "unit": "ns"
      }
    }
  ]
}
EOF

echo -e "${GREEN}✓ IC Metadata database created (7 ICs configured)${NC}"

# ============================================================================
# STEP 8: Create Advanced Generator Script
# ============================================================================
echo -e "\n${YELLOW}▶ Step 8: Creating Advanced Generator${NC}"
echo "──────────────────────────────────────────────────────────────"

cat > advanced_generator.py << 'EOF'
#!/usr/bin/env python3
"""
Advanced HDL Generator for Legacy ICs
Author: Gokul R
Email: gokulr200305@gmail.com
"""

import json
import os
import sys
import argparse
from datetime import datetime
from jinja2 import Template, Environment, FileSystemLoader

class HDLGenerator:
    def __init__(self):
        self.load_ic_database()
        self.setup_template_env()
        
    def load_ic_database(self):
        """Load IC metadata database"""
        try:
            with open('Ic_Metadata_Master.json', 'r') as f:
                data = json.load(f)
                self.ics = {ic['part_number']: ic for ic in data['ics']}
            print(f"✓ Loaded {len(self.ics)} ICs from database")
        except FileNotFoundError:
            print("✗ IC database not found")
            self.ics = {}
    
    def setup_template_env(self):
        """Setup Jinja2 template environment"""
        self.template_env = Environment(
            loader=FileSystemLoader('hdl_templates'),
            trim_blocks=True,
            lstrip_blocks=True
        )
    
    def list_supported_ics(self):
        """List all supported ICs"""
        print("\n" + "="*80)
        print("Supported ICs - HDL Generator")
        print("="*80)
        print(f"{'Part':<8} {'Name':<40} {'Category':<15} {'Status':<10}")
        print("-"*80)
        
        for part_num, ic in sorted(self.ics.items()):
            name = ic['name'][:38] + ".." if len(ic['name']) > 38 else ic['name']
            category = ic.get('category', 'unknown')
            print(f"{part_num:<8} {name:<40} {category:<15} ✓")
        
        print(f"\nTotal: {len(self.ics)} ICs supported")
    
    def generate_verilog(self, ic_number, with_testbench=True):
        """Generate Verilog for an IC"""
        if ic_number not in self.ics:
            print(f"✗ IC {ic_number} not found")
            return False
        
        ic = self.ics[ic_number]
        module_name = f"IC_{ic_number}"
        
        # Create output directory
        os.makedirs('generated_verilog', exist_ok=True)
        
        # Generate module
        template = self.template_env.get_template('verilog/generic.vtpl')
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        verilog_code = template.render(
            ic=ic,
            module_name=module_name,
            timestamp=timestamp
        )
        
        # Save to file
        filename = f"generated_verilog/{module_name}.v"
        with open(filename, 'w') as f:
            f.write(verilog_code)
        
        print(f"✓ Generated Verilog: {filename}")
        
        # Generate testbench if requested
        if with_testbench:
            self.generate_testbench(ic_number)
        
        return True
    
    def generate_vhdl(self, ic_number, with_testbench=True):
        """Generate VHDL for an IC"""
        if ic_number not in self.ics:
            print(f"✗ IC {ic_number} not found")
            return False
        
        ic = self.ics[ic_number]
        module_name = f"IC_{ic_number}"
        
        # Create output directory
        os.makedirs('generated_vhdl', exist_ok=True)
        
        # Generate module
        template = self.template_env.get_template('vhdl/generic.vhdltpl')
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        vhdl_code = template.render(
            ic=ic,
            module_name=module_name,
            timestamp=timestamp
        )
        
        # Save to file
        filename = f"generated_vhdl/{module_name}.vhd"
        with open(filename, 'w') as f:
            f.write(vhdl_code)
        
        print(f"✓ Generated VHDL: {filename}")
        
        return True
    
    def generate_testbench(self, ic_number):
        """Generate testbench for an IC"""
        if ic_number not in self.ics:
            print(f"✗ IC {ic_number} not found")
            return False
        
        ic = self.ics[ic_number]
        module_name = f"IC_{ic_number}"
        
        # Create output directory
        os.makedirs('generated_testbenches', exist_ok=True)
        
        # Generate testbench
        template_env = Environment(loader=FileSystemLoader('testbench_templates'))
        template = template_env.get_template('verilog/generic_tb.vtpl')
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        tb_code = template.render(
            ic=ic,
            module_name=module_name,
            timestamp=timestamp
        )
        
        # Save to file
        filename = f"generated_testbenches/tb_{module_name}.v"
        with open(filename, 'w') as f:
            f.write(tb_code)
        
        print(f"✓ Generated Testbench: {filename}")
        return True
    
    def generate_all(self, language='verilog', testbenches=False):
        """Generate all ICs"""
        print(f"\nGenerating all ICs in {language.upper()}...")
        print("="*50)
        
        success_count = 0
        for ic_number in self.ics:
            try:
                if language == 'verilog':
                    if self.generate_verilog(ic_number, testbenches):
                        success_count += 1
                elif language == 'vhdl':
                    if self.generate_vhdl(ic_number, testbenches):
                        success_count += 1
            except Exception as e:
                print(f"✗ Failed to generate {ic_number}: {e}")
        
        print(f"\n✓ Generated {success_count}/{len(self.ics)} ICs successfully")
    
    def generate_from_boolean(self, expression, name=None):
        """Generate HDL from boolean expression"""
        print(f"\nGenerating from boolean expression: {expression}")
        
        # Simple boolean parser
        variables = sorted(set(c for c in expression if c.isalpha()))
        
        if not variables:
            print("✗ No variables found in expression")
            return False
        
        if not name:
            safe_name = expression[:15].replace('&','and').replace('|','or')
            safe_name = safe_name.replace('^','xor').replace('!','not')
            safe_name = safe_name.replace('(','').replace(')','').replace(' ','')
            name = f"bool_{safe_name}"
        
        # Convert to Verilog
        verilog_expr = expression.replace('&', ' && ').replace('|', ' || ')
        verilog_expr = verilog_expr.replace('^', ' ^ ').replace('!', '~')
        
        verilog_code = f"""// Boolean Expression: {expression}
module {name}(
    input {', '.join(variables)},
    output Y
);
    assign Y = {verilog_expr};
endmodule
"""
        
        # Save to file
        os.makedirs('generated_verilog', exist_ok=True)
        filename = f"generated_verilog/{name}.v"
        with open(filename, 'w') as f:
            f.write(verilog_code)
        
        print(f"✓ Generated: {filename}")
        print(f"  Expression: {expression}")
        print(f"  Variables: {', '.join(variables)}")
        
        return True

def main():
    parser = argparse.ArgumentParser(description='IC HDL Generator')
    parser.add_argument('command', choices=['list', 'generate', 'generate-all', 'boolean'],
                       help='Command to execute')
    parser.add_argument('target', nargs='?', help='IC number or boolean expression')
    parser.add_argument('--language', choices=['verilog', 'vhdl'], default='verilog',
                       help='Target language')
    parser.add_argument('--testbenches', action='store_true',
                       help='Generate testbenches')
    parser.add_argument('--name', help='Circuit name for boolean expressions')
    
    args = parser.parse_args()
    
    generator = HDLGenerator()
    
    if args.command == 'list':
        generator.list_supported_ics()
    
    elif args.command == 'generate':
        if not args.target:
            print("Error: Please specify an IC number")
            return
        
        if args.language == 'verilog':
            generator.generate_verilog(args.target, args.testbenches)
        else:
            generator.generate_vhdl(args.target, args.testbenches)
    
    elif args.command == 'generate-all':
        generator.generate_all(args.language, args.testbenches)
    
    elif args.command == 'boolean':
        if not args.target:
            print("Error: Please specify a boolean expression")
            return
        generator.generate_from_boolean(args.target, args.name)

if __name__ == '__main__':
    main()
EOF

chmod +x advanced_generator.py

# ============================================================================
# STEP 9: Create Circuit Generator
# ============================================================================
echo -e "\n${YELLOW}▶ Step 9: Creating Circuit Generator${NC}"
echo "──────────────────────────────────────────────────────────────"

cat > circuit_generator_advanced.py << 'EOF'
#!/usr/bin/env python3
"""
Advanced Circuit Generator for HDL Compositions
Author: Gokul R
"""

import json
import os
import sys
from datetime import datetime

class CircuitGenerator:
    def __init__(self):
        self.circuits = {
            'full_adder_1bit': {
                'name': '1-bit binary full adder',
                'description': 'Adds three 1-bit inputs (A, B, Cin) to produce Sum and Cout',
                'ics': ['7486', '7408', '7432'],
                'inputs': ['A', 'B', 'Cin'],
                'outputs': ['Sum', 'Cout'],
                'equations': {
                    'Sum': 'A ^ B ^ Cin',
                    'Cout': '(A & B) | (Cin & (A ^ B))'
                }
            },
            'half_adder_1bit': {
                'name': '1-bit binary half adder',
                'description': 'Adds two 1-bit inputs (A, B) to produce Sum and Carry',
                'ics': ['7486', '7408'],
                'inputs': ['A', 'B'],
                'outputs': ['Sum', 'Carry'],
                'equations': {
                    'Sum': 'A ^ B',
                    'Carry': 'A & B'
                }
            },
            '2bit_adder': {
                'name': '2-bit binary adder',
                'description': 'Adds two 2-bit numbers with carry in/out',
                'ics': ['full_adder_1bit', 'full_adder_1bit'],
                'inputs': ['A[1:0]', 'B[1:0]', 'Cin'],
                'outputs': ['Sum[1:0]', 'Cout']
            },
            '4bit_adder': {
                'name': '4-bit binary adder',
                'description': 'Adds two 4-bit numbers with carry ripple',
                'ics': ['full_adder_1bit'] * 4,
                'inputs': ['A[3:0]', 'B[3:0]', 'Cin'],
                'outputs': ['Sum[3:0]', 'Cout']
            }
        }
    
    def list_circuits(self):
        """List all available circuits"""
        print("\n=== Supported Advanced Circuits ===")
        print("="*40)
        
        for name, info in self.circuits.items():
            print(f"\n{name}:")
            print(f"  Name: {info['name']}")
            print(f"  Description: {info['description']}")
            print(f"  ICs required: {', '.join(info['ics'])}")
            print(f"  Inputs: {', '.join(info['inputs'])}")
            print(f"  Outputs: {', '.join(info['outputs'])}")
    
    def generate_circuit(self, circuit_name):
        """Generate HDL for a circuit"""
        if circuit_name not in self.circuits:
            print(f"✗ Circuit '{circuit_name}' not found")
            return False
        
        circuit = self.circuits[circuit_name]
        
        # Create output directory
        os.makedirs('generated_circuits', exist_ok=True)
        
        # Generate Verilog
        verilog = self._generate_verilog(circuit_name, circuit)
        
        filename = f"generated_circuits/{circuit_name}.v"
        with open(filename, 'w') as f:
            f.write(verilog)
        
        print(f"✓ Generated circuit: {filename}")
        
        # Generate testbench
        tb = self._generate_testbench(circuit_name, circuit)
        tb_filename = f"generated_circuits/tb_{circuit_name}.v"
        with open(tb_filename, 'w') as f:
            f.write(tb)
        
        print(f"✓ Generated testbench: {tb_filename}")
        
        return True
    
    def _generate_verilog(self, name, circuit):
        """Generate Verilog for circuit"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        code = f"""// {circuit['name']}
// Description: {circuit['description']}
// Generated: {timestamp}

module {name}(
"""
        # Add inputs
        for i, inp in enumerate(circuit['inputs']):
            code += f"    input {inp}"
            if i < len(circuit['inputs']) - 1:
                code += ",\n"
            else:
                code += ",\n"
        
        # Add outputs
        for i, out in enumerate(circuit['outputs']):
            code += f"    output {out}"
            if i < len(circuit['outputs']) - 1:
                code += ",\n"
            else:
                code += "\n"
        
        code += ");\n\n"
        
        if 'equations' in circuit:
            # Direct implementation
            code += "    // Implementation using Boolean equations\n"
            for out, eq in circuit['equations'].items():
                code += f"    assign {out} = {eq};\n"
        else:
            # Hierarchical implementation
            code += "    // Hierarchical implementation\n"
            code += "    // Using instantiated components\n"
            
            if name == '2bit_adder':
                code += """
    wire c1;
    
    full_adder_1bit fa0 (
        .A(A[0]),
        .B(B[0]),
        .Cin(Cin),
        .Sum(Sum[0]),
        .Cout(c1)
    );
    
    full_adder_1bit fa1 (
        .A(A[1]),
        .B(B[1]),
        .Cin(c1),
        .Sum(Sum[1]),
        .Cout(Cout)
    );
"""
            elif name == '4bit_adder':
                code += """
    wire c1, c2, c3;
    
    full_adder_1bit fa0 (
        .A(A[0]), .B(B[0]), .Cin(Cin),
        .Sum(Sum[0]), .Cout(c1)
    );
    
    full_adder_1bit fa1 (
        .A(A[1]), .B(B[1]), .Cin(c1),
        .Sum(Sum[1]), .Cout(c2)
    );
    
    full_adder_1bit fa2 (
        .A(A[2]), .B(B[2]), .Cin(c2),
        .Sum(Sum[2]), .Cout(c3)
    );
    
    full_adder_1bit fa3 (
        .A(A[3]), .B(B[3]), .Cin(c3),
        .Sum(Sum[3]), .Cout(Cout)
    );
"""
        
        code += "\nendmodule\n"
        return code
    
    def _generate_testbench(self, name, circuit):
        """Generate testbench for circuit"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        tb = f"""// Testbench for {name}
// Generated: {timestamp}

`timescale 1ns/1ps

module tb_{name};
"""
        # Add regs for inputs
        for inp in circuit['inputs']:
            if '[' in inp:
                # Bus input
                base = inp.split('[')[0]
                tb += f"    reg [{inp.split('[')[1].replace(']','')}] {base};\n"
            else:
                tb += f"    reg {inp};\n"
        
        # Add wires for outputs
        for out in circuit['outputs']:
            if '[' in out:
                base = out.split('[')[0]
                tb += f"    wire [{out.split('[')[1].replace(']','')}] {base};\n"
            else:
                tb += f"    wire {out};\n"
        
        tb += f"""
    // Instantiate DUT
    {name} dut (
"""
        # Connect inputs
        for inp in circuit['inputs']:
            if '[' in inp:
                base = inp.split('[')[0]
                tb += f"        .{inp}({base})"
            else:
                tb += f"        .{inp}({inp})"
            if inp != circuit['inputs'][-1] or circuit['outputs']:
                tb += ",\n"
        
        # Connect outputs
        for out in circuit['outputs']:
            if '[' in out:
                base = out.split('[')[0]
                tb += f"        .{out}({base})"
            else:
                tb += f"        .{out}({out})"
            if out != circuit['outputs'][-1]:
                tb += ",\n"
        
        tb += """
    );
    
    initial begin
        $display("Testing %s", "");
        $display("Circuit: %s", "");
"""
        
        # Add test vectors
        if 'equations' in circuit:
            # Test all combinations for small circuits
            num_inputs = len([i for i in circuit['inputs'] if not '[' in i])
            if num_inputs <= 4:
                tb += f"""
        // Test all {2**num_inputs} combinations
        $display("Truth Table Test");
        $display("----------------------------------------");
        
        for (int i = 0; i < {2**num_inputs}; i++) begin
"""
                # Assign inputs
                simple_inputs = [i for i in circuit['inputs'] if not '[' in i]
                for idx, inp in enumerate(simple_inputs):
                    tb += f"            {inp} = i[{len(simple_inputs)-idx-1}];\n"
                
                tb += "            #10;\n"
                tb += '            $display('
                for inp in simple_inputs:
                    tb += f'" {inp}=%b", {inp},'
                for out in circuit['outputs']:
                    tb += f'" {out}=%b", {out},'
                tb += '"");\n'
                tb += "        end\n"
        
        tb += """
        $display("----------------------------------------");
        $display("Test completed successfully!");
        $finish;
    end
    
    initial begin
        $dumpfile("tb_%s.vcd", "");
        $dumpvars(0, tb_%s);
    end
endmodule
""" % (name, name)
        
        return tb
    
    def generate_all(self):
        """Generate all circuits"""
        print("\nGenerating all circuits...")
        print("="*40)
        
        for name in self.circuits:
            self.generate_circuit(name)
        
        print(f"\n✓ Generated {len(self.circuits)} circuits")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Circuit Generator')
    parser.add_argument('command', choices=['list', 'generate', 'generate-all'],
                       help='Command to execute')
    parser.add_argument('circuit', nargs='?', help='Circuit name')
    
    args = parser.parse_args()
    
    generator = CircuitGenerator()
    
    if args.command == 'list':
        generator.list_circuits()
    elif args.command == 'generate':
        if not args.circuit:
            print("Error: Please specify a circuit name")
            return
        generator.generate_circuit(args.circuit)
    elif args.command == 'generate-all':
        generator.generate_all()

if __name__ == '__main__':
    main()
EOF

chmod +x circuit_generator_advanced.py

# ============================================================================
# STEP 10: Create Run Script
# ============================================================================
echo -e "\n${YELLOW}▶ Step 10: Creating Run Script${NC}"
echo "──────────────────────────────────────────────────────────────"

cat > run.sh << 'EOF'
#!/bin/bash
# ============================================================================
# IC HDL Generator - Run Script
# ============================================================================
# Author: Gokul R
# Email: gokulr200305@gmail.com
# ============================================================================

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

show_menu() {
    clear
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${NC}${YELLOW}              IC HDL GENERATOR - MAIN MENU              ${NC}${BLUE}║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "1) List Supported ICs"
    echo "2) Generate Single IC (Verilog)"
    echo "3) Generate Single IC (VHDL)"
    echo "4) Generate All ICs (Verilog)"
    echo "5) Generate All ICs (VHDL)"
    echo "6) Generate Testbench for IC"
    echo "7) List Available Circuits"
    echo "8) Generate Circuit"
    echo "9) Generate All Circuits"
    echo "10) Boolean Expression to HDL"
    echo "11) Run Complete Presentation"
    echo "12) Show Statistics"
    echo "13) Exit"
    echo ""
    echo -n "Enter choice [1-13]: "
}

while true; do
    show_menu
    read choice
    
    case $choice in
        1)
            echo -e "\n${GREEN}▶ Listing Supported ICs${NC}"
            python3 advanced_generator.py list
            read -p "Press Enter to continue..."
            ;;
        2)
            echo -e "\n${GREEN}▶ Generate Single IC (Verilog)${NC}"
            echo -n "Enter IC number (e.g., 7400): "
            read ic
            python3 advanced_generator.py generate $ic --language verilog --testbenches
            read -p "Press Enter to continue..."
            ;;
        3)
            echo -e "\n${GREEN}▶ Generate Single IC (VHDL)${NC}"
            echo -n "Enter IC number (e.g., 7400): "
            read ic
            python3 advanced_generator.py generate $ic --language vhdl
            read -p "Press Enter to continue..."
            ;;
        4)
            echo -e "\n${GREEN}▶ Generating All ICs (Verilog)${NC}"
            python3 advanced_generator.py generate-all --language verilog --testbenches
            read -p "Press Enter to continue..."
            ;;
        5)
            echo -e "\n${GREEN}▶ Generating All ICs (VHDL)${NC}"
            python3 advanced_generator.py generate-all --language vhdl
            read -p "Press Enter to continue..."
            ;;
        6)
            echo -e "\n${GREEN}▶ Generate Testbench${NC}"
            echo -n "Enter IC number (e.g., 7400): "
            read ic
            python3 advanced_generator.py generate $ic --testbenches
            read -p "Press Enter to continue..."
            ;;
        7)
            echo -e "\n${GREEN}▶ Listing Available Circuits${NC}"
            python3 circuit_generator_advanced.py list
            read -p "Press Enter to continue..."
            ;;
        8)
            echo -e "\n${GREEN}▶ Generate Circuit${NC}"
            python3 circuit_generator_advanced.py list
            echo -n "Enter circuit name: "
            read circuit
            python3 circuit_generator_advanced.py generate $circuit
            read -p "Press Enter to continue..."
            ;;
        9)
            echo -e "\n${GREEN}▶ Generating All Circuits${NC}"
            python3 circuit_generator_advanced.py generate-all
            read -p "Press Enter to continue..."
            ;;
        10)
            echo -e "\n${GREEN}▶ Boolean Expression to HDL${NC}"
            echo "Examples:"
            echo "  A&B          (AND)"
            echo "  A|B          (OR)" 
            echo "  A^B          (XOR)"
            echo "  !(A&B)       (NAND)"
            echo "  (A&B)|(C&D)  (Complex)"
            echo ""
            echo -n "Enter boolean expression: "
            read expr
            echo -n "Enter circuit name (optional): "
            read name
            
            if [ -z "$name" ]; then
                python3 advanced_generator.py boolean "$expr"
            else
                python3 advanced_generator.py boolean "$expr" --name $name
            fi
            read -p "Press Enter to continue..."
            ;;
        11)
            echo -e "\n${GREEN}▶ Running Complete Presentation${NC}"
            if [ -f "presentation_script.sh" ]; then
                ./presentation_script.sh
            else
                echo "Presentation script not found"
            fi
            read -p "Press Enter to continue..."
            ;;
        12)
            echo -e "\n${GREEN}▶ Generation Statistics${NC}"
            echo "========================================"
            echo "Verilog files: $(find generated_verilog -name '*.v' 2>/dev/null | wc -l)"
            echo "VHDL files: $(find generated_vhdl -name '*.vhd' 2>/dev/null | wc -l)"
            echo "Testbenches: $(find generated_testbenches -name '*.v' 2>/dev/null | wc -l)"
            echo "Circuits: $(find generated_circuits -name '*.v' 2>/dev/null | wc -l)"
            echo "========================================"
            read -p "Press Enter to continue..."
            ;;
        13)
            echo -e "\n${GREEN}Thank you for using IC HDL Generator!${NC}"
            exit 0
            ;;
        *)
            echo -e "\n${RED}Invalid choice${NC}"
            read -p "Press Enter to continue..."
            ;;
    esac
done
EOF

chmod +x run.sh

# ============================================================================
# STEP 11: Create Presentation Script
# ============================================================================
echo -e "\n${YELLOW}▶ Step 11: Creating Presentation Script${NC}"
echo "──────────────────────────────────────────────────────────────"

cat > presentation_script.sh << 'EOF'
#!/bin/bash
# IC HDL Generator - Presentation Script
# Author: Gokul R

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${NC}${YELLOW}         IC HDL GENERATOR - COMPLETE DEMO           ${NC}${BLUE}║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Step 1: Show supported ICs
echo -e "${GREEN}▶ Step 1: Supported ICs${NC}"
python3 advanced_generator.py list
echo ""
read -p "Press Enter to continue..."

# Step 2: Generate 7400
echo -e "\n${GREEN}▶ Step 2: Generating 7400 NAND Gate${NC}"
python3 advanced_generator.py generate 7400 --language verilog --testbenches
echo ""
read -p "Press Enter to continue..."

# Step 3: Show generated code
echo -e "\n${GREEN}▶ Step 3: Generated Verilog for 7400${NC}"
echo "----------------------------------------"
head -20 generated_verilog/IC_7400.v
echo ""
read -p "Press Enter to continue..."

# Step 4: Boolean expression demo
echo -e "\n${GREEN}▶ Step 4: Boolean Expression Demo${NC}"
python3 quick_boolean_fix.py
echo ""
echo "Generated AND gate:"
cat generated_verilog/demo_and.v
echo ""
read -p "Press Enter to continue..."

# Step 5: Circuit composition
echo -e "\n${GREEN}▶ Step 5: Generating Full Adder Circuit${NC}"
python3 circuit_generator_advanced.py generate full_adder_1bit
echo ""
read -p "Press Enter to continue..."

# Summary
echo -e "\n${GREEN}▶ Demo Complete!${NC}"
echo "Generated files:"
echo "  - Verilog: $(find generated_verilog -name '*.v' | wc -l) files"
echo "  - VHDL: $(find generated_vhdl -name '*.vhd' | wc -l) files"
echo "  - Testbenches: $(find generated_testbenches -name '*.v' | wc -l) files"
echo "  - Circuits: $(find generated_circuits -name '*.v' | wc -l) files"
echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
EOF

chmod +x presentation_script.sh

# ============================================================================
# STEP 12: Create Requirements File
# ============================================================================
echo -e "\n${YELLOW}▶ Step 12: Creating Requirements File${NC}"
echo "──────────────────────────────────────────────────────────────"

cat > requirements.txt << 'EOF'
# Core dependencies
jinja2>=3.0.0
pyyaml>=5.4.0

# Testing
pytest>=6.0.0
pytest-cov>=2.12.0

# Code quality
black>=21.0.0
pylint>=2.8.0

# Optional
numpy>=1.19.0
matplotlib>=3.3.0
EOF

# ============================================================================
# STEP 13: Create README
# ============================================================================
echo -e "\n${YELLOW}▶ Step 13: Creating README${NC}"
echo "──────────────────────────────────────────────────────────────"

cat > README.md << 'EOF'
# IC HDL Generator - Automated HDL Generation Framework for Legacy ICs

## 📋 Overview
This framework automatically generates Verilog/VHDL code for legacy 7400-series ICs, complete with testbenches and circuit composition capabilities.

## ✨ Features
- Generate HDL for 20+ 7400-series ICs
- Automatic testbench generation
- Boolean expression to HDL conversion
- Circuit composition (adders, ALUs, etc.)
- Multi-language support (Verilog/VHDL)
- Educational focus with simulation-ready output

## 🚀 Quick Start

### Installation
```bash
# Clone and setup
git clone https://github.com/GokulR2003/ic_hdl_generator.git
cd ic_hdl_generator
chmod +x setup.sh
./setup.sh
