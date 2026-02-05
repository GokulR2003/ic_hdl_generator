[11/01, 11:07] Gokul R: use the below code in terminal

# One-command setup
chmod +x run_quick_test.sh
./run_quick_test.sh

# Or step by step:
python setup_complete.py
python advanced_generator.py list-supported
python advanced_generator.py generate-all --language verilog --testbenches
python advanced_generator.py generate-all --language vhdl
[11/01, 15:19] Gokul R: # Install dependencies
sudo apt-get update
sudo apt-get install -y python3 python3-pip iverilog
pip3 install jinja2

# Setup directories and templates
python3 setup_complete.py

# Generate ICs
python3 advanced_generator.py list-supported
python3 advanced_generator.py generate-all --language verilog --language vhdl --testbenches

# Generate circuits
python3 circuit_generator_advanced.py list
python3 circuit_generator_advanced.py generate-all

# List all supported ICs
python3 advanced_generator.py list-supported

# Generate a specific IC
python3 advanced_generator.py generate 7400 --language verilog--language vhdl --testbenches

# Generate all ICs
python3 advanced_generator.py generate-all --language verilog--language vhdl --testbenches# List available circuits
python3 circuit_generator_advanced.py list

# Generate a specific circuit
python3 circuit_generator_advanced.py generate full_adder_1bit

# Generate all circuits
python3 circuit_generator_advanced.py generate-all
[11/01, 15:44] Gokul R: # Install dependencies
sudo apt-get update
sudo apt-get install -y python3 python3-pip iverilog
pip3 install jinja2

# Setup directories and templates
python3 setup_complete.py

# Generate all ICs
python3 advanced_generator.py list-supported
python3 advanced_generator.py generate-all --language verilog
python3 advanced_generator.py generate-all --language vhdl
python3 advanced_generator.py generate-all --testbenches

# Generate circuits
python3 circuit_generator_advanced.py list
python3 circuit_generator_advanced.py generate-all

# List all supported ICs
python3 advanced_generator.py list-supported

# Generate a specific IC
python3 advanced_generator.py generate 7400 --language verilog--language vhdl --testbenches

# List available circuits
python3 circuit_generator_advanced.py list

# Generate a specific circuit
python3 circuit_generator_advanced.py generate full_adder_1bit

# Generate all circuits
python3 circuit_generator_advanced.py generate-all
