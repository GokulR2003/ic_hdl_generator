#!/usr/bin/env python3
"""
Main HDL Generator - Command Line Interface
Generates Verilog code from IC metadata
"""

import json
import os
import sys
import argparse
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

class HDLGenerator:
    def __init__(self):
        self.metadata_file = 'Ic_Metadata_Master.json'
        self.template_dir = 'hdl_templates'
        self.metadata = self.load_metadata()
        self.env = Environment(
            loader=FileSystemLoader(self.template_dir),
            trim_blocks=True,
            lstrip_blocks=True
        )
    
    def load_metadata(self):
        with open(self.metadata_file, 'r') as f:
            return json.load(f)
    
    def find_ic(self, part_number):
        for ic in self.metadata:
            if ic['part_number'] == part_number:
                return ic
        return None
    
    def find_template(self, ic_data):
        """Find template file for IC"""
        part = ic_data['part_number']
        template_name = ic_data.get('template', ic_data.get('subtype', 'generic'))
        
        # Possible template locations
        search_paths = [
            # By template name
            f"verilog/combinational/basic_gates/{template_name}.vtpl",
            f"verilog/combinational/decoders/{template_name}.vtpl",
            f"verilog/combinational/multiplexers/{template_name}.vtpl",
            f"verilog/combinational/encoders/{template_name}.vtpl",
            f"verilog/combinational/special/{template_name}.vtpl",
            f"verilog/sequential/flip_flops/{template_name}.vtpl",
            f"verilog/sequential/counters/{template_name}.vtpl",
            f"verilog/transceivers/{template_name}.vtpl",
            f"verilog/special_analog/{template_name}.vtpl",
            # By part number
            f"verilog/combinational/basic_gates/IC_{part}.vtpl",
            f"verilog/sequential/flip_flops/IC_{part}.vtpl",
            # Generic fallback
            f"verilog/generic.vtpl",
        ]
        
        for template_path in search_paths:
            full_path = os.path.join(self.template_dir, template_path)
            if os.path.exists(full_path):
                return template_path
        
        return None
    
    def generate_hdl(self, part_number, output_dir='generated_verilog'):
        # Find IC
        ic = self.find_ic(part_number)
        if not ic:
            print(f"Error: IC {part_number} not found")
            return False
        
        print(f"Generating {part_number} - {ic['ic_name']}")
        
        # Find template
        template_path = self.find_template(ic)
        if not template_path:
            print(f"  ✗ No template found")
            return False
        
        print(f"  ✓ Using template: {template_path}")
        
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
    
    def generate_all(self, output_dir='generated_verilog'):
        print(f"Generating all ICs to {output_dir}/")
        print("=" * 50)
        
        success = 0
        total = len(self.metadata)
        
        for ic in self.metadata:
            part = ic['part_number']
            if self.generate_hdl(part, output_dir):
                success += 1
        
        print("=" * 50)
        print(f"Generated: {success}/{total} ICs")
        
        # List generated files
        if os.path.exists(output_dir):
            files = [f for f in os.listdir(output_dir) if f.endswith('.v')]
            print(f"\nFiles in {output_dir}/: {len(files)}")
    
    def list_ics(self):
        print("\nAvailable ICs:")
        print("=" * 50)
        
        # Group by category
        categories = {}
        for ic in self.metadata:
            category = ic.get('category', 'Unknown')
            if category not in categories:
                categories[category] = []
            categories[category].append(ic)
        
        for category, ics in sorted(categories.items()):
            print(f"\n{category.upper()}:")
            print("-" * 30)
            for ic in sorted(ics, key=lambda x: x['part_number']):
                print(f"  {ic['part_number']:8} - {ic['ic_name']}")
        
        print(f"\nTotal: {len(self.metadata)} ICs")

def main():
    parser = argparse.ArgumentParser(
        description='Generate Verilog from IC metadata',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s list
  %(prog)s generate 7400
  %(prog)s generate-all --output-dir my_design
        '''
    )
    
    parser.add_argument('command', 
                       choices=['generate', 'generate-all', 'list'],
                       help='Command to execute')
    
    parser.add_argument('part_number', nargs='?',
                       help='IC part number (e.g., 7400, 7474)')
    
    parser.add_argument('--output-dir', default='generated_verilog',
                       help='Output directory')
    
    args = parser.parse_args()
    
    generator = HDLGenerator()
    
    if args.command == 'list':
        generator.list_ics()
    
    elif args.command == 'generate':
        if not args.part_number:
            print("Error: Part number required for 'generate' command")
            return
        generator.generate_hdl(args.part_number, args.output_dir)
    
    elif args.command == 'generate-all':
        generator.generate_all(args.output_dir)

if __name__ == '__main__':
    main()
