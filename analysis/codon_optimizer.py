class CodonOptimizer:
    def __init__(self):
        self.host_preferences = {
            'e_coli': self._load_codon_table('e_coli'),
            'human': self._load_codon_table('human')
        }

    def optimize(self, protein_sequence, host='e_coli'):
        """بهینه‌سازی کدون برای میزبان خاص"""
        optimized_dna = ""
        table = self.host_preferences.get(host, {})
        for aa in protein_sequence:
            optimized_dna += self._choose_best_codon(aa, table)
        return optimized_dna