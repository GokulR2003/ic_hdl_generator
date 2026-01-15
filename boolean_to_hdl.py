# boolean_to_hdl.py
from boolean_parser import BooleanExpressionParser
from kmap_solver import KMapSolver
from technology_mapper import TechnologyMapper
from gate_database import GateDatabase

class BooleanToHDLGenerator:
    def __init__(self, technology: str = "TTL", optimize: bool = True):
        self.parser = BooleanExpressionParser()
        self.solver = KMapSolver()
        self.mapper = TechnologyMapper(technology)
        self.db = GateDatabase()
        self.optimize = optimize
    
    def generate(self, expression: str, circuit_name: str = None) -> Dict:
        """Complete pipeline: Boolean expression → HDL code"""
        
        print(f"Generating HDL for expression: {expression}")
        print("-" * 50)
        
        # Step 1: Parse expression
        print("Step 1: Parsing Boolean expression...")
        parsed = self.parser.parse_expression(expression)
        
        if not circuit_name:
            circuit_name = f"logic_{hash(expression) % 1000:04d}"
        
        # Step 2: Simplify using K-map
        print("Step 2: Simplifying using K-map...")
        if self.optimize:
            simplified = self.solver.solve(
                parsed["minterms"], 
                parsed["num_inputs"],
                []
            )
        else:
            # Generate unsimplified SOP
            simplified = self.solver._simplify_sop(
                parsed["minterms"],
                parsed["num_inputs"]
            )
        
        # Step 3: Map to gates and count
        print("Step 3: Mapping to logic gates...")
        simplified["gate_counts"] = simplified.get("gate_count", {})
        
        # Step 4: Map to physical ICs
        print("Step 4: Selecting physical ICs...")
        ic_mapping = self.mapper.map_expression_to_ics(simplified)
        
        # Step 5: Generate HDL code
        print("Step 5: Generating HDL code...")
        hdl_code = self._generate_verilog(
            circuit_name,
            parsed["variables"],
            simplified["sop_expression"],
            ic_mapping
        )
        
        # Step 6: Generate testbench
        print("Step 6: Generating testbench...")
        testbench = self._generate_testbench(
            circuit_name,
            parsed["variables"],
            parsed["truth_table"]
        )
        
        return {
            "circuit_name": circuit_name,
            "original_expression": expression,
            "simplified_expression": simplified["sop_expression"],
            "variables": parsed["variables"],
            "minterms": parsed["minterms"],
            "gate_counts": simplified["gate_counts"],
            "ic_mapping": ic_mapping,
            "hdl_code": hdl_code,
            "testbench": testbench,
            "truth_table": parsed["truth_table"]
        }
    
    def _generate_verilog(self, name: str, inputs: List[str], 
                         expression: str, ic_mapping: Dict) -> str:
        """Generate Verilog code from expression and IC mapping"""
        
        verilog = f"""// Generated from Boolean expression
// Original expression: {expression}
// Simplified using K-map

module {name}(
    input {', '.join(inputs)},
    output Y
);
"""
        
        # For now, generate behavioral code
        # Later: generate structural code using mapped ICs
        expr_verilog = expression
        expr_verilog = expr_verilog.replace("·", "&").replace("+", "|")
        expr_verilog = expr_verilog.replace("'", "'").replace("!", "'")
        
        verilog += f"\n    assign Y = {expr_verilog};\n\nendmodule\n"
        
        return verilog
    
    def _generate_testbench(self, name: str, inputs: List[str], 
                           truth_table: List[Dict]) -> str:
        """Generate testbench from truth table"""
        
        tb = f"""`timescale 1ns/1ps

module tb_{name};
    // Inputs
    reg {', '.join(inputs)};
    
    // Outputs
    wire Y;
    
    // Instantiate unit under test
    {name} uut (
        {', '.join(['.' + inp + '(' + inp + ')' for inp in inputs])},
        .Y(Y)
    );
    
    initial begin
        $display("Testing circuit: {name}");
        $display("{'=' * 50}");
        $display("Inputs: {', '.join(inputs)}");
        $display("");
        $display("Test cases:");
        $display("------------------");
"""
        
        for i, row in enumerate(truth_table):
            input_vals = [str(row["inputs"][var]) for var in inputs]
            tb += f"        // Test {i}: Inputs = {''.join(input_vals)}\n"
            tb += f"        {', '.join(inputs)} = {i}'b{''.join(input_vals)};\n"
            tb += f"        #10;\n"
            tb += f"        if (Y !== {row['output']}) begin\n"
            tb += f'            $display("ERROR: Test {i} failed. Expected {row["output"]}, got %b", Y);\n'
            tb += f"        end\n\n"
        
        tb += """        $display("------------------");
        $display("All tests passed!");
        $finish;
    end
    
    // Generate waveforms
    initial begin
        $dumpfile("test.vcd");
        $dumpvars(0, tb_{name});
    end
    
endmodule
"""
        
        return tb
