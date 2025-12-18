from django.test import TestCase
from django.contrib.auth.models import User
from .models import Dossier, Document, Report
from django.core.files.uploadedfile import SimpleUploadedFile
import os


class DossierModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
    def test_dossier_creation(self):
        """Test creating a dossier"""
        dossier = Dossier.objects.create(
            user=self.user,
            reference_number='REF-2025-001',
            status='PENDING'
        )
        self.assertEqual(dossier.reference_number, 'REF-2025-001')
        self.assertEqual(dossier.status, 'PENDING')
        self.assertEqual(str(dossier), "Dossier REF-2025-001")
        
    def test_dossier_unique_reference(self):
        """Test that reference numbers must be unique"""
        Dossier.objects.create(
            user=self.user,
            reference_number='REF-2025-002'
        )
        with self.assertRaises(Exception):
            Dossier.objects.create(
                user=self.user,
                reference_number='REF-2025-002'
            )
    
    def test_dossier_default_status(self):
        """Test dossier default status is PENDING"""
        dossier = Dossier.objects.create(
            user=self.user,
            reference_number='REF-2025-003'
        )
        self.assertEqual(dossier.status, 'PENDING')


class DocumentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.dossier = Dossier.objects.create(
            user=self.user,
            reference_number='REF-2025-100'
        )
        
    def test_document_creation(self):
        """Test creating a document"""
        # Create a simple file
        test_file = SimpleUploadedFile(
            "test.pdf",
            b"file_content",
            content_type="application/pdf"
        )
        
        document = Document.objects.create(
            dossier=self.dossier,
            file=test_file,
            document_type='ID Card'
        )
        
        self.assertEqual(document.document_type, 'ID Card')
        self.assertEqual(document.dossier, self.dossier)
        self.assertTrue(document.file.name.endswith('test.pdf'))
        
    def test_document_dossier_relationship(self):
        """Test document-dossier relationship"""
        test_file = SimpleUploadedFile(
            "test.pdf",
            b"file_content",
            content_type="application/pdf"
        )
        
        doc1 = Document.objects.create(
            dossier=self.dossier,
            file=test_file,
            document_type='ID Card'
        )
        
        self.assertEqual(self.dossier.documents.count(), 1)
        self.assertEqual(self.dossier.documents.first(), doc1)


class ReportModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.dossier = Dossier.objects.create(
            user=self.user,
            reference_number='REF-2025-200'
        )
        
    def test_report_creation(self):
        """Test creating a report"""
        report = Report.objects.create(
            dossier=self.dossier,
            compliance_score=0.85,
            rejection_probability=0.15,
            details={'test': 'data'}
        )
        
        self.assertEqual(report.compliance_score, 0.85)
        self.assertEqual(report.rejection_probability, 0.15)
        self.assertEqual(report.details, {'test': 'data'})
        
    def test_report_dossier_relationship(self):
        """Test one-to-one relationship between report and dossier"""
        report = Report.objects.create(
            dossier=self.dossier,
            compliance_score=0.90,
            rejection_probability=0.10
        )
        
        self.assertEqual(self.dossier.report, report)
        self.assertEqual(report.dossier, self.dossier)


class DossierSerializerTest(TestCase):
    def setUp(self):
        from .serializers import DossierSerializer
        self.serializer_class = DossierSerializer
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
    def test_dossier_serializer_fields(self):
        """Test dossier serializer contains expected fields"""
        dossier = Dossier.objects.create(
            user=self.user,
            reference_number='REF-2025-300'
        )
        serializer = self.serializer_class(dossier)
        
        self.assertIn('reference_number', serializer.data)
        self.assertIn('status', serializer.data)
        self.assertIn('documents', serializer.data)
        self.assertIn('created_at', serializer.data)
        
    def test_dossier_serializer_with_documents(self):
        """Test dossier serializer includes related documents"""
        dossier = Dossier.objects.create(
            user=self.user,
            reference_number='REF-2025-301'
        )
        
        test_file = SimpleUploadedFile(
            "test.pdf",
            b"file_content",
            content_type="application/pdf"
        )
        
        Document.objects.create(
            dossier=dossier,
            file=test_file,
            document_type='ID Card'
        )
        
        serializer = self.serializer_class(dossier)
        self.assertEqual(len(serializer.data['documents']), 1)
        

class DocumentSerializerTest(TestCase):
    def setUp(self):
        from .serializers import DocumentSerializer
        self.serializer_class = DocumentSerializer
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.dossier = Dossier.objects.create(
            user=self.user,
            reference_number='REF-2025-400'
        )
        
    def test_document_serializer_fields(self):
        """Test document serializer contains expected fields"""
        test_file = SimpleUploadedFile(
            "test.pdf",
            b"file_content",
            content_type="application/pdf"
        )
        
        document = Document.objects.create(
            dossier=self.dossier,
            file=test_file,
            document_type='ID Card'
        )
        
        serializer = self.serializer_class(document)
        
        self.assertIn('dossier', serializer.data)
        self.assertIn('file', serializer.data)
        self.assertIn('document_type', serializer.data)
        self.assertIn('uploaded_at', serializer.data)


class ReportSerializerTest(TestCase):
    def setUp(self):
        from .serializers import ReportSerializer
        self.serializer_class = ReportSerializer
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.dossier = Dossier.objects.create(
            user=self.user,
            reference_number='REF-2025-500'
        )
        
    def test_report_serializer_fields(self):
        """Test report serializer contains expected fields"""
        report = Report.objects.create(
            dossier=self.dossier,
            compliance_score=0.75,
            rejection_probability=0.25,
            details={'analysis': 'complete'}
        )
        
        serializer = self.serializer_class(report)
        
        self.assertIn('dossier', serializer.data)
        self.assertIn('compliance_score', serializer.data)
        self.assertIn('rejection_probability', serializer.data)
        self.assertIn('details', serializer.data)
        self.assertEqual(serializer.data['compliance_score'], 0.75)


