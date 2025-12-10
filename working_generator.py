#!/usr/bin/env python3
"""
Improved HDL Generator - Better template finding
"""

import json
import os
import sys
import argparse
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

class WorkingGenerator:
    def __init__(self):
        self.metadata = self.load_metadata()
        self.template_dir = 'hdl_templates'
        self.env = Environment(
            loader=FileSystemLoader(self.template_dir),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Build template map
        self.template_map = self.build_template_map()
    
    def load_metadata(self):
        with open('Ic_Metadata_Master.json', 'r') as f:
            return json.load(f)
    
    def build_template_map(self):
        """Map IC part numbers to their template paths"""
        template_map = {}
        
        # Scan all templates
        for root, dirs, files in os.walk(self.template_dir):
            for file in files:
                if file.endswith('.vtpl'):
                    template_base = file.replace('.vtpl', '')
                    
                    # Find ICs that use this template
                    for ic in self.metadata:
                        if ic.get('template') == template_base:
                            rel_path = os.path.relpath(os.path.join(root, file), self.template_dir)
                            template_map[ic['part_number']] = rel_path
        
        return template_map
    
    def generate_ic(self, part_number, output_dir='generated_verilog_fixed'):
        # Find IC
        ic = None
        for item in self.metadata:
            if item['part_number'] == part_number:
                ic = item
                break
        
        if not ic:
            print(f"Error: IC {part_number} not found")
            return False
        
        print(f"\nGenerating {part_number} - {ic['ic_name']}")
        
        # Find template
        template_path = self.template_map.get(part_number)
        
        if not template_path:
            # Try to find by template name
            template_name = ic.get('template', '')
            if template_name:
                # Search in common directories
                search_dirs = [
                    'verilog/combinational/basic_gates',
                    'verilog/combinational/decoders',
                    'verilog/combinational/multiplexers',
                    'verilog/combinational/encoders',
                    'verilog/combinational/special',
                    'verilog/sequential/flip_flops',
                    'verilog/sequential/counters',
                    'verilog/transceivers',
                    'verilog/special_analog',
                ]
                
                for search_dir in search_dirs:
                    possible_path = f"{search_dir}/{template_name}.vtpl"
                    full_path = os.path.join(self.template_dir, possible_path)
                    if os.path.exists(full_path):
                        template_path = possible_path
                        self.template_map[part_number] = template_path
                        break
        
        if template_path:
            print(f"  ✓ Found template: {template_path}")
        else:
            print(f"  ✗ No template found, using generic")
            template_path = "verilog/generic.vtpl"
        
        # Prepare data
        ic['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ic.setdefault('ports', {})
        ic['ports'].setdefault('inputs', [])
        ic['ports'].setdefault('outputs', [])
        ic['ports'].setdefault('bidirectional', [])
        ic['ports'].setdefault('power', ['VCC', 'GND'])
        
        # Render template
        try:
            template = self.env.get_template(template_path)
            code = template.render(**ic)
        except Exception as e:
            print(f"  ✗ Template error: {e}")
            return False
        
        # Save file
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f"IC_{part_number}.v")
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(code)
            
            file_size = os.path.getsize(output_file)
            print(f"  ✓ Saved: {output_file} ({file_size} bytes)")
            return True
            
        except Exception as e:
            print(f"  ✗ File write error: {e}")
            return False
    
    def generate_all(self, output_dir='generated_verilog_fixed'):
        print("Generating ALL ICs")
        print("=" * 60)
        
        success = 0
        total = len(self.metadata)
        
        for ic in self.metadata:
            part = ic['part_number']
            
            if self.generate_ic(part, output_dir):
                success += 1
        
        print("\n" + "=" * 60)
        print(f"SUMMARY: {success}/{total} ICs generated")
        
        # Show template usage
        print("\nTemplate usage summary:")
        for part, template in sorted(self.template_map.items()):
            print(f"  {part}: {template}")
    
    def list_ics(self):
        print("ICs with template status:")
        print("=" * 60)
        
        for ic in self.metadata:
            part = ic['part_number']
            name = ic['ic_name']
            template = self.template_map.get(part, "NOT FOUND")
            
            status = "✓" if template != "NOT FOUND" else "✗"
            print(f"{status} {part:8} - {name:40}")

def main():
    parser = argparse.ArgumentParser(description='Working HDL Generator')
    parser.add_argument('command', choices=['generate', 'generate-all', 'list'])
    parser.add_argument('part_number', nargs='?', help='IC part number')
    parser.add_argument('--output-dir', default='generated_verilog_fixed')
    
    args = parser.parse_args()
    
    generator = WorkingGenerator()
    
    if args.command == 'list':
        generator.list_ics()
    
    elif args.command == 'generate':
        if not args.part_number:
            print("Error: Part number required")
            return
        generator.generate_ic(args.part_number, args.output_dir)
    
    elif args.command == 'generate-all':
        generator.generate_all(args.output_dir)

if __name__ == '__main__':
    main()
