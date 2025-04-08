from Bio.Seq import Seq

def calculate_complement(dna_sequence):
    """Calculate complement of DNA sequence"""
    return str(Seq(dna_sequence).complement())

def calculate_gc_content(dna_sequence):
    """Calculate GC content percentage"""
    gc_count = dna_sequence.upper().count('G') + dna_sequence.upper().count('C')
    return (gc_count / len(dna_sequence)) * 100 if dna_sequence else 0

def validate_dna_sequence(dna_sequence):
    """Validate DNA sequence contains only ATGC"""
    return all(nuc.upper() in {'A', 'T', 'C', 'G'} for nuc in dna_sequence)