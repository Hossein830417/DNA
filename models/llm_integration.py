from transformers import pipeline

class LLMAnalysis:
    def __init__(self):
        self.function_predictor = pipeline(
            "text-generation",
            model="bio-llm/protein-function"
        )

    def predict_function(self, protein_sequence):
        """پیش‌بینی عملکرد پروتئین با مدل زبان"""
        return self.function_predictor(protein_sequence)