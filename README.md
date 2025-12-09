# IC HDL Generator

A tool to automatically generate Verilog/VHDL code from IC metadata using Jinja2 templates.

## Features

- Generate HDL code for 75+ classic ICs (7400 series, 4000 series, etc.)
- Support for both Verilog and VHDL
- Auto-generated testbenches with coverage tracking
- Template-based system for easy extension
- Command-line interface and Python API
- Metadata-driven design (JSON format)

## Quick Start

### Installation

```
# Clone the repository
git clone https://github.com/GokulR2003/ic_hdl_generator.git
cd ic_hdl_generator

# Install dependencies
pip install -r requirements.txt
```
# List all available ICs
ic-hdl-gen list

# Generate Verilog for 7400
ic-hdl-gen generate 7400

# Generate VHDL for 7400
ic-hdl-gen generate 7400 --language vhdl

# Generate all ICs
ic-hdl-gen generate-all

# Generate testbench
ic-hdl-gen testbench 7400

## Python API
from src.hdl_generator import HDLGenerator

# Create generator
gen = HDLGenerator('Ic_Metadata_Master.json', 'hdl_templates/')

# Generate HDL
verilog = gen.generate_hdl('7400', 'verilog')

# Generate all
gen.generate_all('verilog', 'output/')

## Supported ICs
# Combinational Logic
7400 - Quad 2-input NAND

7402 - Quad 2-input NOR

7404 - Hex Inverter

7408 - Quad 2-input AND

7432 - Quad 2-input OR

7486 - Quad 2-input XOR

74138 - 3-to-8 Decoder

74139 - Dual 2-to-4 Decoder

74147 - Priority Encoder

74153 - Dual 4:1 MUX

7447 - BCD to 7-Segment

7485 - 4-bit Comparator

# Sequential Logic
7474 - Dual D Flip-Flop

7476 - Dual JK Flip-Flop

7490 - Decade Counter

7493 - Binary Counter

4017 - Johnson Counter

# Special Functions
74245 - Octal Bus Transceiver

74121 - Monostable Multivibrator

555 - Timer IC

## Adding New ICs
Add IC metadata to Ic_Metadata_Master.json

Create template in hdl_templates/

Test generation: ic-hdl-gen generate <part_number>

Example template (hdl_templates/verilog/combinational/basic_gates/nand_quad.vtpl):[jinja.txt](https://github.com/user-attachments/files/24063226/jinja.txt)
```// {{ic_name}}
module {{module_name}}(
    {% for input in ports.inputs %}
    input {{input}},
    {% endfor %}
    {% for output in ports.outputs %}
    output {{output}},
    {% endfor %}
);

assign {{ports.outputs[0]}} = ~({{ports.inputs[0]}} & {{ports.inputs[1]}});
// ... more gates

endmodule
```


