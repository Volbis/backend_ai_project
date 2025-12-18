from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.exceptions import ValidationError
from .models import Dossier, Document, Report
from .serializers import DossierSerializer, DocumentSerializer, ReportSerializer
from .services import DossierService
from ai_engine.utils import validate_file
import logging

logger = logging.getLogger('ai_engine')

class DossierViewSet(viewsets.ModelViewSet):
    queryset = Dossier.objects.all()
    serializer_class = DossierSerializer

    @action(detail=True, methods=['post'])
    def analyze(self, request, pk=None):
        try:
            dossier = self.get_object()
            service = DossierService()
            # In a real app, this should be a background task (Celery)
            service.process_dossier(dossier.id)
            
            dossier.refresh_from_db()
            return Response({'status': dossier.status})
        except Exception as e:
            logger.error(f"Analysis failed for dossier {pk}: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    parser_classes = (MultiPartParser, FormParser)
    
    def create(self, request, *args, **kwargs):
        try:
            # Validate file before saving
            if 'file' in request.FILES:
                validate_file(request.FILES['file'])
            return super().create(request, *args, **kwargs)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Document upload failed: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ReportViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer

