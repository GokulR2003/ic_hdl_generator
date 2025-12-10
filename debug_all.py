#!/usr/bin/env python3
import json
import os

with open('Ic_Metadata_Master.json', 'r') as f:
    metadata = json.load(f)

print(f"Total ICs in metadata: {len(metadata)}")
print("\nChecking templates for each IC:")

for ic in metadata:
    part = ic['part_number']
    subtype = ic.get('subtype', 'generic')
    template_path = f"hdl_templates/verilog/combinational/basic_gates/{subtype}.vtpl"
    
    if os.path.exists(template_path):
        status = "✓ Template exists"
    else:
        # Check other possible locations
        found = False
        for dir_name in ['basic_gates', 'decoders', 'multiplexers', 'encoders', 
                        'special', 'flip_flops', 'counters', 'transceivers', 
                        'special_analog']:
            path = f"hdl_templates/verilog/{dir_name}/{subtype}.vtpl"
            if os.path.exists(path):
                status = f"✓ Template in {dir_name}/"
                found = True
                break
        
        if not found:
            status = "✗ MISSING TEMPLATE"
    
    print(f"{part:8} - {subtype:25} - {status}")
