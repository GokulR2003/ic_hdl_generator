#!/usr/bin/env python3
"""
HDL Template Engine - Fixed Version
"""

import json
import os
import sys
import argparse
from datetime import datetime
from pathlib import Path

try:
    from jinja2 import Environment, FileSystemLoader, TemplateNotFound
    JINJA2_AVAILABLE = True
except ImportError:
    print("Error: Jinja2 is required. Install with: pip install jinja2")
    sys.exit(1)

class HDLGenerator:
    def __init__(self, metadata_file='Ic_Metadata_Master.json', 
                 template_dir='hdl_templates'):
        self.metadata_file = metadata_file
        self.template_dir = Path(template_dir)
        self.metadata = self.load_metadata()
        self.env = Environment(
            loader=FileSystemLoader(self.template_dir),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
    def load_metadata(self):
        try:
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading metadata: {e}")
            return []
    
    def find_ic(self, part_number):
        for ic in self.metadata:
            if ic['part_number'] == part_number:
                return ic
        return None
    
    def generate_hdl(self, part_number, language='verilog', output_dir=None):
        ic_data = self.find_ic(part_number)
        if not ic_data:
            print(f"Error: IC {part_number} not found")
            return None
        
        # Ensure all required fields exist
        ic_data.setdefault('ports', {})
        ic_data['ports'].setdefault('inputs', [])
        ic_data['ports'].setdefault('outputs', [])
        ic_data['ports'].setdefault('bidirectional', [])
        ic_data['ports'].setdefault('power', ['VCC', 'GND'])
        ic_data.setdefault('template', ic_data.get('subtype', 'generic'))
        
        # Add generation info
        ic_data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Determine template path
        template_name = ic_data['template']
        if language == 'verilog':
            template_ext = '.vtpl'
        else:
            template_ext = '.vhdltpl'
        
        # Try to find template
        template_paths = [
            f"verilog/combinational/basic_gates/{template_name}{template_ext}",
            f"verilog/combinational/{template_name}{template_ext}",
            f"verilog/{template_name}{template_ext}",
            f"verilog/generic{template_ext}",
        ]
        
        template_content = None
        for path in template_paths:
            full_path = self.template_dir / path
            if full_path.exists():
                try:
                    template = self.env.get_template(path)
                    template_content = template.render(**ic_data)
                    print(f"Used template: {path}")
                    break
                except Exception as e:
                    print(f"Error rendering template {path}: {e}")
        
        # If no template found, use fallback
        if template_content is None:
            print(f"Warning: No template found for {template_name}, using fallback")
            template_content = self.generate_fallback(ic_data, language)
        
        # Save to file
        if output_dir:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            if language == 'verilog':
                filename = f"IC_{part_number}.v"
            else:
                filename = f"IC_{part_number}.vhd"
            
            filepath = output_dir / filename
            
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(template_content)
                print(f"Successfully generated: {filepath}")
                print(f"File size: {len(template_content)} bytes")
            except Exception as e:
                print(f"Error writing file: {e}")
        
        return template_content
    
    def generate_fallback(self, ic_data, language):
        """Generate fallback HDL when template is missing"""
        part_number = ic_data['part_number']
        ports = ic_data['ports']
        
        if language == 'verilog':
            code = f"""// Auto-generated fallback for {part_number}
// This is a fallback implementation

`timescale 1ns / 1ps

module IC_{part_number}(
"""
            # Add inputs
            for inp in ports['inputs']:
                code += f"    input wire {inp},\n"
            
            # Add outputs
            for i, outp in enumerate(ports['outputs']):
                if i == len(ports['outputs']) - 1 and not ports['bidirectional']:
                    code += f"    output wire {outp}\n"
                else:
                    code += f"    output wire {outp},\n"
            
            # Add bidirectional
            for i, bidir in enumerate(ports['bidirectional']):
                if i == len(ports['bidirectional']) - 1:
                    code += f"    inout wire {bidir}\n"
                else:
                    code += f"    inout wire {bidir},\n"
            
            # Add power
            if ports['power']:
                code += "    // Power pins\n"
                for power in ports['power']:
                    code += f"    input wire {power},\n"
                code = code.rstrip(',\n') + "\n"
            
            code += ");\n\n"
            code += "    // Fallback implementation - all outputs tied to 0\n"
            for outp in ports['outputs']:
                code += f"    assign {outp} = 1'b0;\n"
            
            code += "\nendmodule\n"
        else:
            # VHDL fallback
            code = f"""-- Auto-generated fallback for {part_number}
-- This is a fallback implementation

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity IC_{part_number} is
    Port (
"""
            # Add all ports...
            code += "    );\nend IC_{part_number};\n\n"
            code += "architecture Behavioral of IC_{part_number} is\nbegin\n    -- Fallback\nend Behavioral;\n"
        
        return code
    
    def generate_all(self, language='verilog', output_dir=None):
        if output_dir is None:
            output_dir = f"generated_{language}"
        
        success = 0
        total = len(self.metadata)
        
        print(f"Generating {language.upper()} for {total} ICs...")
        print("=" * 60)
        
        for ic in self.metadata:
            part = ic['part_number']
            name = ic['ic_name']
            
            try:
                self.generate_hdl(part, language, output_dir)
                print(f"✓ {part}: {name}")
                success += 1
            except Exception as e:
                print(f"✗ {part}: Error - {e}")
        
        print("=" * 60)
        print(f"Generated {success}/{total} ICs successfully")
    
    def list_ics(self):
        print("\nAvailable ICs:")
        print("=" * 60)
        
        for ic in sorted(self.metadata, key=lambda x: x['part_number']):
            print(f"{ic['part_number']:8} - {ic['ic_name']}")
        
        print(f"\nTotal: {len(self.metadata)} ICs")

def main():
    parser = argparse.ArgumentParser(description='Generate HDL from IC metadata')
    subparsers = parser.add_subparsers(dest='command', help='Command')
    
    # Generate command
    gen_parser = subparsers.add_parser('generate', help='Generate HDL for IC')
    gen_parser.add_argument('part_number', help='IC part number')
    gen_parser.add_argument('--language', choices=['verilog', 'vhdl'], default='verilog')
    gen_parser.add_argument('--output-dir', default='generated_verilog')
    
    # Generate all command
    all_parser = subparsers.add_parser('generate-all', help='Generate all ICs')
    all_parser.add_argument('--language', choices=['verilog', 'vhdl'], default='verilog')
    all_parser.add_argument('--output-dir')
    
    # List command
    subparsers.add_parser('list', help='List all ICs')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    generator = HDLGenerator()
    
    if args.command == 'generate':
        generator.generate_hdl(args.part_number, args.language, args.output_dir)
    
    elif args.command == 'generate-all':
        output_dir = args.output_dir or f"generated_{args.language}"
        generator.generate_all(args.language, output_dir)
    
    elif args.command == 'list':
        generator.list_ics()

if __name__ == '__main__':
    main()
