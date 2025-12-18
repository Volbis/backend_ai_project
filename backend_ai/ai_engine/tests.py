from django.test import TestCase
from unittest.mock import Mock, patch, MagicMock
from .pipeline import AIPipeline
from .schemas import DocumentAnalysisResult
from .utils import validate_file, pdf_to_images, preprocess_image
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
import tempfile
import os


class OCRTests(TestCase):
    """Tests for PaddleOCR module"""
    
    def test_ocr_mock_mode(self):
        """Test OCR in mock mode (when PaddleOCR not installed)"""
        from .ocr.paddle_ocr import PaddleOCR
        
        with patch('ai_engine.ocr.paddle_ocr.PaddleOCRModel', None):
            ocr = PaddleOCR()
            self.assertIsNone(ocr.ocr)
            
            result = ocr.extract_text('dummy_path.jpg')
            self.assertEqual(len(result), 1)
            self.assertIn('text', result[0])
            self.assertIn('Mock Text', result[0]['text'])


class LayoutLMTests(TestCase):
    """Tests for LayoutLM module"""
    
    def test_layoutlm_mock_mode(self):
        """Test LayoutLM in mock mode"""
        from .layout.layoutlm import LayoutLM
        
        with patch('ai_engine.layout.layoutlm.LayoutLMv3Processor', None):
            layout = LayoutLM()
            self.assertIsNone(layout.processor)
            
            ocr_data = [{'text': 'Test', 'box': [0, 0, 100, 100]}]
            result = layout.analyze_layout('dummy.jpg', ocr_data)
            
            self.assertIn('document_type', result)
            self.assertIn('fields', result)
            self.assertEqual(result['document_type'], 'mock_type')


class LlamaAnalysisTests(TestCase):
    """Tests for Llama Analysis module"""
    
    def test_llama_mock_mode(self):
        """Test LlamaAnalysis in mock mode"""
        from .analysis.llama_analysis import LlamaAnalysis
        
        with patch('ai_engine.analysis.llama_analysis.OpenAI', None):
            llama = LlamaAnalysis()
            self.assertIsNone(llama.client)
            
            # Test verify_consistency
            result = llama.verify_consistency({'fields': {'raw_text': 'Test'}})
            self.assertIsInstance(result, list)
            
            # Test check_compliance
            score = llama.check_compliance({'fields': {'raw_text': 'Test'}})
            self.assertIsInstance(score, float)
            self.assertGreaterEqual(score, 0.0)
            self.assertLessEqual(score, 1.0)


class PipelineTests(TestCase):
    """Tests for AI Pipeline"""
    
    @patch('ai_engine.pipeline.PaddleOCR')
    @patch('ai_engine.pipeline.LayoutLM')
    @patch('ai_engine.pipeline.LlamaAnalysis')
    def test_pipeline_process_document(self, mock_llama, mock_layout, mock_ocr):
        """Test complete pipeline processing"""
        # Setup mocks
        mock_ocr_instance = Mock()
        mock_ocr_instance.extract_text.return_value = [
            {'text': 'John Doe', 'box': [0, 0, 100, 50], 'confidence': 0.99}
        ]
        mock_ocr.return_value = mock_ocr_instance
        
        mock_layout_instance = Mock()
        mock_layout_instance.analyze_layout.return_value = {
            'document_type': 'ID Card',
            'fields': {'raw_text': 'John Doe', 'name': 'John Doe'}
        }
        mock_layout.return_value = mock_layout_instance
        
        mock_llama_instance = Mock()
        mock_llama_instance.verify_consistency.return_value = []
        mock_llama_instance.check_compliance.return_value = 0.95
        mock_llama.return_value = mock_llama_instance
        
        # Test pipeline
        pipeline = AIPipeline()
        result = pipeline.process_document('test.jpg')
        
        self.assertIsInstance(result, DocumentAnalysisResult)
        self.assertEqual(result.document_type, 'ID Card')
        self.assertEqual(result.compliance_score, 0.95)
        self.assertEqual(result.rejection_probability, 0.05)


class FileValidationTests(TestCase):
    """Tests for file validation utilities"""
    
    def test_validate_file_size_limit(self):
        """Test file size validation"""
        # Create a file that exceeds limit
        large_content = b'x' * (11 * 1024 * 1024)  # 11MB
        large_file = SimpleUploadedFile(
            "large.pdf",
            large_content,
            content_type="application/pdf"
        )
        
        with self.assertRaises(ValidationError) as context:
            validate_file(large_file)
        self.assertIn('exceeds', str(context.exception))
    
    def test_validate_file_extension(self):
        """Test file extension validation"""
        bad_file = SimpleUploadedFile(
            "test.exe",
            b"content",
            content_type="application/x-msdownload"
        )
        
        with self.assertRaises(ValidationError) as context:
            validate_file(bad_file)
        self.assertIn('extension', str(context.exception).lower())
    
    def test_validate_file_valid(self):
        """Test valid file passes validation"""
        valid_file = SimpleUploadedFile(
            "test.pdf",
            b"%PDF-1.4 content",
            content_type="application/pdf"
        )
        
        # Should not raise exception
        try:
            result = validate_file(valid_file)
            self.assertTrue(result)
        except ValidationError:
            self.fail("Valid file should not raise ValidationError")


class ImagePreprocessingTests(TestCase):
    """Tests for image preprocessing utilities"""
    
    def test_preprocess_image_exists(self):
        """Test that preprocess_image function exists and returns path"""
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
            tmp.write(b'fake image data')
            tmp_path = tmp.name
        
        try:
            from PIL import Image
            # Create a real tiny image
            img = Image.new('RGB', (100, 100), color='red')
            img.save(tmp_path)
            
            result = preprocess_image(tmp_path)
            self.assertEqual(result, tmp_path)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)


class DocumentAnalysisResultTests(TestCase):
    """Tests for DocumentAnalysisResult schema"""
    
    def test_document_analysis_result_creation(self):
        """Test creating DocumentAnalysisResult"""
        result = DocumentAnalysisResult(
            document_type='ID Card',
            extracted_data={'name': 'John Doe'},
            missing_documents=['Birth Certificate'],
            inconsistencies=['Date in future'],
            compliance_score=0.85,
            rejection_probability=0.15,
            recommendations=['Fix date']
        )
        
        self.assertEqual(result.document_type, 'ID Card')
        self.assertEqual(result.compliance_score, 0.85)
        self.assertEqual(len(result.missing_documents), 1)
        self.assertEqual(len(result.inconsistencies), 1)
