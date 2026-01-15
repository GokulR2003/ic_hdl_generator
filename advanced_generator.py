#!/usr/bin/env python3
"""
Advanced HDL Generator with Testbenches, VHDL, and Boolean Expression Support
"""

import json
import os
import sys
import argparse
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

# Try to import Boolean support modules
try:
    from boolean_to_hdl import BooleanToHDLGenerator
    BOOLEAN_SUPPORT = True
except ImportError as e:
    BOOLEAN_SUPPORT = False
    # Create a dummy class if import fails
    class BooleanToHDLGenerator:
        def __init__(self, *args, **kwargs):
            pass
        def generate(self, *args, **kwargs):
            return {"error": "Boolean modules not installed"}
class AdvancedHDLGenerator:
    def __init__(self):
        self.metadata = self.load_metadata()
        self.template_dir = 'hdl_templates'
        self.testbench_dir = 'testbench_templates'
        self.env = Environment(
            loader=FileSystemLoader([self.template_dir, self.testbench_dir]),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Initialize Boolean generator if available
        if BOOLEAN_SUPPORT:
            self.boolean_gen = BooleanToHDLGenerator()
        
        # Build template maps
        self.verilog_templates = self.build_template_map('verilog')
        self.vhdl_templates = self.build_template_map('vhdl')
        self.testbench_templates = self.build_testbench_map()
    
    def load_metadata(self):
        """Load IC metadata"""
        try:
            with open('Ic_Metadata_Master.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print("Warning: Ic_Metadata_Master.json not found")
            return []
    
    def build_template_map(self, language='verilog'):
        """Map IC part numbers to their template paths"""
        template_map = {}
        ext = '.vtpl' if language == 'verilog' else '.vhdltpl'
        
        # Scan all templates
        for root, dirs, files in os.walk(self.template_dir):
            for file in files:
                if file.endswith(ext):
                    template_base = file.replace(ext, '')
                    
                    # Find ICs that use this template
                    for ic in self.metadata:
                        if ic.get('template') == template_base:
                            rel_path = os.path.relpath(os.path.join(root, file), self.template_dir)
                            template_map[ic['part_number']] = rel_path
        
        return template_map
    
    def build_testbench_map(self):
        """Map IC part numbers to testbench template paths"""
        testbench_map = {}
        
        # Scan testbench templates
        for root, dirs, files in os.walk(self.testbench_dir):
            for file in files:
                if file.endswith('_tb.vtpl'):
                    part = file.split('_')[0]
                    rel_path = os.path.relpath(os.path.join(root, file), self.testbench_dir)
                    testbench_map[part] = rel_path
        
        return testbench_map
    
    def find_template(self, ic_data, language='verilog'):
        """Find appropriate template for IC"""
        part = ic_data['part_number']
        template_name = ic_data.get('template', ic_data.get('subtype', 'generic'))
        
        if language == 'verilog':
            template_map = self.verilog_templates
            ext = '.vtpl'
        else:
            template_map = self.vhdl_templates
            ext = '.vhdltpl'
        
        # Check if we have a direct mapping
        if part in template_map:
            return template_map[part]
        
        # Try to find by template name
        search_paths = []
        category = ic_data.get('category', 'combinational')
        
        # Determine likely directories based on category
        if category == 'combinational':
            dirs = ['combinational/basic_gates', 'combinational/decoders', 
                   'combinational/multiplexers', 'combinational/encoders', 
                   'combinational/special']
        elif category in ['sequential', 'counter']:
            dirs = ['sequential/flip_flops', 'sequential/counters']
        elif category == 'special':
            dirs = ['special_analog', 'transceivers']
        else:
            dirs = ['']
        
        # Generate search paths
        for dir_path in dirs:
            search_paths.append(f"{language}/{dir_path}/{template_name}{ext}")
            search_paths.append(f"{language}/{dir_path}/generic{ext}")
        
        search_paths.append(f"{language}/generic{ext}")
        
        # Try each path
        for template_path in search_paths:
            full_path = os.path.join(self.template_dir, template_path)
            if os.path.exists(full_path):
                return template_path
        
        return None
    
    def find_testbench_template(self, ic_data):
        """Find testbench template for IC"""
        part = ic_data['part_number']
        
        # Check if we have a specific testbench
        if part in self.testbench_templates:
            return self.testbench_templates[part]
        
        # Try to find by category
        category = ic_data.get('category', 'combinational')
        template_name = ic_data.get('template', ic_data.get('subtype', 'generic'))
        
        search_paths = [
            f"verilog/{category}/generic_tb.vtpl",
            f"verilog/generic_tb.vtpl",
        ]
        
        # Try each path
        for template_path in search_paths:
            full_path = os.path.join(self.testbench_dir, template_path)
            if os.path.exists(full_path):
                return template_path
        
        return None
    
    def prepare_ic_data(self, ic_data):
        """Prepare IC data for template rendering"""
        ic_data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ic_data.setdefault('ports', {})
        ic_data['ports'].setdefault('inputs', [])
        ic_data['ports'].setdefault('outputs', [])
        ic_data['ports'].setdefault('bidirectional', [])
        ic_data['ports'].setdefault('power', ['VCC', 'GND'])
        ic_data.setdefault('test_coverage', {})
        ic_data['test_coverage'].setdefault('min_test_vectors', 10)
        ic_data['test_coverage'].setdefault('simulation_duration_ns', 1000)
        ic_data['test_coverage'].setdefault('coverage_target', 95.0)
        
        return ic_data
    
    def generate_hdl(self, part_number, language='verilog', output_dir=None):
        """Generate HDL for specific IC"""
        # Find IC
        ic = None
        for item in self.metadata:
            if item['part_number'] == part_number:
                ic = item
                break
        
        if not ic:
            print(f"Error: IC {part_number} not found")
            return False
        
        print(f"\nGenerating {language.upper()} for {part_number} - {ic['ic_name']}")
        
        # Prepare data
        ic = self.prepare_ic_data(ic)
        
        # Find template
        template_path = self.find_template(ic, language)
        
        if not template_path:
            print(f"  ✗ No {language.upper()} template found")
            return False
        
        print(f"  ✓ Using template: {template_path}")
        
        # Render template
        try:
            template = self.env.get_template(template_path)
            code = template.render(**ic)
        except Exception as e:
            print(f"  ✗ Template error: {e}")
            return False
        
        # Determine output directory and filename
        if output_dir is None:
            output_dir = f"generated_{language}"
        
        if language == 'verilog':
            ext = '.v'
        else:
            ext = '.vhd'
        
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f"IC_{part_number}{ext}")
        
        # Save file
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(code)
            
            file_size = os.path.getsize(output_file)
            print(f"  ✓ Saved: {output_file} ({file_size} bytes)")
            return True
            
        except Exception as e:
            print(f"  ✗ File write error: {e}")
            return False
    
    def generate_testbench(self, part_number, output_dir=None):
        """Generate testbench for specific IC"""
        # Find IC
        ic = None
        for item in self.metadata:
            if item['part_number'] == part_number:
                ic = item
                break
        
        if not ic:
            print(f"Error: IC {part_number} not found")
            return False
        
        print(f"\nGenerating testbench for {part_number} - {ic['ic_name']}")
        
        # Prepare data
        ic = self.prepare_ic_data(ic)
        
        # Find testbench template
        template_path = self.find_testbench_template(ic)
        
        if not template_path:
            print(f"  ✗ No testbench template found")
            return False
        
        print(f"  ✓ Using testbench template: {template_path}")
        
        # Render template
        try:
            template = self.env.get_template(template_path)
            code = template.render(**ic)
        except Exception as e:
            print(f"  ✗ Template error: {e}")
            return False
        
        # Determine output directory
        if output_dir is None:
            output_dir = 'generated_testbenches'
        
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f"tb_{part_number}.v")
        
        # Save file
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(code)
            
            file_size = os.path.getsize(output_file)
            print(f"  ✓ Saved: {output_file} ({file_size} bytes)")
            return True
            
        except Exception as e:
            print(f"  ✗ File write error: {e}")
            return False
    
    def generate_all(self, language='verilog', include_testbenches=False):
        """Generate HDL for all ICs"""
        output_dir = f"generated_{language}"
        testbench_dir = 'generated_testbenches'
        
        print(f"\nGenerating {language.upper()} for all ICs")
        print("=" * 60)
        
        success_hdl = 0
        success_tb = 0
        total = len(self.metadata)
        
        for ic in self.metadata:
            part = ic['part_number']
            
            # Generate HDL
            if self.generate_hdl(part, language, output_dir):
                success_hdl += 1
            
            # Generate testbench if requested
            if include_testbenches:
                if self.generate_testbench(part, testbench_dir):
                    success_tb += 1
        
        print("\n" + "=" * 60)
        print(f"HDL Generation: {success_hdl}/{total} ICs")
        
        if include_testbenches:
            print(f"Testbenches:     {success_tb}/{total} ICs")
        
        # List generated files
        if os.path.exists(output_dir):
            files = [f for f in os.listdir(output_dir) if f.endswith(('.v', '.vhd'))]
            print(f"\nGenerated {len(files)} {language.upper()} files in {output_dir}/")
    
    def list_supported(self):
        """List all ICs with template support info"""
        print("\nIC Support Matrix:")
        print("=" * 80)
        print(f"{'Part':8} {'Verilog':10} {'VHDL':10} {'Testbench':12} {'Name'}")
        print("-" * 80)
        
        for ic in self.metadata:
            part = ic['part_number']
            name = ic['ic_name']
            
            verilog_support = "✓" if self.find_template(ic, 'verilog') else "✗"
            vhdl_support = "✓" if self.find_template(ic, 'vhdl') else "✗"
            testbench_support = "✓" if self.find_testbench_template(ic) else "✗"
            
            print(f"{part:8} {verilog_support:10} {vhdl_support:10} {testbench_support:12} {name}")
        
        print(f"\nTotal: {len(self.metadata)} ICs")
    
    def generate_from_boolean(self, expression, circuit_name=None):
        """Generate HDL from Boolean expression"""
        if not BOOLEAN_SUPPORT:
            print("❌ Boolean expression support not available")
            print("Required modules: boolean_to_hdl.py and dependencies")
            return False
        
        print(f"\nGenerating HDL from Boolean expression:")
        print(f"Expression: {expression}")
        
        try:
            # Generate using BooleanToHDLGenerator
            result = self.boolean_gen.generate(expression, circuit_name)
            
            # Save generated files
            output_dir = "generated_verilog"
            os.makedirs(output_dir, exist_ok=True)
            
            # Save Verilog
            verilog_file = os.path.join(output_dir, f"{result['circuit_name']}.v")
            with open(verilog_file, 'w') as f:
                f.write(result['hdl_code'])
            
            # Save testbench
            tb_dir = 'generated_testbenches'
            os.makedirs(tb_dir, exist_ok=True)
            tb_file = os.path.join(tb_dir, f"tb_{result['circuit_name']}.v")
            with open(tb_file, 'w') as f:
                f.write(result['testbench'])
            
            print(f"✓ Generated: {verilog_file}")
            print(f"✓ Testbench: {tb_file}")
            
            # Print summary
            print("\n" + "="*50)
            print("BOOLEAN EXPRESSION GENERATION SUMMARY")
            print("="*50)
            print(f"Circuit: {result['circuit_name']}")
            print(f"Original: {result['original_expression']}")
            print(f"Simplified: {result['simplified_expression']}")
            print(f"Variables: {', '.join(result['variables'])}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error generating from Boolean expression: {e}")
            return False

def main():
    # Create main parser
    parser = argparse.ArgumentParser(
        description='Advanced HDL Generator with Boolean Expression Support',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f'''
Examples:
  IC Generation:
    %(prog)s ic 7400 --language verilog
    %(prog)s ic 7474 --language vhdl
    %(prog)s ic-all --language verilog --testbenches
  
  Boolean Expression Generation: {'✓ Available' if BOOLEAN_SUPPORT else '✗ Not available'}
    %(prog)s boolean "A&B + !C" --name my_circuit
    %(prog)s boolean "A^B" --name xor_gate
  
  Testbenches:
    %(prog)s testbench 7400
    %(prog)s testbench-all
  
  Information:
    %(prog)s list-supported
        '''
    )
    
    # Add subparsers for different commands
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # IC generation command
    ic_parser = subparsers.add_parser('ic', help='Generate HDL for specific IC')
    ic_parser.add_argument('part_number', help='IC part number')
    ic_parser.add_argument('--language', choices=['verilog', 'vhdl'], default='verilog',
                          help='HDL language')
    ic_parser.add_argument('--output-dir', help='Output directory')
    
    # Boolean expression command
    bool_parser = subparsers.add_parser('boolean', help='Generate HDL from Boolean expression')
    bool_parser.add_argument('expression', help='Boolean expression (e.g., "A&B + !C")')
    bool_parser.add_argument('--name', help='Circuit name')
    bool_parser.add_argument('--technology', choices=['TTL', 'CMOS'], default='TTL',
                           help='Technology family')
    
    # Generate all ICs command
    all_parser = subparsers.add_parser('ic-all', help='Generate HDL for all ICs')
    all_parser.add_argument('--language', choices=['verilog', 'vhdl'], default='verilog',
                           help='HDL language')
    all_parser.add_argument('--testbenches', action='store_true',
                           help='Include testbenches')
    
    # Testbench command
    tb_parser = subparsers.add_parser('testbench', help='Generate testbench for IC')
    tb_parser.add_argument('part_number', help='IC part number')
    tb_parser.add_argument('--output-dir', help='Output directory')
    
    # Testbench all command
    subparsers.add_parser('testbench-all', help='Generate testbenches for all ICs')
    
    # List supported command
    subparsers.add_parser('list-supported', help='List all supported ICs')
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    generator = AdvancedHDLGenerator()
    
    # Route to appropriate function
    if args.command == 'ic':
        generator.generate_hdl(args.part_number, args.language, args.output_dir)
    
    elif args.command == 'boolean':
        generator.generate_from_boolean(args.expression, args.name)
    
    elif args.command == 'ic-all':
        generator.generate_all(args.language, args.testbenches)
    
    elif args.command == 'testbench':
        generator.generate_testbench(args.part_number, args.output_dir)
    
    elif args.command == 'testbench-all':
        print("Generating testbenches for all ICs...")
        success = 0
        total = len(generator.metadata)
        
        for ic in generator.metadata:
            if generator.generate_testbench(ic['part_number']):
                success += 1
        
        print(f"\nGenerated {success}/{total} testbenches")
    
    elif args.command == 'list-supported':
        generator.list_supported()

if __name__ == '__main__':
    main()
