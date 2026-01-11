import json
import os
from jinja2 import Environment, FileSystemLoader

class CircuitGenerator:
    def __init__(self, ic_db_path, template_dir):
        # Load IC database
        with open(ic_db_path, 'r') as f:
            self.ic_db = json.load(f)
        
        # Load circuit definitions
        with open('circuit_definitions/circuit_library.json', 'r') as f:
            self.circuit_db = json.load(f)
        
        # Setup template engine
        self.template_env = Environment(
            loader=FileSystemLoader(template_dir),
            trim_blocks=True,
            lstrip_blocks=True
        )
    
    def generate_circuit(self, circuit_name, language='verilog'):
        """Generate HDL for a complex circuit"""
        
        # Get circuit definition
        circuit = self.circuit_db[circuit_name]
        
        # Prepare template context
        context = {
            'circuit': circuit,
            'circuit_name': circuit_name,
            'instances': self._create_instances(circuit),
            'connections': self._parse_connections(circuit),
            'inputs': ['A', 'B', 'Cin'],  # Extract from circuit definition
            'outputs': ['Sum', 'Cout']
        }
        
        # Load and render template
        if language == 'verilog':
            template = self.template_env.get_template(f'verilog/circuits/{circuit_name}.vtpl')
        elif language == 'systemverilog':
            template = self.template_env.get_template(f'systemverilog/circuits/{circuit_name}.svtpl')
        elif language == 'vhdl':
            template = self.template_env.get_template(f'vhdl/circuits/{circuit_name}.vhdltpl')
        else:
            raise ValueError(f"Unsupported language: {language}")
        
        return template.render(context)
    
    def _create_instances(self, circuit):
        """Create instance list from circuit definition"""
        instances = []
        impl = circuit['implementation']['discrete_7400']
        
        ic_counter = {}
        for ic_req in impl['ics_required']:
            part = ic_req['part']
            count = ic_req.get('count', 1)
            
            for i in range(count):
                instance_name = f"{part}_{ic_counter.get(part, 0)}"
                ic_counter[part] = ic_counter.get(part, 0) + 1
                
                instances.append({
                    'name': instance_name,
                    'part': part,
                    'ports': self.ic_db[part]['ports']
                })
        
        return instances
    
    def _parse_connections(self, circuit):
        """Parse connection map from circuit definition"""
        connections = []
        impl = circuit['implementation']['discrete_7400']
        
        for conn_str in impl.get('connections', []):
            # Parse "target = source" format
            if '=' in conn_str:
                target, source = conn_str.split('=')
                connections.append({
                    'target': target.strip(),
                    'source': source.strip()
                })
        
        return connections
    
    def generate_testbench(self, circuit_name, language='systemverilog'):
        """Generate testbench for circuit"""
        circuit = self.circuit_db[circuit_name]
        
        context = {
            'circuit': circuit,
            'circuit_name': circuit_name,
            'test_vectors': self._generate_test_vectors(circuit)
        }
        
        if language == 'systemverilog':
            template = self.template_env.get_template('systemverilog/testbench.svtpl')
        elif language == 'verilog':
            template = self.template_env.get_template('verilog/testbench.vtpl')
        
        return template.render(context)
    
    def _generate_test_vectors(self, circuit):
        """Generate test vectors based on circuit type"""
        vectors = []
        
        if circuit['category'] == 'arithmetic':
            if 'full_adder' in circuit.get('description', '').lower():
                # 8 test vectors for 1-bit adder
                for a in [0, 1]:
                    for b in [0, 1]:
                        for cin in [0, 1]:
                            vectors.append({
                                'A': a, 'B': b, 'Cin': cin,
                                'Sum': a ^ b ^ cin,
                                'Cout': (a & b) | (cin & (a ^ b))
                            })
        
        return vectors
