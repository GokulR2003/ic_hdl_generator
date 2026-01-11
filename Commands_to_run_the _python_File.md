# Install dependencies
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
python3 advanced_generator.py generate 7400 --language verilog --testbenches

# Generate all ICs
python3 advanced_generator.py generate-all --language verilog --testbenches# List available circuits
python3 circuit_generator_advanced.py list

# Generate a specific circuit
python3 circuit_generator_advanced.py generate full_adder_1bit

# Generate all circuits
python3 circuit_generator_advanced.py generate-all
