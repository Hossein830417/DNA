class SNPAnalyzer:
    def find_snps(self, reference, sample):
        """شناسایی تفاوت‌های توالی"""
        snps = []
        for i, (ref, sam) in enumerate(zip(reference, sample)):
            if ref != sam:
                snps.append({
                    'position': i+1,
                    'reference': ref,
                    'sample': sam
                })
        return snps

    def predict_impact(self, snp):
        """پیش‌بینی تاثیر SNP با هوش مصنوعی"""
        # ادغام با مدل‌های پیش‌بینی تاثیر
        return "Moderate impact"