#!/usr/bin/env python3
"""
Simple but working HDL Generator
"""

import json
import os
import sys
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

class SimpleHDLGenerator:
    def __init__(self):
        self.metadata = self.load_metadata()
        self.template_dir = 'hdl_templates'
        self.env = Environment(loader=FileSystemLoader(self.template_dir))
        
    def load_metadata(self):
        with open('Ic_Metadata_Master.json', 'r') as f:
            return json.load(f)
    
    def find_ic(self, part_number):
        for ic in self.metadata:
            if ic['part_number'] == part_number:
                return ic
        return None
    
    def generate(self, part_number, output_dir='generated_verilog'):
        ic = self.find_ic(part_number)
        if not ic:
            print(f"Error: IC {part_number} not found")
            return False
        
        # Prepare data
        ic['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Ensure all fields exist
        ic.setdefault('ports', {})
        ic['ports'].setdefault('inputs', [])
        ic['ports'].setdefault('outputs', [])
        ic['ports'].setdefault('bidirectional', [])
        ic['ports'].setdefault('power', ['VCC', 'GND'])
        
        # Determine template
        subtype = ic.get('subtype', 'generic')
        
        # Try to find template
        template_paths = [
            f"verilog/combinational/basic_gates/{subtype}.vtpl",
            f"verilog/combinational/decoders/{subtype}.vtpl",
            f"verilog/combinational/multiplexers/{subtype}.vtpl",
            f"verilog/combinational/encoders/{subtype}.vtpl",
            f"verilog/combinational/special/{subtype}.vtpl",
            f"verilog/sequential/flip_flops/{subtype}.vtpl",
            f"verilog/sequential/counters/{subtype}.vtpl",
            f"verilog/transceivers/{subtype}.vtpl",
            f"verilog/special_analog/{subtype}.vtpl",
            f"verilog/generic.vtpl"
        ]
        
        template = None
        template_used = None
        
        for path in template_paths:
            full_path = os.path.join(self.template_dir, path)
            if os.path.exists(full_path):
                try:
                    template = self.env.get_template(path)
                    template_used = path
                    break
                except:
                    continue
        
        if not template:
            print(f"Error: No template found for {subtype}")
            return False
        
        # Generate code
        try:
            code = template.render(**ic)
        except Exception as e:
            print(f"Error rendering template: {e}")
            return False
        
        # Save file
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f"IC_{part_number}.v")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(code)
        
        print(f"✓ Generated: {output_file} (using {template_used})")
        return True
    
    def generate_all(self, output_dir='generated_verilog'):
        print(f"Generating all ICs to {output_dir}/")
        print("=" * 60)
        
        success = 0
        total = len(self.metadata)
        
        for ic in self.metadata:
            part = ic['part_number']
            name = ic['ic_name']
            
            if self.generate(part, output_dir):
                success += 1
                print(f"  {part}: {name}")
            else:
                print(f"✗ {part}: FAILED - {name}")
        
        print("=" * 60)
        print(f"Successfully generated: {success}/{total} ICs")
    
    def list_all(self):
        print("\nAvailable ICs:")
        print("=" * 60)
        
        for ic in self.metadata:
            print(f"{ic['part_number']:8} - {ic['ic_name']}")
        
        print(f"\nTotal: {len(self.metadata)} ICs")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate HDL from IC metadata')
    parser.add_argument('command', choices=['generate', 'generate-all', 'list'], 
                       help='Command to execute')
    parser.add_argument('part_number', nargs='?', help='IC part number')
    parser.add_argument('--output-dir', default='generated_verilog', 
                       help='Output directory')
    
    args = parser.parse_args()
    
    generator = SimpleHDLGenerator()
    
    if args.command == 'list':
        generator.list_all()
    
    elif args.command == 'generate':
        if not args.part_number:
            print("Error: Part number required")
            return
        generator.generate(args.part_number, args.output_dir)
    
    elif args.command == 'generate-all':
        generator.generate_all(args.output_dir)

if __name__ == '__main__':
    main()
