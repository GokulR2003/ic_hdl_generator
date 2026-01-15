#!/usr/bin/env python3
"""
K-map Solver
"""

from typing import Dict, List, Optional

class KMapSolver:
    def __init__(self):
        pass
    
    def solve(self, minterms: List[int], num_vars: int = 3, 
              dont_cares: List[int] = None) -> Dict:
        """Solve K-map and return simplified expression"""
        
        if num_vars == 2:
            return self._solve_2var(minterms, dont_cares)
        elif num_vars == 3:
            return self._solve_3var(minterms, dont_cares)
        else:
            return self._simplify_sop(minterms, num_vars)
    
    def _solve_2var(self, minterms: List[int], dont_cares: List[int]) -> Dict:
        """Solve 2-variable K-map"""
        # K-map patterns for 2 variables
        kmap_patterns = {
            (0,): "A'B'",
            (1,): "A'B",
            (2,): "AB'",
            (3,): "AB",
            (0, 1): "A'",
            (2, 3): "A",
            (0, 2): "B'",
            (1, 3): "B",
            (0, 3): "A'B' + AB",  # XOR pattern
            (1, 2): "A'B + AB'",  # XNOR pattern (complement)
            (0, 1, 2, 3): "1",    # Always true
        }
        
        minterms_tuple = tuple(sorted(minterms))
        if minterms_tuple in kmap_patterns:
            expression = kmap_patterns[minterms_tuple]
        else:
            # Generate SOP from minterms
            terms = []
            for m in minterms:
                a = (m >> 1) & 1
                b = m & 1
                term_a = "A" if a else "A'"
                term_b = "B" if b else "B'"
                terms.append(f"{term_a}{term_b}")
            expression = " + ".join(terms)
        
        return {
            "sop_expression": expression,
            "pos_expression": self._sop_to_pos(expression),
            "gate_count": self._count_gates(expression),
            "simplified": len(minterms_tuple) > 1
        }
    
    def _solve_3var(self, minterms: List[int], dont_cares: List[int]) -> Dict:
        """Solve 3-variable K-map (placeholder)"""
        # For now, just generate SOP
        return self._simplify_sop(minterms, 3)
    
    def _simplify_sop(self, minterms: List[int], num_vars: int) -> Dict:
        """Generate SOP from minterms"""
        variables = ['A', 'B', 'C', 'D'][:num_vars]
        terms = []
        
        for m in minterms:
            term_parts = []
            for i, var in enumerate(variables):
                bit = (m >> (num_vars - i - 1)) & 1
                term_parts.append(f"{var}" if bit else f"{var}'")
            terms.append("".join(term_parts))
        
        sop = " + ".join(terms)
        
        return {
            "sop_expression": sop,
            "gate_count": self._count_gates(sop),
            "simplified": False
        }
    
    def _sop_to_pos(self, sop: str) -> str:
        """Convert SOP to POS (simplified)"""
        # This is a placeholder - implement proper conversion
        return f"({sop})'"  # Just negate for now
    
    def _count_gates(self, expression: str) -> Dict:
        """Count gates needed for expression"""
        gate_counts = {
            "AND": expression.count("·") + expression.count("&") + expression.count("AB") // 2,
            "OR": expression.count("+") + expression.count("|"),
            "NOT": expression.count("'") + expression.count("!"),
            "XOR": expression.count("^") + expression.count("⊕"),
            "NAND": expression.count("~&"),
            "NOR": expression.count("~|"),
            "XNOR": expression.count("~^")
        }
        
        # Remove zeros
        gate_counts = {k: v for k, v in gate_counts.items() if v > 0}
        
        return gate_counts
