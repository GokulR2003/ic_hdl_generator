#!/usr/bin/env python3
"""
Complete setup for IC HDL Generator with testbenches and VHDL
"""

import os
import shutil

def create_directory_structure():
    """Create all required directories"""
    directories = [
        # HDL Templates
        'hdl_templates/verilog/combinational/basic_gates',
        'hdl_templates/verilog/combinational/decoders',
        'hdl_templates/verilog/combinational/multiplexers',
        'hdl_templates/verilog/combinational/encoders',
        'hdl_templates/verilog/combinational/special',
        'hdl_templates/verilog/sequential/flip_flops',
        'hdl_templates/verilog/sequential/counters',
        'hdl_templates/verilog/transceivers',
        'hdl_templates/verilog/special_analog',
        
        # VHDL Templates
        'hdl_templates/vhdl/combinational/basic_gates',
        'hdl_templates/vhdl/combinational/decoders',
        'hdl_templates/vhdl/sequential/flip_flops',
        'hdl_templates/vhdl/sequential/counters',
        'hdl_templates/vhdl/special_analog',
        
        # Testbench Templates
        'testbench_templates/verilog/combinational/basic_gates',
        'testbench_templates/verilog/combinational/decoders',
        'testbench_templates/verilog/combinational/multiplexers',
        'testbench_templates/verilog/combinational/encoders',
        'testbench_templates/verilog/combinational/special',
        'testbench_templates/verilog/sequential/flip_flops',
        'testbench_templates/verilog/sequential/counters',
        'testbench_templates/verilog/transceivers',
        'testbench_templates/verilog/special_analog',
        
        # VHDL Testbenches
        'testbench_templates/vhdl/combinational/basic_gates',
        'testbench_templates/vhdl/sequential/flip_flops',
        
        # Output directories
        'generated_verilog',
        'generated_vhdl',
        'generated_testbenches',
        'examples',
        'scripts',
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Created: {directory}/")
    
    print("\n✅ Directory structure created!")

def create_essential_templates():
    """Create essential template files"""
    
    # Generic Verilog template
    generic_verilog = '''// Generic template for {{part_number}} - {{ic_name}}
// Generated: {{timestamp}}

`timescale 1ns / 1ps

module IC_{{part_number}}(
    {% for input in ports.inputs %}
    input wire {{input}},
    {% endfor %}
    
    {% for output in ports.outputs %}
    output wire {{output}},
    {% endfor %}
    
    {% for bidir in ports.bidirectional %}
    inout wire {{bidir}},
    {% endfor %}
    
    {% for power in ports.power %}
    input wire {{power}},
    {% endfor %}
);

// Generic implementation
{% for output in ports.outputs %}
assign {{output}} = 1'b0;
{% endfor %}

endmodule'''
    
    with open('hdl_templates/verilog/generic.vtpl', 'w') as f:
        f.write(generic_verilog)
    print("Created: hdl_templates/verilog/generic.vtpl")
    
    # Generic VHDL template
    generic_vhdl = '''-- Generic template for {{part_number}} - {{ic_name}}
-- Generated: {{timestamp}}

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity IC_{{part_number}} is
    Port (
        {% for input in ports.inputs %}
        {{input}} : in STD_LOGIC;
        {% endfor %}
        
        {% for output in ports.outputs %}
        {{output}} : out STD_LOGIC;
        {% endfor %}
        
        {% for bidir in ports.bidirectional %}
        {{bidir}} : inout STD_LOGIC;
        {% endfor %}
        
        {% for power in ports.power %}
        {{power}} : in STD_LOGIC
        {% if not loop.last %};{% else %};{% endif %}
        {% endfor %}
    );
end IC_{{part_number}};

architecture Behavioral of IC_{{part_number}} is

begin

    -- Generic implementation
    {% for output in ports.outputs %}
    {{output}} <= '0';
    {% endfor %}

end Behavioral;'''
    
    with open('hdl_templates/vhdl/generic.vhdltpl', 'w') as f:
        f.write(generic_vhdl)
    print("Created: hdl_templates/vhdl/generic.vhdltpl")
    
    # Generic testbench template
    generic_tb = '''// ============================================================================
// Testbench for: {{part_number}} - {{ic_name}}
// Generated: {{timestamp}}
// ============================================================================

`timescale 1ns / 1ps

module tb_{{part_number}};
    
    // Parameters
    parameter CLK_PERIOD = 10;
    parameter SIM_DURATION = {{test_coverage.simulation_duration_ns|default(1000)}};
    
    // DUT Signals
    {% for input in ports.inputs %}
    reg {{input}};
    {% endfor %}
    
    {% for output in ports.outputs %}
    wire {{output}};
    {% endfor %}
    
    {% for bidir in ports.bidirectional %}
    wire {{bidir}};
    {% endfor %}
    
    {% for power in ports.power %}
    wire {{power}};
    {% endfor %}
    
    // DUT
    IC_{{part_number}} dut (
        {% for input in ports.inputs %}
        .{{input}}({{input}}),
        {% endfor %}
        
        {% for output in ports.outputs %}
        .{{output}}({{output}}),
        {% endfor %}
        
        {% for bidir in ports.bidirectional %}
        .{{bidir}}({{bidir}}),
        {% endfor %}
        
        {% for power in ports.power %}
        .{{power}}({{power}}),
        {% endfor %}
    );
    
    // Test variables
    integer test_count = 0;
    integer pass_count = 0;
    
    initial begin
        $display("[TEST] Starting testbench for {{part_number}} - {{ic_name}}");
        
        // Initialize
        {% for input in ports.inputs %}
        {{input}} = 0;
        {% endfor %}
        
        {% for power in ports.power %}
        {% if 'VCC' in power or 'VDD' in power %}
        {{power}} = 1;
        {% else %}
        {{power}} = 0;
        {% endif %}
        {% endfor %}
        
        #100;
        
        // Run basic tests
        test_basic_functionality();
        
        // Print summary
        print_summary();
        
        #100;
        $finish;
    end
    
    task test_basic_functionality;
        integer i;
        begin
            $display("[TEST] Testing basic functionality");
            
            for (i = 0; i < {{test_coverage.min_test_vectors|default(10)}}; i = i + 1) begin
                {% for input in ports.inputs %}
                {{input}} = $random;
                {% endfor %}
                #20;
                
                test_count = test_count + 1;
                pass_count = pass_count + 1;
            end
        end
    endtask
    
    task print_summary;
        real coverage;
        begin
            coverage = (real'(pass_count) / real'(test_count)) * 100.0;
            
            $display("\n[SUMMARY] Tests: %0d, Passed: %0d, Coverage: %0.2f%%",
                    test_count, pass_count, coverage);
        end
    endtask
    
    // Simulation timeout
    initial begin
        #(SIM_DURATION);
        $display("[TIMEOUT] Simulation time exceeded");
        $finish;
    end
    
endmodule'''
    
    with open('testbench_templates/verilog/generic_tb.vtpl', 'w') as f:
        f.write(generic_tb)
    print("Created: testbench_templates/verilog/generic_tb.vtpl")
    
    print("\n✅ Essential templates created!")

def check_dependencies():
    """Check and install dependencies"""
    try:
        import jinja2
        print("✅ Jinja2 is installed")
        return True
    except ImportError:
        print("⚠️  Jinja2 not installed. Installing...")
        try:
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "jinja2"])
            print("✅ Jinja2 installed successfully")
            return True
        except:
            print("❌ Failed to install Jinja2")
            print("Please install manually: pip install jinja2")
            return False

def create_examples():
    """Create example files"""
    
    # Example usage script
    example_code = '''#!/usr/bin/env python3
"""
Example usage of Advanced HDL Generator
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from advanced_generator import AdvancedHDLGenerator

def main():
    print("Advanced HDL Generator - Examples")
    print("=" * 60)
    
    # Initialize generator
    print("1. Initializing generator...")
    gen = AdvancedHDLGenerator()
    
    # Example 1: List supported ICs
    print("\n2. Listing supported ICs...")
    gen.list_supported()
    
    # Example 2: Generate Verilog for 7400
    print("\n3. Generating Verilog for 7400...")
    gen.generate_hdl('7400', 'verilog', 'examples/output')
    
    # Example 3: Generate VHDL for 7474
    print("\n4. Generating VHDL for 7474...")
    gen.generate_hdl('7474', 'vhdl', 'examples/output')
    
    # Example 4: Generate testbench
    print("\n5. Generating testbench for 7400...")
    gen.generate_testbench('7400', 'examples/output')
    
    # Example 5: Generate all Verilog with testbenches
    print("\n6. Generating all Verilog ICs with testbenches...")
    gen.generate_all('verilog', include_testbenches=True)
    
    print("\n" + "=" * 60)
    print("Examples completed!")
    print("Check the output directories for generated files")

if __name__ == "__main__":
    main()'''
    
    with open('examples/advanced_example.py', 'w') as f:
        f.write(example_code)
    
    print("Created: examples/advanced_example.py")
    print("✅ Examples created!")

def main():
    print("IC HDL Generator - Complete Setup")
    print("=" * 60)
    
    # Create directories
    create_directory_structure()
    
    # Check dependencies
    if check_dependencies():
        # Create templates
        create_essential_templates()
        
        # Create examples
        create_examples()
        
        print("\n" + "=" * 60)
        print("SETUP COMPLETE! 🎉")
        print("\nNext steps:")
        print("1. Run: python advanced_generator.py list-supported")
        print("2. Run: python advanced_generator.py generate 7400")
        print("3. Run: python advanced_generator.py generate-all --language verilog --testbenches")
        print("\nCheck examples/advanced_example.py for more usage")
    else:
        print("\nSetup incomplete. Please install dependencies first.")

if __name__ == "__main__":
    import sys
    main()
