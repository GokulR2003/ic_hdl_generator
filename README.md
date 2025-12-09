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



