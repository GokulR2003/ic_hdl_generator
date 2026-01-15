# cli_boolean.py
import argparse
from boolean_to_hdl import BooleanToHDLGenerator
import json

def main():
    parser = argparse.ArgumentParser(description="Generate HDL from Boolean expression")
    parser.add_argument("expression", help="Boolean expression (e.g., 'A&B + !C')")
    parser.add_argument("--name", help="Circuit name", default=None)
    parser.add_argument("--technology", choices=["TTL", "CMOS"], default="TTL")
    parser.add_argument("--no-optimize", action="store_true", help="Don't optimize with K-map")
    parser.add_argument("--output", choices=["verilog", "json", "all"], default="verilog")
    parser.add_argument("--output-dir", default="generated_boolean")
    
    args = parser.parse_args()
    
    # Create generator
    generator = BooleanToHDLGenerator(
        technology=args.technology,
        optimize=not args.no_optimize
    )
    
    # Generate HDL
    result = generator.generate(args.expression, args.name)
    
    # Save output
    import os
    os.makedirs(args.output_dir, exist_ok=True)
    
    if args.output in ["verilog", "all"]:
        # Save Verilog
        with open(f"{args.output_dir}/{result['circuit_name']}.v", "w") as f:
            f.write(result["hdl_code"])
        print(f"✓ Verilog saved: {args.output_dir}/{result['circuit_name']}.v")
        
        # Save testbench
        with open(f"{args.output_dir}/tb_{result['circuit_name']}.v", "w") as f:
            f.write(result["testbench"])
        print(f"✓ Testbench saved: {args.output_dir}/tb_{result['circuit_name']}.v")
    
    if args.output in ["json", "all"]:
        # Save full results as JSON
        with open(f"{args.output_dir}/{result['circuit_name']}_report.json", "w") as f:
            json.dump(result, f, indent=2)
        print(f"✓ JSON report saved: {args.output_dir}/{result['circuit_name']}_report.json")
    
    # Print summary
    print("\n" + "="*50)
    print("GENERATION SUMMARY")
    print("="*50)
    print(f"Circuit: {result['circuit_name']}")
    print(f"Original: {result['original_expression']}")
    print(f"Simplified: {result['simplified_expression']}")
    print(f"Variables: {', '.join(result['variables'])}")
    print(f"Minterms: {result['minterms']}")
    print(f"Gate counts: {result['gate_counts']}")
    print(f"Total ICs needed: {result['ic_mapping']['total_ics']}")
    print("="*50)

if __name__ == "__main__":
    main()
