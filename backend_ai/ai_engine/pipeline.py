from .ocr.paddle_ocr import PaddleOCR
from .layout.layoutlm import LayoutLM
from .analysis.llama_analysis import LlamaAnalysis
from .schemas import DocumentAnalysisResult

class AIPipeline: 
    def __init__(self): 
        self.ocr = PaddleOCR()
        self.layout = LayoutLM()
        self.analysis = LlamaAnalysis()

    def process_document(self, file_path: str) -> DocumentAnalysisResult:
        # 1. OCR
        # Returns list of dicts: [{'text': '...', 'box': [...]}, ...]
        ocr_data = self.ocr.extract_text(file_path)
        
        # 2. Layout Analysis
        # Takes structured OCR data
        layout_data = self.layout.analyze_layout(file_path, ocr_data)
        
        # 3. Semantic Analysis & Verification
        inconsistencies = self.analysis.verify_consistency(layout_data)
        compliance_score = self.analysis.check_compliance(layout_data)
        
        # Construct result
        return DocumentAnalysisResult(
            document_type=layout_data.get("document_type", "unknown"),
            extracted_data=layout_data.get("fields", {}),
            missing_documents=[], # Logic to check against required docs would go here
            inconsistencies=inconsistencies,
            compliance_score=compliance_score,
            rejection_probability=1.0 - compliance_score,
            recommendations=["Ensure all fields are visible"] if compliance_score < 1.0 else []
        )
