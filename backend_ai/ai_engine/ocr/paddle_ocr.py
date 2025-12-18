
# Permet d'extraire le texte des images en utilisant PaddleOCR

import logging
logger = logging.getLogger('ai_engine')

try:
    from paddleocr import PaddleOCR as PaddleOCRModel
except ImportError:
    PaddleOCRModel = None

class PaddleOCR:
    def __init__(self, lang='fr'):
        if PaddleOCRModel is None:
            logger.warning("PaddleOCR not installed. Using mock mode.")
            self.ocr = None
        else:
            try:
                # Initialize PaddleOCR
                # use_angle_cls=True enables angle classification
                self.ocr = PaddleOCRModel(use_angle_cls=True, lang=lang, show_log=False)
                logger.info(f"PaddleOCR initialized with language: {lang}")
            except Exception as e:
                logger.error(f"Failed to initialize PaddleOCR: {e}")
                self.ocr = None

    def extract_text(self, image_path: str):
        """
        Returns a list of dictionaries:
        [{'text': '...', 'confidence': 0.99, 'box': [x1, y1, x2, y2]}]
        """
        try:
            if self.ocr is None:
                logger.warning("Using mock OCR data")
                return [{"text": "Mock Text", "confidence": 0.99, "box": [0, 0, 100, 100]}]

            logger.info(f"Running OCR on {image_path}...")
            result = self.ocr.ocr(image_path, cls=True)
            
            extracted_data = []
            if not result or result[0] is None:
                logger.warning(f"No text detected in {image_path}")
                return extracted_data

            for line in result[0]:
                # line structure: [ [[x1,y1],[x2,y2],[x3,y3],[x4,y4]], (text, confidence) ]
                coords = line[0]
                text, confidence = line[1]
                
                # Convert 4 points to [x1, y1, x2, y2] (min/max) for LayoutLM
                x_coords = [pt[0] for pt in coords]
                y_coords = [pt[1] for pt in coords]
                x1, y1 = min(x_coords), min(y_coords)
                x2, y2 = max(x_coords), max(y_coords)
                
                extracted_data.append({
                    "text": text,
                    "confidence": confidence,
                    "box": [int(x1), int(y1), int(x2), int(y2)]
                })
            
            logger.info(f"Extracted {len(extracted_data)} text segments from {image_path}")
            return extracted_data
            
        except Exception as e:
            logger.error(f"OCR extraction failed for {image_path}: {e}")
            return []
            
        return extracted_data
 