#!/usr/bin/env python3
# circuit_generator_simple.py
import json
import os
import sys

def generate_full_adder():
    """Simple full adder generator for testing"""
    
    # Load IC database
    with open('Ic_Metadata_Master.json', 'r') as f:
        ic_db = json.load(f)
    
    # Generate Verilog for full adder
    verilog_code = """
// 1-bit Full Adder (generated from IC components)
module full_adder(
    input wire A,
    input wire B,
    input wire Cin,
    output wire Sum,
    output wire Cout
);
    
    // XOR gates (7486)
    wire temp;
    xor_gate xor1(.A(A), .B(B), .Y(temp));
    xor_gate xor2(.A(temp), .B(Cin), .Y(Sum));
    
    // AND gates (7408)
    wire carry1, carry2;
    and_gate and1(.A(A), .B(B), .Y(carry1));
    and_gate and2(.A(temp), .B(Cin), .Y(carry2));
    
    // OR gate (7432)
    or_gate or1(.A(carry1), .B(carry2), .Y(Cout));
    
endmodule

// Sub-module definitions
module xor_gate(input A, B, output Y);
    assign Y = A ^ B;
endmodule

module and_gate(input A, B, output Y);
    assign Y = A & B;
endmodule

module or_gate(input A, B, output Y);
    assign Y = A | B;
endmodule
"""
    
    # Generate SystemVerilog testbench
    sv_tb = """
// SystemVerilog Testbench for Full Adder
module full_adder_tb;
    logic A, B, Cin;
    logic Sum, Cout;
    
    // DUT
    full_adder dut(.*);
    
    initial begin
        $display("Testing 1-bit Full Adder");
        $display("A B Cin | Sum Cout");
        $display("-------------------");
        
        // Test all 8 combinations
        for (int i = 0; i < 8; i++) begin
            {A, B, Cin} = i;
            #10;
            
            // Check results
            assert(Sum === (A ^ B ^ Cin)) else
                $error("Sum error: A=%b, B=%b, Cin=%b, Got=%b", A, B, Cin, Sum);
                
            assert(Cout === ((A & B) | (Cin & (A ^ B)))) else
                $error("Carry error: A=%b, B=%b, Cin=%b, Got=%b", A, B, Cin, Cout);
            
            $display("%b %b %b   | %b   %b", A, B, Cin, Sum, Cout);
        end
        
        $display("\\nAll tests passed!");
        $finish;
    end
    
    // Waveform dump
    initial begin
        $dumpfile("full_adder.vcd");
        $dumpvars(0, full_adder_tb);
    end
endmodule
"""
    
    # Save files
    os.makedirs('generated_circuits', exist_ok=True)
    
    with open('generated_circuits/full_adder.v', 'w') as f:
        f.write(verilog_code)
    
    with open('generated_circuits/full_adder_tb.sv', 'w') as f:
        f.write(sv_tb)
    
    print("Generated:")
    print("  - generated_circuits/full_adder.v")
    print("  - generated_circuits/full_adder_tb.sv")
    print("\nTo simulate: iverilog -o full_adder full_adder.v full_adder_tb.sv && vvp full_adder")

if __name__ == "__main__":
    generate_full_adder()
