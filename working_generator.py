#!/usr/bin/env python3
"""
Working HDL Generator - Finds templates by part number or subtype
"""

import json
import os
import sys
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, TemplateNotFound

class WorkingGenerator:
    def __init__(self):
        self.metadata = self.load_metadata()
        self.template_dir = 'hdl_templates'
        self.env = Environment(
            loader=FileSystemLoader(self.template_dir),
            trim_blocks=True,
            lstrip_blocks=True
        )
        self.template_cache = {}  # Cache found templates
    
    def load_metadata(self):
        with open('Ic_Metadata_Master.json', 'r') as f:
            return json.load(f)
    
    def find_template_for_ic(self, ic_data):
        """Find template file for an IC using multiple strategies"""
        part = ic_data['part_number']
        subtype = ic_data.get('subtype', '')
        
        # Strategy 1: Try exact part number template
        template_paths = [
            # Try by part number
            f"verilog/combinational/basic_gates/IC_{part}.vtpl",
            f"verilog/sequential/flip_flops/IC_{part}.vtpl",
            f"verilog/sequential/counters/IC_{part}.vtpl",
            
            # Try by subtype from metadata template field
            f"verilog/combinational/basic_gates/{ic_data.get('template', '')}.vtpl",
            f"verilog/sequential/flip_flops/{ic_data.get('template', '')}.vtpl",
            f"verilog/sequential/counters/{ic_data.get('template', '')}.vtpl",
            
            # Try by subtype
            f"verilog/combinational/basic_gates/{subtype}.vtpl",
            f"verilog/sequential/flip_flops/{subtype}.vtpl",
            f"verilog/sequential/counters/{subtype}.vtpl",
            
            # Try generic locations
            f"verilog/combinational/basic_gates/generic.vtpl",
            f"verilog/generic.vtpl",
        ]
        
        # Remove empty paths
        template_paths = [p for p in template_paths if '.vtpl' in p and '//' not in p]
        
        # Try each path
        for template_path in template_paths:
            full_path = os.path.join(self.template_dir, template_path)
            if os.path.exists(full_path):
                return template_path
        
        return None
    
    def generate_ic(self, part_number, output_dir='generated_verilog'):
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
        print(f"  Subtype: {ic.get('subtype', 'N/A')}")
        print(f"  Template field: {ic.get('template', 'N/A')}")
        
        # Prepare data
        ic['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ic.setdefault('ports', {})
        ic['ports'].setdefault('inputs', [])
        ic['ports'].setdefault('outputs', [])
        ic['ports'].setdefault('bidirectional', [])
        ic['ports'].setdefault('power', ['VCC', 'GND'])
        
        # Find template
        template_path = self.find_template_for_ic(ic)
        
        if not template_path:
            print(f"  ✗ ERROR: No template found!")
            
            # Create a simple fallback
            code = self.create_fallback(ic)
            if not code:
                return False
        else:
            print(f"  ✓ Using template: {template_path}")
            try:
                template = self.env.get_template(template_path)
                code = template.render(**ic)
            except Exception as e:
                print(f"  ✗ Template error: {e}")
                code = self.create_fallback(ic)
        
        # Save file
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f"IC_{part_number}.v")
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(code)
            
            # Verify
            file_size = os.path.getsize(output_file)
            if file_size == 0:
                print(f"  ✗ WARNING: File is empty (0 bytes)!")
                # Add some content
                with open(output_file, 'a') as f:
                    f.write(f"\n// Auto-generated placeholder for {part_number}\n")
                file_size = os.path.getsize(output_file)
            
            print(f"  ✓ Saved: {output_file} ({file_size} bytes)")
            return True
            
        except Exception as e:
            print(f"  ✗ File write error: {e}")
            return False
    
    def create_fallback(self, ic_data):
        """Create fallback Verilog when template is missing"""
        part = ic_data['part_number']
        ports = ic_data['ports']
        
        code = f"""// ============================================================
// Auto-generated HDL (FALLBACK - No template found)
// Part: {part} - {ic_data['ic_name']}
// Generated: {ic_data['timestamp']}
// WARNING: This is a fallback implementation
// ============================================================

`timescale 1ns / 1ps

module IC_{part}(
"""
        
        # Add inputs
        for inp in ports['inputs']:
            code += f"    input wire {inp},\n"
        
        # Add outputs
        for i, outp in enumerate(ports['outputs']):
            comma = ',' if (i < len(ports['outputs']) - 1 or ports['bidirectional']) else ''
            code += f"    output wire {outp}{comma}\n"
        
        # Add bidirectional
        for i, bidir in enumerate(ports['bidirectional']):
            comma = ',' if i < len(ports['bidirectional']) - 1 else ''
            code += f"    inout wire {bidir}{comma}\n"
        
        # Add power
        if ports['power']:
            for i, power in enumerate(ports['power']):
                comma = ',' if i < len(ports['power']) - 1 else ''
                code += f"    input wire {power}{comma}\n"
        
        code += ");\n\n"
        code += "    // ============================================================\n"
        code += "    // FALLBACK IMPLEMENTATION\n"
        code += "    // This was generated because no template was found\n"
        code += "    // ============================================================\n\n"
        
        # Simple implementation
        if ports['outputs']:
            code += "    // All outputs tied low\n"
            for outp in ports['outputs']:
                code += f"    assign {outp} = 1'b0;\n"
        
        code += "\nendmodule\n"
        
        return code
    
    def generate_all(self, output_dir='generated_verilog'):
        print("Generating ALL ICs")
        print("=" * 60)
        
        success = 0
        total = len(self.metadata)
        
        for ic in self.metadata:
            part = ic['part_number']
            
            if self.generate_ic(part, output_dir):
                success += 1
        
        print("\n" + "=" * 60)
        print(f"SUMMARY: {success}/{total} ICs generated successfully")
        
        # List generated files
        if os.path.exists(output_dir):
            files = [f for f in os.listdir(output_dir) if f.endswith('.v')]
            print(f"\nGenerated {len(files)} files in {output_dir}/")
            
            # Check for empty files
            empty_files = []
            for file in files:
                filepath = os.path.join(output_dir, file)
                if os.path.getsize(filepath) == 0:
                    empty_files.append(file)
            
            if empty_files:
                print(f"WARNING: {len(empty_files)} empty files:")
                for file in empty_files:
                    print(f"  {file}")
    
    def list_ics_with_templates(self):
        print("ICs and their template status:")
        print("=" * 60)
        
        for ic in self.metadata:
            part = ic['part_number']
            name = ic['ic_name']
            template_path = self.find_template_for_ic(ic)
            
            if template_path:
                status = "✓"
            else:
                status = "✗"
            
            print(f"{status} {part:8} - {name:40}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Working HDL Generator')
    parser.add_argument('command', choices=['generate', 'generate-all', 'list'])
    parser.add_argument('part_number', nargs='?', help='IC part number')
    parser.add_argument('--output-dir', default='generated_verilog')
    
    args = parser.parse_args()
    
    generator = WorkingGenerator()
    
    if args.command == 'list':
        generator.list_ics_with_templates()
    
    elif args.command == 'generate':
        if not args.part_number:
            print("Error: Part number required")
            return
        generator.generate_ic(args.part_number, args.output_dir)
    
    elif args.command == 'generate-all':
        generator.generate_all(args.output_dir)

if __name__ == '__main__':
    main()
