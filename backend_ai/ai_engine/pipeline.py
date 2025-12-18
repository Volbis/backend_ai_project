from .ocr.paddle_ocr import PaddleOCR
from .layout.layoutlm import LayoutLM
from .analysis.llama_analysis import LlamaAnalysis
from .schemas import DocumentAnalysisResult
from .document_requirements import check_missing_documents

class AIPipeline: 
    def __init__(self): 
        self.ocr = PaddleOCR() 
        self.layout = LayoutLM()
        self.analysis = LlamaAnalysis()

    def process_document(self, file_path: str, application_type: str = 'general') -> DocumentAnalysisResult:
        # 1. OCR
        # Returns list of dicts: [{'text': '...', 'box': [...]}, ...]
        ocr_data = self.ocr.extract_text(file_path)
        
        # 2. Layout Analysis
        # Takes structured OCR data
        layout_data = self.layout.analyze_layout(file_path, ocr_data)
        
        # 3. Semantic Analysis & Verification
        inconsistencies = self.analysis.verify_consistency(layout_data)
        compliance_score = self.analysis.check_compliance(layout_data)
        
        # 4. Generate recommendations based on analysis
        recommendations = self._generate_recommendations(layout_data, inconsistencies, compliance_score)
        
        # Construct result
        return DocumentAnalysisResult(
            document_type=layout_data.get("document_type", "unknown"),
            extracted_data=layout_data.get("fields", {}),
            missing_documents=[],  # Filled at dossier level, not individual document
            inconsistencies=inconsistencies,
            compliance_score=compliance_score,
            rejection_probability=1.0 - compliance_score,
            recommendations=recommendations
        )
    
    def _generate_recommendations(self, layout_data: dict, inconsistencies: list, compliance_score: float) -> list:
        """Generate actionable recommendations based on analysis"""
        recommendations = []
        
        if compliance_score < 0.5:
            recommendations.append("Document quality is poor. Please rescan with better lighting and resolution.")
        elif compliance_score < 0.8:
            recommendations.append("Some fields may be unclear. Please verify all information is legible.")
        
        if inconsistencies:
            recommendations.append(f"Found {len(inconsistencies)} inconsistencies that need attention.")
        
        doc_type = layout_data.get("document_type", "Unknown")
        if doc_type == "Unknown":
            recommendations.append("Document type could not be identified. Please ensure the document is clear and complete.")
        
        if not recommendations:
            recommendations.append("Document appears to be in good condition.")
        
        return recommendations
