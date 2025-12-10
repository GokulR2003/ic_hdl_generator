#!/usr/bin/env python3
"""
Create missing template files with simple implementations
"""

import json
import os

# Load metadata
with open('Ic_Metadata_Master.json', 'r') as f:
    metadata = json.load(f)

# Template directory structure
template_dirs = {
    'nand_quad': 'verilog/combinational/basic_gates',
    'nor_quad': 'verilog/combinational/basic_gates',
    'inverter_hex': 'verilog/combinational/basic_gates',
    'and_quad': 'verilog/combinational/basic_gates',
    'or_quad': 'verilog/combinational/basic_gates',
    'xor_quad': 'verilog/combinational/basic_gates',
    'd_ff_dual_async': 'verilog/sequential/flip_flops',
    'jk_ff_dual': 'verilog/sequential/flip_flops',
    'decoder_3to8': 'verilog/combinational/decoders',
    'decoder_2to4_dual': 'verilog/combinational/decoders',
    'encoder_10to4_priority': 'verilog/combinational/encoders',
    'mux_4to1_dual': 'verilog/combinational/multiplexers',
    'decoder_bcd_7seg': 'verilog/combinational/special',
    'comparator_4bit': 'verilog/combinational/special',
    'counter_decade_7490': 'verilog/sequential/counters',
    'counter_4bit_binary_7493': 'verilog/sequential/counters',
    'monostable_74121': 'verilog/special_analog',
    'transceiver_8bit': 'verilog/transceivers',
    'timer_555_behavioral': 'verilog/special_analog',
    'counter_decade_4017': 'verilog/sequential/counters',
}

print("Creating missing template files...")
print("=" * 60)

created_count = 0
for ic in metadata:
    part = ic['part_number']
    template_name = ic.get('template', '')
    
    if not template_name:
        print(f"✗ {part:8}: No template name in metadata")
        continue
    
    # Determine directory
    dir_path = None
    for key, template_dir in template_dirs.items():
        if key in template_name or template_name in key:
            dir_path = template_dir
            break
    
    if not dir_path:
        # Guess based on category
        category = ic.get('category', 'combinational')
        if category == 'sequential':
            dir_path = 'verilog/sequential/flip_flops'
        elif category == 'counter':
            dir_path = 'verilog/sequential/counters'
        elif category == 'special':
            dir_path = 'verilog/special_analog'
        else:
            dir_path = 'verilog/combinational/basic_gates'
    
    # Create directory if needed
    full_dir = os.path.join('hdl_templates', dir_path)
    os.makedirs(full_dir, exist_ok=True)
    
    # Check if template already exists
    template_file = os.path.join(full_dir, f"{template_name}.vtpl")
    
    if os.path.exists(template_file):
        print(f"✓ {part:8}: {template_name}.vtpl already exists")
    else:
        # Create simple template
        template_content = f"""// Auto-generated template for {part}
// IC: {ic['ic_name']}
// This is a minimal template - customize as needed

`timescale 1ns / 1ps

module IC_{part}(
    // Input ports
    {% for input in ports.inputs %}
    input wire {{input}},
    {% endfor %}
    
    // Output ports
    {% for output in ports.outputs %}
    output wire {{output}},
    {% endfor %}
    
    // Bidirectional ports
    {% for bidir in ports.bidirectional %}
    inout wire {{bidir}},
    {% endfor %}
    
    // Power ports
    {% for power in ports.power %}
    input wire {{power}},
    {% endfor %}
);

// Simple implementation for {ic['ic_name']}
// TODO: Replace with actual logic

{% for output in ports.outputs %}
assign {{output}} = 1'b0;  // Placeholder
{% endfor %}

endmodule
"""
        
        with open(template_file, 'w') as f:
            f.write(template_content)
        
        print(f"↳ {part:8}: Created {template_name}.vtpl in {dir_path}/")
        created_count += 1

print(f"\nCreated {created_count} new template files")
