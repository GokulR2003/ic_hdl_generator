#!/usr/bin/env python3
"""
Update template names in metadata to match actual .vtpl files
"""

import json
import os

# Load metadata
with open('Ic_Metadata_Master.json', 'r') as f:
    metadata = json.load(f)

# Find all actual template files
actual_templates = {}
for root, dirs, files in os.walk("hdl_templates"):
    for file in files:
        if file.endswith('.vtpl'):
            template_name = file.replace('.vtpl', '')
            actual_templates[template_name] = os.path.join(root, file)

print("Actual template files found:")
for name, path in sorted(actual_templates.items()):
    print(f"  {name:30} -> {path}")

print("\n" + "=" * 60)
print("Updating metadata template names...")

# Map of current template names to actual template files
# Based on your output, these are the mismatches:
template_mapping = {
    # These are correct
    'nand_quad': 'nand_quad',
    'nor_quad': 'nor_quad',
    'inverter_hex': 'inverter_hex',
    'and_quad': 'and_quad',
    'or_quad': 'or_quad',
    'xor_quad': 'xor_quad',
    'd_ff_dual_async': 'd_ff_dual_async',
    'jk_ff_dual': 'jk_ff_dual',
    'decoder_3to8': 'decoder_3to8',
    'decoder_2to4_dual': 'decoder_2to4_dual',
    'encoder_10to4_priority': 'encoder_10to4_priority',
    'mux_4to1_dual': 'mux_4to1_dual',
    'decoder_bcd_7seg': 'decoder_bcd_7seg',
    'comparator_4bit': 'comparator_4bit',
    'transceiver_8bit': 'transceiver_8bit',
    
    # These need fixing - metadata template doesn't match actual file
    'counter_decade_7490': 'counter_decade_7490',  # 7490
    'counter_4bit_binary_7493': 'counter_4bit_binary_7493',  # 7493
    'monostable_74121': 'monostable_74121',  # 74121
    'timer_555_behavioral': 'timer_555_behavioral',  # 555
    'counter_decade_4017': 'counter_decade_4017',  # 4017
}

# Update metadata
updated_count = 0
for ic in metadata:
    part = ic['part_number']
    current_template = ic.get('template', '')
    
    # Check if template exists
    if current_template in actual_templates:
        print(f"✓ {part:8}: template '{current_template}' exists")
    else:
        # Try to find correct template
        for actual_template in actual_templates:
            if part in actual_template or ic['subtype'] in actual_template:
                ic['template'] = actual_template
                print(f"↳ {part:8}: changed '{current_template}' -> '{actual_template}'")
                updated_count += 1
                break
        else:
            print(f"✗ {part:8}: template '{current_template}' NOT FOUND")

# Save updated metadata
with open('Ic_Metadata_Master_updated.json', 'w') as f:
    json.dump(metadata, f, indent=2)

print(f"\nUpdated {updated_count} ICs")
print("Saved to: Ic_Metadata_Master_updated.json")
print("\nTo use: cp Ic_Metadata_Master_updated.json Ic_Metadata_Master.json")
