#!/usr/bin/env python3
"""
SIMPLE FIX Generator - Direct template matching
"""

import json
import os
import sys
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

class SimpleFixGenerator:
    def __init__(self):
        self.metadata = self.load_metadata()
        self.template_dir = 'hdl_templates'
        self.env = Environment(
            loader=FileSystemLoader(self.template_dir),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Map IC part numbers to their actual template paths
        self.template_map = self.build_template_map()
    
    def load_metadata(self):
        with open('Ic_Metadata_Master.json', 'r') as f:
            return json.load(f)
    
    def build_template_map(self):
        """Build a map of IC part numbers to template paths"""
        template_map = {}
        
        # Scan all template files
        for root, dirs, files in os.walk(self.template_dir):
            for file in files:
                if file.endswith('.vtpl'):
                    # Extract potential IC number from filename
                    # e.g., "decoder_3to8.vtpl" -> look for ICs with decoder_3to8 template
                    template_base = file.replace('.vtpl', '')
                    
                    # Map this template to all ICs that use it
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
        print(f"  Template field: {ic.get('template', 'N/A')}")
        
        # Find template
        template_path = self.template_map.get(part_number)
        
        if not template_path:
            # Try to find by searching
            template_name = ic.get('template', '')
            if template_name:
                # Search for this template
                possible_locations = [
                    f"verilog/combinational/basic_gates/{template_name}.vtpl",
                    f"verilog/combinational/decoders/{template_name}.vtpl",
                    f"verilog/combinational/multiplexers/{template_name}.vtpl",
                    f"verilog/combinational/encoders/{template_name}.vtpl",
                    f"verilog/combinational/special/{template_name}.vtpl",
                    f"verilog/sequential/flip_flops/{template_name}.vtpl",
                    f"verilog/sequential/counters/{template_name}.vtpl",
                    f"verilog/transceivers/{template_name}.vtpl",
                    f"verilog/special_analog/{template_name}.vtpl",
                ]
                
                for location in possible_locations:
                    full_path = os.path.join(self.template_dir, location)
                    if os.path.exists(full_path):
                        template_path = location
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
        
        # Load and render template
        try:
            template = self.env.get_template(template_path)
            code = template.render(**ic)
        except Exception as e:
            print(f"  ✗ Template error: {e}")
            # Create simple fallback
            code = self.create_fallback(ic)
        
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
    
    def create_fallback(self, ic_data):
        """Create simple fallback Verilog"""
        part = ic_data['part_number']
        ports = ic_data['ports']
        
        code = f"""// Fallback for {part} - {ic_data['ic_name']}
// Generated: {ic_data['timestamp']}

module IC_{part}(
"""
        
        # Add all ports
        all_ports = []
        all_ports.extend(ports['inputs'])
        all_ports.extend(ports['outputs'])
        all_ports.extend(ports['bidirectional'])
        all_ports.extend(ports['power'])
        
        for i, port in enumerate(all_ports):
            if 'input' in port or port in ports['inputs'] or port in ports['power']:
                direction = "input"
            elif port in ports['outputs']:
                direction = "output"
            else:
                direction = "inout"
            
            comma = "," if i < len(all_ports) - 1 else ""
            code += f"    {direction} {port}{comma}\n"
        
        code += ");\n\n"
        
        # Simple assignments
        for output in ports['outputs']:
            code += f"    assign {output} = 1'b0;\n"
        
        code += "\nendmodule\n"
        
        return code
    
    def generate_all(self, output_dir='generated_verilog_fixed'):
        print("Generating ALL ICs with FIXED template matching")
        print("=" * 60)
        
        success = 0
        total = len(self.metadata)
        
        for ic in self.metadata:
            part = ic['part_number']
            
            if self.generate_ic(part, output_dir):
                success += 1
        
        print("\n" + "=" * 60)
        print(f"SUMMARY: {success}/{total} ICs generated")
        
        # Show what templates were used
        print("\nTemplate usage:")
        for part, template in sorted(self.template_map.items()):
            print(f"  {part}: {template}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Simple Fix Generator')
    parser.add_argument('command', choices=['generate', 'generate-all', 'list'])
    parser.add_argument('part_number', nargs='?', help='IC part number')
    parser.add_argument('--output-dir', default='generated_verilog_fixed')
    
    args = parser.parse_args()
    
    generator = SimpleFixGenerator()
    
    if args.command == 'list':
        # Show template mapping
        print("IC -> Template mapping:")
        print("=" * 60)
        for ic in generator.metadata:
            part = ic['part_number']
            template = generator.template_map.get(part, "NOT FOUND")
            print(f"{part:8} -> {template}")
    
    elif args.command == 'generate':
        if not args.part_number:
            print("Error: Part number required")
            return
        generator.generate_ic(args.part_number, args.output_dir)
    
    elif args.command == 'generate-all':
        generator.generate_all(args.output_dir)

if __name__ == '__main__':
    main()
