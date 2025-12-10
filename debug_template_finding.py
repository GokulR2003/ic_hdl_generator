#!/usr/bin/env python3
"""
Debug why templates aren't being found
"""

import json
import os

# Load metadata
with open('Ic_Metadata_Master.json', 'r') as f:
    metadata = json.load(f)

print("Checking template matching for problem ICs:")
print("=" * 60)

problem_ics = ['74138', '74139', '74147', '74153', '7447', '7485', '74121', '74245', '555']

for ic in metadata:
    part = ic['part_number']
    if part not in problem_ics:
        continue
    
    template_name = ic.get('template', '')
    print(f"\n{part} - {ic['ic_name']}")
    print(f"  Template field: '{template_name}'")
    
    # Check if template exists
    found = False
    for root, dirs, files in os.walk('hdl_templates'):
        for file in files:
            if file == f"{template_name}.vtpl":
                rel_path = os.path.relpath(os.path.join(root, file), 'hdl_templates')
                print(f"  ✓ FOUND: {rel_path}")
                found = True
    
    if not found:
        print(f"  ✗ NOT FOUND: {template_name}.vtpl")
        print(f"    Searching for similar files...")
        for root, dirs, files in os.walk('hdl_templates'):
            for file in files:
                if file.endswith('.vtpl') and template_name in file:
                    rel_path = os.path.relpath(os.path.join(root, file), 'hdl_templates')
                    print(f"    Similar: {rel_path}")
