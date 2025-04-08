from Bio.Seq import Seq
from Bio import pairwise2
from Bio.SeqUtils import gc_fraction
from analysis.sequence_db import SEQUENCE_DATABASE
import numpy as np
import re

class DNADetector:
    def __init__(self):
        self.common_patterns = {
            'promoter': re.compile(r'[AT]TATA[AT]A[AT]'),
            'terminator': re.compile(r'GCGC[GC]+|ATAT[AT]+'),
            'orf': re.compile(r'ATG(?:\w{3})*?(?:TAA|TAG|TGA)')
        }

    def identify_sequence(self, sequence):
        """شناسایی توالی در دیتابیس و برگرداندن اطلاعات"""
        sequence = sequence.upper()
        for seq_id, data in SEQUENCE_DATABASE.items():
            if sequence in data['sequence']:
                return {
                    'id': seq_id,
                    'name': data['name'],
                    'type': data['type'],
                    'description': data['description'],
                    'match_position': data['sequence'].index(sequence)
                }
        return None

    def detect_features(self, sequence):
        """تشخیص ویژگی‌ها با مدیریت خطای کامل"""
        try:
            if not isinstance(sequence, str):
                raise ValueError("Input must be a string")
                
            sequence = sequence.upper()
            if not all(c in 'ATCG' for c in sequence):
                raise ValueError("Invalid DNA sequence")
                
            # شناسایی توالی (حتی اگر None باشد)
            seq_info = self.identify_sequence(sequence) or {
                'name': 'Unknown Sequence',
                'type': 'custom',
                'description': 'User-provided sequence'
            }
            
            return {
                'sequence_info': seq_info,  # این خط اضافه شد
                'gc_content': self.calculate_gc_content(sequence),
                'patterns': self.find_patterns(sequence),
                'orf': self.find_open_reading_frames(sequence),
                'repeats': self.find_repeats(sequence),
                'hairpins': self.detect_hairpins(sequence),
                'length': len(sequence)
            }
        except Exception as e:
            return {
                'error': str(e),
                'sequence_info': {
                    'name': 'Error',
                    'type': 'error',
                    'description': 'Analysis failed'
                }
            }

    def calculate_gc_content(self, sequence):
        """محاسبه درصد GC"""
        return round(gc_fraction(sequence) * 100, 2)

    def find_patterns(self, sequence):
        """یافتن الگوهای شناخته شده"""
        found = {}
        for name, pattern in self.common_patterns.items():
            matches = pattern.finditer(sequence)
            found[name] = [{'start': m.start(), 'end': m.end()} for m in matches]
        return found

    def find_open_reading_frames(self, sequence):
        """یافتن چارچوب‌های خوانش باز"""
        orfs = []
        for frame in range(3):
            trans = str(Seq(sequence[frame:]).translate())
            start_pos = -1
            for i, aa in enumerate(trans):
                if aa == 'M' and start_pos == -1:
                    start_pos = i
                elif aa == '*' and start_pos != -1:
                    orfs.append({
                        'frame': frame + 1,
                        'start': start_pos * 3 + frame,
                        'end': i * 3 + 3 + frame,
                        'length': (i - start_pos) * 3
                    })
                    start_pos = -1
        return orfs

    def find_repeats(self, sequence, min_length=4):
        """یافتن تکرارها"""
        repeats = {}
        for i in range(len(sequence) - min_length + 1):
            substr = sequence[i:i+min_length]
            if sequence.count(substr) > 1:
                if substr not in repeats:
                    repeats[substr] = []
                repeats[substr].append(i)
        return {k: v for k, v in repeats.items() if len(v) > 1}

    def detect_hairpins(self, sequence, min_stem=5, min_loop=3):
        """تشخیص ساختارهای سنجاق‌سری"""
        hairpins = []
        comp = str(Seq(sequence).complement())
        for i in range(len(sequence) - (2*min_stem + min_loop)):
            for j in range(i+min_stem+min_loop, len(sequence)-min_stem):
                stem1 = sequence[i:i+min_stem]
                stem2 = comp[j:j+min_stem]
                if stem1 == stem2[::-1]:
                    hairpins.append({
                        'start': i,
                        'end': j+min_stem,
                        'loop_start': i+min_stem,
                        'loop_end': j
                    })
        return hairpins

    def align_sequences(self, seq1, seq2):
        """همترازی دو توالی"""
        alignments = pairwise2.align.globalxx(seq1, seq2)
        return alignments[0] if alignments else None