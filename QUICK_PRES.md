# ============================================================================
# IC HDL GENERATOR - QUICK COMMANDS
# ============================================================================

# LISTING COMMANDS
# ----------------
python3 advanced_generator.py list-supported           # List all ICs
python3 circuit_generator_advanced.py list             # List all circuits

# IC GENERATION (SINGLE)
# ----------------------
python3 advanced_generator.py ic 7400 --language verilog           # Verilog only
python3 advanced_generator.py ic 7400 --language vhdl              # VHDL only
python3 advanced_generator.py ic 7400 --language verilog --testbenches  # With testbench

# IC GENERATION (ALL)
# -------------------
python3 advanced_generator.py ic-all --language verilog            # All Verilog
python3 advanced_generator.py ic-all --language vhdl               # All VHDL
python3 advanced_generator.py ic-all --language verilog --testbenches  # All with testbenches

# TESTBENCH GENERATION
# --------------------
python3 advanced_generator.py testbench 7400                        # Single testbench
python3 advanced_generator.py testbench-all                         # All testbenches

# BOOLEAN EXPRESSIONS
# -------------------
python3 advanced_generator.py boolean "A&B"                         # AND gate
python3 advanced_generator.py boolean "A|B"                         # OR gate
python3 advanced_generator.py boolean "A^B"                         # XOR gate
python3 advanced_generator.py boolean "!(A&B)"                      # NAND gate
python3 advanced_generator.py boolean "(A&B)|(C&D)" --name complex  # Complex expression

# CIRCUIT COMPOSITION
# -------------------
python3 circuit_generator_advanced.py generate full_adder_1bit      # Generate full adder
python3 circuit_generator_advanced.py generate half_adder_1bit      # Generate half adder
python3 circuit_generator_advanced.py generate 2bit_adder           # Generate 2-bit adder
python3 circuit_generator_advanced.py generate 4bit_adder           # Generate 4-bit adder
python3 circuit_generator_advanced.py generate-all                  # Generate all circuits

# VIEW GENERATED FILES
# --------------------
ls -la generated_verilog/                                           # Verilog files
ls -la generated_vhdl/                                              # VHDL files
ls -la generated_testbenches/                                       # Testbench files
ls -la generated_circuits/                                          # Circuit files

# CLEANUP
# -------
rm -rf generated_*/*                                                # Remove all generated files
