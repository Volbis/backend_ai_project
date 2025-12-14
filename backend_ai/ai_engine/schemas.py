from dataclasses import dataclass
from typing import List, Optional, Dict, Any

@dataclass
class ExtractedText:
    text: str
    confidence: float
    bbox: List[int]  # [x1, y1, x2, y2]

@dataclass
class DocumentAnalysisResult:
    document_type: str
    extracted_data: Dict[str, Any]
    missing_documents: List[str]
    inconsistencies: List[str]
    compliance_score: float
    rejection_probability: float
    recommendations: List[str]
