
# Identifie quel type de document est fourni en entrée (facture, carte d'id, reçu, bon de commande, etc.)
# Prends les champs clés

import logging
logger = logging.getLogger('ai_engine')

try:
    from transformers import LayoutLMv3Processor, LayoutLMv3ForTokenClassification
    from PIL import Image
    import torch
except ImportError:
    LayoutLMv3Processor = None
    logger.warning("transformers/torch not installed")

class LayoutLM: 
    def __init__(self):
        if LayoutLMv3Processor is None:
            logger.warning("LayoutLM not available. Using mock mode.")
            self.processor = None
            return

        try:
            # Load pre-trained model and processor
            # Note: For production, you should use a model fine-tuned on your specific document types
            self.model_name = "microsoft/layoutlmv3-base" 
            logger.info(f"Loading LayoutLMv3 model: {self.model_name}")
            self.processor = LayoutLMv3Processor.from_pretrained(self.model_name, apply_ocr=False)
            self.model = LayoutLMv3ForTokenClassification.from_pretrained(self.model_name)
            self.model.eval()
            
            # Check for GPU
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            self.model.to(self.device)
            logger.info(f"LayoutLM initialized on device: {self.device}")
        except Exception as e:
            logger.error(f"Failed to initialize LayoutLM: {e}")
            self.processor = None

    def analyze_layout(self, image_path: str, ocr_results: list):
        try:
            if self.processor is None:
                logger.warning("Using mock layout analysis")
                return {
                    "document_type": "mock_type",
                    "fields": {"raw_text": "Mock Text", "segments": ocr_results}
                }

            if not ocr_results:
                logger.warning(f"No OCR results for {image_path}")
                return {"document_type": "unknown", "fields": {}}

            logger.info(f"Analyzing layout for {image_path}")
            image = Image.open(image_path).convert("RGB")
            
            # Prepare data for LayoutLM
            words = [item['text'] for item in ocr_results]
            boxes = [item['box'] for item in ocr_results]
            
            # Normalize boxes (0-1000)
            width, height = image.size
            normalized_boxes = [
                [
                    int(b[0] * 1000 / width),
                    int(b[1] * 1000 / height),
                    int(b[2] * 1000 / width),
                    int(b[3] * 1000 / height)
                ]
                for b in boxes
            ]

            # Encoding
            encoding = self.processor(
                image,
                words,
                boxes=normalized_boxes,
                return_tensors="pt",
                truncation=True
            )
            
            # Move to device
            encoding = {k: v.to(self.device) for k, v in encoding.items()}

            # Inference
            with torch.no_grad():
                outputs = self.model(**encoding)
            
            # Process outputs (logits to predictions)
            # For MVP, use simple heuristics to detect document type from text content
            all_text = " ".join(words).lower()
            
            # Simple keyword-based classification
            document_type = self._classify_document_type(all_text, ocr_results)
            
            predictions = outputs.logits.argmax(-1).squeeze().tolist()
            logger.info(f"Layout analysis completed for {image_path}. Detected type: {document_type}")
            
            return {
                "document_type": document_type,
                "fields": {
                    "raw_text": " ".join(words),
                    "segments": ocr_results
                }
            }
        except Exception as e:
            logger.error(f"Layout analysis failed for {image_path}: {e}")
            return {"document_type": "error", "fields": {}}
    
    def _classify_document_type(self, text: str, ocr_results: list) -> str:
        """Simple keyword-based document type classification"""
        text_lower = text.lower()
        
        # Check for ID card keywords
        id_keywords = ['carte', 'identité', 'identity', 'card', 'national', 'passport', 'passeport']
        if any(keyword in text_lower for keyword in id_keywords):
            return "ID_Card"
        
        # Check for transcript/diploma keywords
        transcript_keywords = ['relevé', 'notes', 'transcript', 'diplôme', 'diploma', 'université', 'university']
        if any(keyword in text_lower for keyword in transcript_keywords):
            return "Academic_Transcript"
        
        # Check for birth certificate keywords
        birth_keywords = ['naissance', 'birth', 'certificate', 'acte', 'né', 'born']
        if any(keyword in text_lower for keyword in birth_keywords):
            return "Birth_Certificate"
        
        # Check for proof of residence keywords
        residence_keywords = ['domicile', 'résidence', 'residence', 'facture', 'bill', 'électricité', 'electricity']
        if any(keyword in text_lower for keyword in residence_keywords):
            return "Proof_of_Residence"
        
        # Check for invoice/receipt keywords
        invoice_keywords = ['facture', 'invoice', 'reçu', 'receipt', 'total', 'montant', 'amount']
        if any(keyword in text_lower for keyword in invoice_keywords):
            return "Invoice"
        
        return "Unknown"
 