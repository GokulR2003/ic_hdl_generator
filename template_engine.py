#!/usr/bin/env python3
"""
HDL Template Engine for IC Metadata
Generates Verilog/VHDL code from IC metadata using Jinja2 templates
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
import argparse

try:
    from jinja2 import Environment, FileSystemLoader, TemplateNotFound
    JINJA2_AVAILABLE = True
except ImportError:
    JINJA2_AVAILABLE = False
    print("Error: Jinja2 is required. Install with: pip install jinja2")
    sys.exit(1)


class HDLGenerator:
    """Generate HDL code from IC metadata using templates"""
    
    def __init__(self, metadata_file, template_dir):
        """
        Initialize HDL Generator
        
        Args:
            metadata_file: Path to JSON metadata file
            template_dir: Base directory containing templates
        """
        self.metadata_file = metadata_file
        self.template_dir = Path(template_dir)
        self.metadata = self._load_metadata()
        
        # Setup Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(self.template_dir),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Add custom filters
        self.env.filters['range'] = lambda start, end: range(start, end)
        self.env.filters['join'] = lambda items, sep=', ': sep.join(map(str, items))
        
        # Add global functions
        self.env.globals['now'] = datetime.now
        self.env.globals['len'] = len
        
    def _load_metadata(self):
        """Load IC metadata from JSON file"""
        try:
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: Metadata file not found: {self.metadata_file}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in metadata file: {e}")
            sys.exit(1)
    
    def find_ic(self, part_number):
        """Find IC data by part number"""
        for ic in self.metadata:
            if ic['part_number'] == part_number:
                return ic
        return None
    
    def get_template_path(self, ic_data, language):
        """
        Determine template path based on IC data
        
        Args:
            ic_data: IC metadata dictionary
            language: 'verilog' or 'vhdl'
        
        Returns:
            Path to template file
        """
        # Get template name from metadata or use subtype
        template_name = ic_data.get('template', ic_data.get('subtype', 'generic'))
        
        # Determine category directory
        category = ic_data.get('category', 'combinational')
        
        # Map categories to directories
        category_map = {
            'combinational': 'combinational',
            'sequential': 'sequential',
            'counter': 'sequential/counters',
            'special': 'special_analog'
        }
        
        # Get template directory
        if language == 'verilog':
            base_dir = 'verilog'
            ext = '.vtpl'
        elif language == 'vhdl':
            base_dir = 'vhdl'
            ext = '.vhdltpl'
        else:
            raise ValueError(f"Unsupported language: {language}")
        
        # Try specific template first, then generic
        category_dir = category_map.get(category, 'combinational')
        
        # Build possible template paths
        possible_paths = [
            f"{base_dir}/{category_dir}/{template_name}{ext}",
            f"{base_dir}/{category_dir}/generic{ext}",
            f"{base_dir}/generic{ext}"
        ]
        
        # Find existing template
        for path in possible_paths:
            full_path = self.template_dir / path
            if full_path.exists():
                return str(path)
        
        raise TemplateNotFound(f"No template found for {template_name} in {language}")
    
    def generate_hdl(self, part_number, language='verilog', output_dir=None):
        """
        Generate HDL for a specific IC
        
        Args:
            part_number: IC part number (e.g., '7400')
            language: 'verilog' or 'vhdl'
            output_dir: Directory to save generated file
        
        Returns:
            Generated HDL code as string
        """
        # Find IC data
        ic_data = self.find_ic(part_number)
        if not ic_data:
            raise ValueError(f"IC {part_number} not found in metadata")
        
        # Get template
        template_path = self.get_template_path(ic_data, language)
        template = self.env.get_template(template_path)
        
        # Add generation timestamp
        ic_data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Add default values for optional fields
        ic_data.setdefault('template_variables', {})
        ic_data.setdefault('parameters', {})
        ic_data.setdefault('ports', {})
        ic_data['ports'].setdefault('inputs', [])
        ic_data['ports'].setdefault('outputs', [])
        ic_data['ports'].setdefault('bidirectional', [])
        ic_data['ports'].setdefault('power', ['VCC', 'GND'])
        
        # Generate HDL
        hdl_code = template.render(**ic_data)
        
        # Save to file if output_dir specified
        if output_dir:
            self._save_hdl_file(hdl_code, ic_data, language, output_dir)
        
        return hdl_code
    
    def _save_hdl_file(self, hdl_code, ic_data, language, output_dir):
        """Save generated HDL to file"""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Determine filename
        part_number = ic_data['part_number']
        if language == 'verilog':
            filename = f"IC_{part_number}.v"
        else:  # VHDL
            filename = f"IC_{part_number}.vhd"
        
        filepath = output_dir / filename
        
        # Write file
        with open(filepath, 'w') as f:
            f.write(hdl_code)
        
        print(f"Generated: {filepath}")
    
    def generate_all(self, language='verilog', output_dir=None):
        """
        Generate HDL for all ICs in metadata
        
        Args:
            language: 'verilog' or 'vhdl'
            output_dir: Base directory for output files
        """
        if output_dir is None:
            output_dir = f"generated_{language}"
        
        success_count = 0
        error_count = 0
        
        print(f"\n{'='*60}")
        print(f"Generating {language.upper()} for all ICs")
        print(f"{'='*60}")
        
        for ic in self.metadata:
            part_number = ic['part_number']
            ic_name = ic['ic_name']
            
            try:
                self.generate_hdl(part_number, language, output_dir)
                print(f"✓ {part_number}: {ic_name}")
                success_count += 1
            except TemplateNotFound as e:
                print(f"✗ {part_number}: Template not found - {e}")
                error_count += 1
            except Exception as e:
                print(f"✗ {part_number}: Error - {e}")
                error_count += 1
        
        print(f"\n{'='*60}")
        print(f"Summary: {success_count} succeeded, {error_count} failed")
        print(f"{'='*60}")
    
    def generate_testbench(self, part_number, language='verilog', output_dir=None):
        """
        Generate testbench for a specific IC
        
        Args:
            part_number: IC part number
            language: 'verilog' or 'vhdl'
            output_dir: Directory to save testbench
        """
        # Find IC data
        ic_data = self.find_ic(part_number)
        if not ic_data:
            raise ValueError(f"IC {part_number} not found")
        
        # Load testbench template
        if language == 'verilog':
            template_path = "testbench_templates/verilog/generic_tb.vtpl"
            ext = "_tb.v"
        else:
            template_path = "testbench_templates/vhdl/generic_tb.vhdltpl"
            ext = "_tb.vhd"
        
        try:
            template = self.env.get_template(template_path)
        except TemplateNotFound:
            print(f"Warning: No testbench template found for {language}")
            return
        
        # Add test coverage information
        ic_data['test_coverage'] = ic_data.get('test_coverage', {})
        ic_data['test_coverage'].setdefault('min_test_vectors', 10)
        ic_data['test_coverage'].setdefault('required_test_cases', [])
        
        # Generate testbench
        tb_code = template.render(**ic_data)
        
        # Save to file
        if output_dir:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            filename = f"IC_{part_number}{ext}"
            filepath = output_dir / filename
            
            with open(filepath, 'w') as f:
                f.write(tb_code)
            
            print(f"Generated testbench: {filepath}")
        
        return tb_code


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(
        description="Generate HDL code from IC metadata",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s generate 7400 --language verilog
  %(prog)s generate-all --language vhdl
  %(prog)s testbench 7400 --output-dir testbenches/
        """
    )
    
    parser.add_argument(
        'command',
        choices=['generate', 'generate-all', 'testbench', 'list'],
        help='Command to execute'
    )
    
    parser.add_argument(
        'part_number',
        nargs='?',
        help='IC part number (e.g., 7400, 7474)'
    )
    
    parser.add_argument(
        '--metadata',
        default='Ic_Metadata_Master.json',
        help='Path to metadata JSON file (default: Ic_Metadata_Master.json)'
    )
    
    parser.add_argument(
        '--template-dir',
        default='hdl_templates',
        help='Base directory containing templates (default: hdl_templates)'
    )
    
    parser.add_argument(
        '--language',
        choices=['verilog', 'vhdl'],
        default='verilog',
        help='HDL language to generate (default: verilog)'
    )
    
    parser.add_argument(
        '--output-dir',
        help='Directory to save generated files'
    )
    
    parser.add_argument(
        '--list-templates',
        action='store_true',
        help='List available templates'
    )
    
    args = parser.parse_args()
    
    # Check if Jinja2 is available
    if not JINJA2_AVAILABLE:
        print("Error: Jinja2 is required. Install with: pip install jinja2")
        sys.exit(1)
    
    # Initialize generator
    try:
        generator = HDLGenerator(args.metadata, args.template_dir)
    except Exception as e:
        print(f"Error initializing generator: {e}")
        sys.exit(1)
    
    # Execute command
    if args.command == 'generate':
        if not args.part_number:
            print("Error: Part number required for generate command")
            sys.exit(1)
        
        try:
            code = generator.generate_hdl(
                args.part_number,
                args.language,
                args.output_dir
            )
            
            if not args.output_dir:
                print(code)
        
        except Exception as e:
            print(f"Error generating HDL for {args.part_number}: {e}")
            sys.exit(1)
    
    elif args.command == 'generate-all':
        generator.generate_all(args.language, args.output_dir)
    
    elif args.command == 'testbench':
        if not args.part_number:
            print("Error: Part number required for testbench command")
            sys.exit(1)
        
        try:
            generator.generate_testbench(
                args.part_number,
                args.language,
                args.output_dir
            )
        except Exception as e:
            print(f"Error generating testbench: {e}")
            sys.exit(1)
    
    elif args.command == 'list':
        # List all ICs in metadata
        print("\nAvailable ICs in metadata:")
        print("-" * 40)
        for ic in generator.metadata:
            print(f"{ic['part_number']:10} - {ic['ic_name']}")
        
        print(f"\nTotal: {len(generator.metadata)} ICs")
    
    if args.list_templates:
        # List available templates
        print("\nAvailable templates:")
        print("-" * 40)
        
        template_files = []
        for root, dirs, files in os.walk(args.template_dir):
            for file in files:
                if file.endswith(('.vtpl', '.vhdltpl')):
                    rel_path = os.path.relpath(os.path.join(root, file), args.template_dir)
                    template_files.append(rel_path)
        
        for template in sorted(template_files):
            print(template)


if __name__ == "__main__":
    main()
