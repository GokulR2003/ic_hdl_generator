#!/bin/bash
# Setup script for IC HDL Generator

echo "Setting up IC HDL Generator..."
echo "================================"

# Create directories
mkdir -p hdl_templates/verilog/{combinational/{basic_gates,decoders,multiplexers,encoders,special},sequential/{flip_flops,counters},transceivers,special_analog}
mkdir -p generated_verilog generated_verilog_fixed examples

# Install dependencies
echo "Installing Python dependencies..."
pip install jinja2 2>/dev/null || pip3 install jinja2

# Run quick start
echo "Running quick start..."
python quick_start.py

# Create templates
echo "Creating template files..."
python create_all_templates.py 2>/dev/null || echo "Template script not found - creating basic ones manually"

# Create basic generic template
echo '// Generic template
module IC_{{part_number}}(
{% for input in ports.inputs %} input {{input}},
{% endfor %}{% for output in ports.outputs %} output {{output}},
{% endfor %} input VCC, input GND
);
{% for output in ports.outputs %} assign {{output}} = 0;
{% endfor %}endmodule' > hdl_templates/verilog/generic.vtpl

echo "================================"
echo "Setup complete!"
echo ""
echo "Try these commands:"
echo "1. python template_engine.py list"
echo "2. python template_engine.py generate 7400"
echo "3. python working_generator.py generate-all"
