# technology_mapper.py
from gate_database import GateDatabase
from typing import List, Dict

class TechnologyMapper:
    def __init__(self, technology: str = "TTL"):
        self.db = GateDatabase()
        self.technology = technology
    
    def map_expression_to_ics(self, expression_info: Dict) -> Dict:
        """Map simplified expression to physical ICs"""
        
        # Extract gate counts
        gate_counts = expression_info.get("gate_counts", {})
        
        ic_requirements = {}
        total_ics = 0
        
        for gate_type, count in gate_counts.items():
            if count == 0:
                continue
            
            gate_info = self.db.get_gate(gate_type)
            if not gate_info:
                continue
            
            # Get recommended IC for this gate
            recommended_ic = self.db.get_recommended_ic(gate_type, self.technology)
            if not recommended_ic:
                continue
            
            gates_per_ic = recommended_ic["gates_per_package"]
            ics_needed = (count + gates_per_ic - 1) // gates_per_ic
            
            ic_requirements[gate_type] = {
                "ic": recommended_ic["ic_number"],
                "ic_name": recommended_ic["ic_name"],
                "gates_needed": count,
                "gates_per_package": gates_per_ic,
                "packages_needed": ics_needed,
                "cost": recommended_ic.get("cost_relative", 1.0) * ics_needed
            }
            
            total_ics += ics_needed
        
        # Calculate alternative implementations using universal gates
        nand_alternative = self._get_universal_alternative(gate_counts, "NAND")
        nor_alternative = self._get_universal_alternative(gate_counts, "NOR")
        
        return {
            "primary_implementation": ic_requirements,
            "total_ics": total_ics,
            "technology": self.technology,
            "alternatives": {
                "nand_only": nand_alternative,
                "nor_only": nor_alternative
            }
        }
    
    def _get_universal_alternative(self, gate_counts: Dict, universal_gate: str) -> Dict:
        """Convert all gates to universal gate implementation"""
        
        universal_info = self.db.get_gate(universal_gate)
        if not universal_info:
            return None
        
        # Get decomposition rules
        decompositions = universal_info["synthesis_rules"]["decomposition"]
        if "basic_gates_from_nand" in decompositions:
            rules = decompositions["basic_gates_from_nand"]
        elif "basic_gates_from_nor" in decompositions:
            rules = decompositions["basic_gates_from_nor"]
        else:
            return None
        
        total_universal_gates = 0
        
        for gate_type, count in gate_counts.items():
            if gate_type == universal_gate:
                total_universal_gates += count
                continue
            
            if gate_type in rules:
                gates_needed = rules[gate_type]["gates_needed"]
                total_universal_gates += count * gates_needed
        
        # Calculate IC requirements
        recommended_ic = self.db.get_recommended_ic(universal_gate, self.technology)
        if not recommended_ic:
            return None
        
        gates_per_ic = recommended_ic["gates_per_package"]
        ics_needed = (total_universal_gates + gates_per_ic - 1) // gates_per_ic
        
        return {
            "universal_gate": universal_gate,
            "total_gates_needed": total_universal_gates,
            "ic": recommended_ic["ic_number"],
            "packages_needed": ics_needed,
            "cost": recommended_ic.get("cost_relative", 1.0) * ics_needed
        }
