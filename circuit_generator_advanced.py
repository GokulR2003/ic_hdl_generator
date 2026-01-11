#!/usr/bin/env python3
"""
Advanced Circuit Generator
Generate complex circuits by composing individual ICs
"""

import os
import json
import argparse
from jinja2 import Environment, FileSystemLoader

# Circuit configurations
CIRCUIT_CONFIGS = {
    "full_adder_1bit": {
        "name": "1-bit binary full adder",
        "description": "Adds three 1-bit inputs (A, B, Cin) to produce Sum and Cout",
        "ics": ["7486", "7408", "7432"],
        "inputs": ["A", "B", "Cin"],
        "outputs": ["Sum", "Cout"],
        "connections": {
            "7486": [{"instance": "xor1", "inputs": ["A", "B"], "output": "xor_ab"}],
            "7408": [{"instance": "and1", "inputs": ["A", "B"], "output": "and_ab"}],
            "7486": [{"instance": "xor2", "inputs": ["xor_ab", "Cin"], "output": "Sum"}],
            "7408": [{"instance": "and2", "inputs": ["Cin", "xor_ab"], "output": "and_cin_xor"}],
            "7432": [{"instance": "or1", "inputs": ["and_ab", "and_cin_xor"], "output": "Cout"}]
        }
    },
    "half_adder_1bit": {
        "name": "1-bit binary half adder",
        "description": "Adds two 1-bit inputs (A, B) to produce Sum and Carry",
        "ics": ["7486", "7408"],
        "inputs": ["A", "B"],
        "outputs": ["Sum", "Carry"],
        "connections": {
            "7486": [{"instance": "xor1", "inputs": ["A", "B"], "output": "Sum"}],
            "7408": [{"instance": "and1", "inputs": ["A", "B"], "output": "Carry"}]
        }
    },
    "2bit_adder": {
        "name": "2-bit binary adder",
        "description": "Adds two 2-bit numbers with carry in/out",
        "ics": ["full_adder_1bit", "full_adder_1bit"],
        "inputs": ["A[1:0]", "B[1:0]", "Cin"],
        "outputs": ["Sum[1:0]", "Cout"],
        "connections": {
            "full_adder_1bit": [
                {"instance": "fa0", "inputs": ["A[0]", "B[0]", "Cin"], "outputs": ["Sum[0]", "carry0"]},
                {"instance": "fa1", "inputs": ["A[1]", "B[1]", "carry0"], "outputs": ["Sum[1]", "Cout"]}
            ]
        }
    },
    "4bit_adder": {
        "name": "4-bit binary adder",
        "description": "Adds two 4-bit numbers with carry ripple",
        "ics": ["full_adder_1bit", "full_adder_1bit", "full_adder_1bit", "full_adder_1bit"],
        "inputs": ["A[3:0]", "B[3:0]", "Cin"],
        "outputs": ["Sum[3:0]", "Cout"],
        "connections": {
            "full_adder_1bit": [
                {"instance": "fa0", "inputs": ["A[0]", "B[0]", "Cin"], "outputs": ["Sum[0]", "c0"]},
                {"instance": "fa1", "inputs": ["A[1]", "B[1]", "c0"], "outputs": ["Sum[1]", "c1"]},
                {"instance": "fa2", "inputs": ["A[2]", "B[2]", "c1"], "outputs": ["Sum[2]", "c2"]},
                {"instance": "fa3", "inputs": ["A[3]", "B[3]", "c2"], "outputs": ["Sum[3]", "Cout"]}
            ]
        }
    },
    "alu_1bit": {
        "name": "1-bit ALU",
        "description": "1-bit Arithmetic Logic Unit with basic operations",
        "ics": ["7486", "7408", "7432", "7404", "74153"],
        "inputs": ["A", "B", "Op[1:0]", "Cin"],
        "outputs": ["Result", "Cout"],
        "connections": {
            "7486": [{"instance": "xor1", "inputs": ["A", "B"], "output": "xor_out"}],
            "7408": [{"instance": "and1", "inputs": ["A", "B"], "output": "and_out"}],
            "7432": [{"instance": "or1", "inputs": ["A", "B"], "output": "or_out"}],
            "full_adder_1bit": [{"instance": "fa1", "inputs": ["A", "B", "Cin"], "outputs": ["fa_sum", "fa_cout"]}],
            "74153": [{"instance": "mux1", "inputs": ["and_out", "or_out", "xor_out", "fa_sum"], "select": "Op[1:0]", "output": "Result"}]
        }
    }
}

# IC Database - This should match what's in advanced_generator.py
IC_DATABASE = [
    {"part": "7400", "name": "7400 Quad 2-Input NAND", "type": "basic_gate", "template": "verilog/combinational/basic_gates/nand_quad.vtpl"},
    {"part": "7402", "name": "7402 Quad 2-Input NOR", "type": "basic_gate", "template": "verilog/combinational/basic_gates/nor_quad.vtpl"},
    {"part": "7404", "name": "7404 Hex Inverter", "type": "basic_gate", "template": "verilog/combinational/basic_gates/inverter_hex.vtpl"},
    {"part": "7408", "name": "7408 Quad 2-Input AND", "type": "basic_gate", "template": "verilog/combinational/basic_gates/and_quad.vtpl"},
    {"part": "7432", "name": "7432 Quad 2-Input OR", "type": "basic_gate", "template": "verilog/combinational/basic_gates/or_quad.vtpl"},
    {"part": "7486", "name": "7486 Quad 2-Input XOR", "type": "basic_gate", "template": "verilog/combinational/basic_gates/xor_quad.vtpl"},
    {"part": "74138", "name": "74138 3-to-8 Line Decoder/Demultiplexer", "type": "decoder", "template": "verilog/combinational/decoders/decoder_3to8.vtpl"},
    {"part": "74153", "name": "74153 Dual 4:1 Multiplexer", "type": "mux", "template": "verilog/combinational/multiplexers/mux_4to1_dual.vtpl"},
    {"part": "7474", "name": "7474 Dual D-Type Flip-Flop (Preset/Clear)", "type": "flip_flop", "template": "verilog/sequential/flip_flops/d_ff_dual_async.vtpl"},
    {"part": "7490", "name": "7490 Decade Counter", "type": "counter", "template": "verilog/sequential/counters/counter_decade_7490.vtpl"},
    {"part": "7493", "name": "7493 4-bit Binary Counter", "type": "counter", "template": "verilog/sequential/counters/counter_4bit_binary_7493.vtpl"},
    {"part": "74245", "name": "74245 Octal Bus Transceiver", "type": "transceiver", "template": "verilog/transceivers/transceiver_8bit.vtpl"},
    {"part": "7447", "name": "7447 BCD to 7-Segment Decoder/Driver", "type": "special", "template": "verilog/combinational/special/decoder_bcd_7seg.vtpl"},
    {"part": "7485", "name": "7485 4-bit Magnitude Comparator", "type": "comparator", "template": "verilog/combinational/special/comparator_4bit.vtpl"},
    {"part": "74121", "name": "74121 Monostable Multivibrator", "type": "special", "template": "verilog/special_analog/monostable_74121.vtpl"},
    {"part": "555", "name": "NE555 Timer IC", "type": "timer", "template": "verilog/special_analog/timer_555_behavioral.vtpl"},
    {"part": "4017", "name": "CD4017 Decade Counter/Johnson Counter", "type": "counter", "template": "verilog/sequential/counters/counter_decade_4017.vtpl"}
]

def convert_ic_list_to_dict(ic_list):
    """Convert IC list to dictionary for easy lookup"""
    ic_dict = {}
    for ic in ic_list:
        part_num = ic.get('part')
        if part_num:
            ic_dict[part_num] = ic
    return ic_dict

def load_ic_modules(generated_dir="generated_verilog"):
    """Load generated IC modules from files"""
    ic_modules = {}
    
    if not os.path.exists(generated_dir):
        print(f"⚠️ Warning: Directory {generated_dir} not found")
        return ic_dict
    
    for filename in os.listdir(generated_dir):
        if filename.startswith("IC_") and filename.endswith(".v"):
            part_num = filename[3:-2]  # Remove "IC_" and ".v"
            filepath = os.path.join(generated_dir, filename)
            
            try:
                with open(filepath, 'r') as f:
                    content = f.read()
                    ic_modules[part_num] = {
                        'part': part_num,
                        'name': f"IC_{part_num}",
                        'content': content,
                        'filename': filename
                    }
            except Exception as e:
                print(f"⚠️ Error loading {filename}: {e}")
    
    return ic_modules

def generate_circuit_from_ics(circuit_name, ics_config, ic_db, language="verilog"):
    """Generate a complex circuit from individual ICs"""
    
    # Make sure ic_db is a dictionary
    if isinstance(ic_db, list):
        ic_db = convert_ic_list_to_dict(ic_db)
    
    # Get circuit configuration
    circuit_config = CIRCUIT_CONFIGS.get(circuit_name)
    if not circuit_config:
        raise ValueError(f"Unknown circuit: {circuit_name}")
    
    print(f"\nGenerating: {circuit_name} - {circuit_config['name']}")
    print(f"  ICs needed: {circuit_config['ics']}")
    
    # Create Jinja2 environment
    template_dir = os.path.join(os.path.dirname(__file__), "templates")
    if not os.path.exists(template_dir):
        os.makedirs(template_dir, exist_ok=True)
    
    env = Environment(loader=FileSystemLoader(template_dir))
    
    # Check if we have templates for all needed ICs
    missing_ics = []
    for ic_part in circuit_config['ics']:
        if ic_part not in ic_db and ic_part not in CIRCUIT_CONFIGS:
            missing_ics.append(ic_part)
    
    if missing_ics:
        print(f"  ⚠️ Warning: Missing templates for ICs: {missing_ics}")
        print(f"  Using generic templates for missing ICs")
    
    # Generate the circuit
    return _create_circuit_module(circuit_name, circuit_config, ic_db, env)

def _create_circuit_module(circuit_name, circuit_config, ic_db, template_env):
    """Create the actual circuit module"""
    
    # Prepare data for template
    template_data = {
        'circuit_name': circuit_name,
        'config': circuit_config,
        'instances': [],
        'wires': set(),
        'ic_db': ic_db
    }
    
    # Process each IC instance
    ic_counters = {}
    
    for ic_part in circuit_config['ics']:
        # Get IC type (how many of this part)
        if ic_part not in ic_counters:
            ic_counters[ic_part] = 1
        else:
            ic_counters[ic_part] += 1
        
        instance_name = f"{ic_part.lower()}_{ic_counters[ic_part]}"
        
        # Get IC data
        ic_data = ic_db.get(ic_part, {})
        
        # For hierarchical circuits (circuits made of other circuits)
        if ic_part in CIRCUIT_CONFIGS:
            ic_type = "circuit"
            ic_module_name = ic_part
        else:
            ic_type = "ic"
            ic_module_name = f"IC_{ic_part}"
        
        # Create instance data
        instance_data = {
            'part': ic_part,
            'instance_name': instance_name,
            'module_name': ic_module_name,
            'type': ic_type,
            'data': ic_data
        }
        
        # Add connections based on circuit config
        if 'connections' in circuit_config and ic_part in circuit_config['connections']:
            instance_data['connections'] = circuit_config['connections'][ic_part]
        
        template_data['instances'].append(instance_data)
    
    # Try to load circuit template, fall back to generic
    try:
        template = template_env.get_template("circuit.vtpl")
    except:
        # Create a simple generic template in code
        verilog_code = _generate_generic_circuit(template_data)
    else:
        verilog_code = template.render(**template_data)
    
    # Generate testbench
    testbench_code = _generate_testbench(circuit_name, circuit_config)
    
    return verilog_code, testbench_code

def _generate_generic_circuit(template_data):
    """Generate generic circuit code when no template is available"""
    
    circuit_name = template_data['circuit_name']
    config = template_data['config']
    
    code = f"""
// {config['name']}
// {config['description']}
// Generated automatically from ICs: {', '.join(config['ics'])}

module {circuit_name}(
    input {', '.join(config['inputs'])},
    output {', '.join(config['outputs'])}
);
"""
    
    # Add wire declarations
    wires = set()
    for instance in template_data['instances']:
        if 'connections' in instance:
            for conn in instance['connections']:
                if 'output' in conn and isinstance(conn['output'], str):
                    wires.add(conn['output'])
                elif 'outputs' in conn:
                    for out in conn['outputs']:
                        if isinstance(out, str):
                            wires.add(out)
    
    if wires:
        code += "\n    // Internal wires\n"
        for wire in sorted(wires):
            code += f"    wire {wire};\n"
    
    # Add instances
    code += "\n    // IC instances\n"
    for instance in template_data['instances']:
        ic_part = instance['part']
        instance_name = instance['instance_name']
        
        if ic_part in CIRCUIT_CONFIGS:
            # This is a hierarchical circuit
            module_name = ic_part
            code += f"    {module_name} {instance_name} (\n"
            
            # Add connections (simplified)
            if 'connections' in instance and instance['connections']:
                conn = instance['connections'][0]  # Take first connection
                if 'inputs' in conn:
                    for i, inp in enumerate(conn['inputs']):
                        code += f"        .{chr(65+i)}({inp}),\n"
                if 'outputs' in conn:
                    for i, out in enumerate(conn['outputs']):
                        code += f"        .{chr(83+i)}({out}){')\n' if i == len(conn['outputs'])-1 else ','}\n"
        else:
            # This is a basic IC
            module_name = f"IC_{ic_part}"
            code += f"    {module_name} {instance_name} (\n"
            
            # Simplified port connections
            if 'connections' in instance and instance['connections']:
                conn = instance['connections'][0]
                if 'inputs' in conn and 'output' in conn:
                    code += f"        .A({conn['inputs'][0]}),\n"
                    code += f"        .B({conn['inputs'][1] if len(conn['inputs']) > 1 else '1\'b0'}),\n"
                    code += f"        .Y({conn['output']})\n"
                    code += "    );\n"
    
    code += "\nendmodule\n"
    
    return code

def _generate_testbench(circuit_name, circuit_config):
    """Generate a testbench for the circuit"""
    
    tb_code = f"""
`timescale 1ns/1ps

module tb_{circuit_name};
    // Inputs
    reg {', '.join(circuit_config['inputs'])};
    
    // Outputs
    wire {', '.join(circuit_config['outputs'])};
    
    // Instantiate the circuit
    {circuit_name} dut (
        {', '.join(['.' + inp + '(' + inp + ')' for inp in circuit_config['inputs']])},
        {', '.join(['.' + outp + '(' + outp + ')' for outp in circuit_config['outputs']])}
    );
    
    initial begin
        $display("Testing: {circuit_config['name']}");
        $display("{{'>'}} {{'<' * 40}}");
        $display("Inputs: {', '.join(circuit_config['inputs'])}");
        $display("Outputs: {', '.join(circuit_config['outputs'])}");
        $display("");
        
        // Add test cases here
        
        $display("{{'>'}} {{'<' * 40}}");
        $display("Test complete!");
        $finish;
    end
    
    // Generate waveform dump
    initial begin
        $dumpfile("{circuit_name}.vcd");
        $dumpvars(0, tb_{circuit_name});
    end
    
endmodule
"""
    
    return tb_code

def save_circuit_files(circuit_name, verilog_code, testbench_code, output_dir="generated_circuits"):
    """Save generated circuit files"""
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Save main module
    verilog_file = os.path.join(output_dir, f"{circuit_name}.v")
    with open(verilog_file, "w") as f:
        f.write(verilog_code)
    print(f"  ✓ Saved: {verilog_file}")
    
    # Save testbench
    tb_file = os.path.join(output_dir, f"tb_{circuit_name}.v")
    with open(tb_file, "w") as f:
        f.write(testbench_code)
    print(f"  ✓ Saved: {tb_file}")
    
    return verilog_file, tb_file

def list_supported_circuits():
    """List all supported circuits"""
    print("\n=== Supported Advanced Circuits ===")
    print("=" * 40)
    
    for circuit_name, config in CIRCUIT_CONFIGS.items():
        print(f"\n{circuit_name}:")
        print(f"  Name: {config['name']}")
        print(f"  Description: {config['description']}")
        print(f"  ICs required: {', '.join(config['ics'])}")
        print(f"  Inputs: {', '.join(config['inputs'])}")
        print(f"  Outputs: {', '.join(config['outputs'])}")

def generate_all_circuits(ic_db=None, output_dir="generated_circuits"):
    """Generate all supported circuits"""
    
    if ic_db is None:
        ic_db = convert_ic_list_to_dict(IC_DATABASE)
    
    print("\n=== Generating All Advanced Circuits ===")
    print("=" * 50)
    
    generated = []
    
    for circuit_name in CIRCUIT_CONFIGS.keys():
        try:
            verilog_code, testbench_code = generate_circuit_from_ics(
                circuit_name, 
                CIRCUIT_CONFIGS[circuit_name], 
                ic_db
            )
            
            save_circuit_files(circuit_name, verilog_code, testbench_code, output_dir)
            generated.append(circuit_name)
            
        except Exception as e:
            print(f"\n❌ Error generating {circuit_name}: {e}")
    
    print(f"\n✅ Generated {len(generated)} circuits")
    return generated

def main():
    parser = argparse.ArgumentParser(description="Generate complex circuits from ICs")
    parser.add_argument("action", choices=["generate", "list", "generate-all"],
                       help="Action to perform")
    parser.add_argument("circuit_name", nargs="?", 
                       help="Name of circuit to generate (for 'generate' action)")
    parser.add_argument("--output-dir", default="generated_circuits",
                       help="Output directory for generated circuits")
    
    args = parser.parse_args()
    
    # Convert IC database to dictionary
    ic_db = convert_ic_list_to_dict(IC_DATABASE)
    
    if args.action == "list":
        list_supported_circuits()
    
    elif args.action == "generate":
        if not args.circuit_name:
            print("Error: circuit_name is required for 'generate' action")
            parser.print_help()
            return
        
        if args.circuit_name not in CIRCUIT_CONFIGS:
            print(f"Error: Unknown circuit '{args.circuit_name}'")
            print("\nAvailable circuits:")
            for name in CIRCUIT_CONFIGS.keys():
                print(f"  - {name}")
            return
        
        try:
            verilog_code, testbench_code = generate_circuit_from_ics(
                args.circuit_name, 
                CIRCUIT_CONFIGS[args.circuit_name], 
                ic_db
            )
            
            save_circuit_files(args.circuit_name, verilog_code, testbench_code, args.output_dir)
            print(f"\n✅ Successfully generated {args.circuit_name}")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
    
    elif args.action == "generate-all":
        generate_all_circuits(ic_db, args.output_dir)

if __name__ == "__main__":
    main()
