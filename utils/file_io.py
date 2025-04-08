import json

def load_dna_file(file_path):
    """Load DNA sequence from file"""
    with open(file_path, 'r') as file:
        content = file.read().strip().upper()
        # Remove any non-DNA characters
        return ''.join([c for c in content if c in {'A', 'T', 'C', 'G'}])

def save_dna_file(file_path, sequence, complement=None):
    """Save DNA sequence to file"""
    with open(file_path, 'w') as file:
        file.write(f"DNA Sequence: {sequence}\n")
        if complement:
            file.write(f"Complement: {complement}\n")

def load_config(config_path='config.json'):
    """Load application configuration"""
    with open(config_path) as config_file:
        return json.load(config_file)