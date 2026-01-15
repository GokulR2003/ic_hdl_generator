#!/usr/bin/env python3
"""
Gate Database Loader
"""

import json
from typing import Dict, List, Optional

class GateDatabase:
    def __init__(self, db_path: str = "metadata/gate_primitives.json"):
        try:
            with open(db_path, 'r') as f:
                self.data = json.load(f)
        except FileNotFoundError:
            print(f"Warning: {db_path} not found. Using empty database.")
            self.data = []
        
        # Create lookup dictionaries for fast access
        self.by_id = {gate["primitive_id"]: gate for gate in self.data}
        self.by_symbol = {}
        
        # Build symbol mapping
        for gate in self.data:
            symbols = gate.get("logic_properties", {})
            if "symbol" in symbols:
                self.by_symbol[symbols["symbol"]] = gate
            
            # Also map common alternative symbols
            if gate["primitive_id"] == "AND":
                self.by_symbol["&"] = gate
                self.by_symbol["·"] = gate
            elif gate["primitive_id"] == "OR":
                self.by_symbol["|"] = gate
                self.by_symbol["+"] = gate
            elif gate["primitive_id"] == "NOT":
                self.by_symbol["!"] = gate
                self.by_symbol["'"] = gate
            elif gate["primitive_id"] == "XOR":
                self.by_symbol["^"] = gate
                self.by_symbol["⊕"] = gate
    
    def get_gate(self, gate_id: str) -> Optional[Dict]:
        return self.by_id.get(gate_id.upper())
    
    def get_gate_by_symbol(self, symbol: str) -> Optional[Dict]:
        return self.by_symbol.get(symbol)
    
    def get_ics_for_gate(self, gate_id: str, technology: str = "TTL") -> List[Dict]:
        gate = self.get_gate(gate_id)
        if not gate:
            return []
        return gate.get("ic_implementations", {}).get(technology, [])
    
    def get_recommended_ic(self, gate_id: str, technology: str = "TTL") -> Optional[Dict]:
        ics = self.get_ics_for_gate(gate_id, technology)
        for ic in ics:
            if ic.get("recommended"):
                return ic
        return ics[0] if ics else None
    
    def get_truth_vector(self, gate_id: str, num_inputs: int = 2) -> Optional[str]:
        gate = self.get_gate(gate_id)
        if not gate:
            return None
        patterns = gate.get("truth_patterns", {})
        key = f"{num_inputs}_input" if num_inputs > 1 else "1_input"
        return patterns.get(key, {}).get("vector")
