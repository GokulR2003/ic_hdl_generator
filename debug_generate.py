#!/usr/bin/env python3
import json
from jinja2 import Environment, FileSystemLoader

# Load metadata
with open('Ic_Metadata_Master.json', 'r') as f:
    metadata = json.load(f)

# Find 7400
ic_data = None
for ic in metadata:
    if ic['part_number'] == '7400':
        ic_data = ic
        break

print("IC Data Found:")
print(json.dumps(ic_data, indent=2))

# Try to load template
env = Environment(loader=FileSystemLoader('hdl_templates/verilog/combinational/basic_gates/'))
template = env.get_template('nand_quad.vtpl')

# Render template
from datetime import datetime
ic_data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

print("\n\nRendering template...")
result = template.render(**ic_data)
print("\n\nGenerated Output (first 500 chars):")
print(result[:500])
