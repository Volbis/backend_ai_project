
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
            # This part depends heavily on the labels the model was trained on.
            # The base model doesn't have specific labels for "Name", "Date", etc.
            # For this MVP, we will return the raw OCR text structured by the model's tokenization
            
            predictions = outputs.logits.argmax(-1).squeeze().tolist()
            logger.info(f"Layout analysis completed for {image_path}")
            
            return {
                "document_type": "detected_via_classification_head", # Placeholder
                "fields": {
                    "raw_text": " ".join(words),
                    "segments": ocr_results
                }
            }
        except Exception as e:
            logger.error(f"Layout analysis failed for {image_path}: {e}")
            return {"document_type": "error", "fields": {}}
 