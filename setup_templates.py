#!/usr/bin/env python3
"""
Create all template directories and files
"""

import os

# Create directories
directories = [
    'hdl_templates/verilog/combinational/basic_gates',
    'hdl_templates/verilog/combinational/decoders',
    'hdl_templates/verilog/combinational/multiplexers',
    'hdl_templates/verilog/combinational/encoders',
    'hdl_templates/verilog/combinational/special',
    'hdl_templates/verilog/sequential/flip_flops',
    'hdl_templates/verilog/sequential/counters',
    'hdl_templates/verilog/transceivers',
    'hdl_templates/verilog/special_analog',
]

for dir_path in directories:
    os.makedirs(dir_path, exist_ok=True)
    print(f"Created: {dir_path}/")

# List of ICs and their templates
ic_templates = {
    # Basic gates
    '7400': 'nand_quad',
    '7402': 'nor_quad',
    '7404': 'inverter_hex',
    '7408': 'and_quad',
    '7432': 'or_quad',
    '7486': 'xor_quad',
    
    # Sequential
    '7474': 'd_ff_dual_async',
    '7476': 'jk_ff_dual',
    '7490': 'counter_decade_7490',
    '7493': 'counter_4bit_binary_7493',
    '4017': 'counter_decade_4017',
    
    # Decoders
    '74138': 'decoder_3to8',
    '74139': 'decoder_2to4_dual',
    
    # Multiplexers
    '74153': 'mux_4to1_dual',
    
    # Encoders
    '74147': 'encoder_10to4_priority',
    
    # Special
    '7447': 'decoder_bcd_7seg',
    '7485': 'comparator_4bit',
    '74245': 'transceiver_8bit',
    '74121': 'monostable_74121',
    '555': 'timer_555_behavioral',
}

print(f"\nTemplates needed for {len(ic_templates)} ICs")
print("Copy the template files I provided to their respective directories")
