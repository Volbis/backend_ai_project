from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Dossier, Document, Report
from .serializers import DossierSerializer, DocumentSerializer, ReportSerializer
from .services import DossierService

class DossierViewSet(viewsets.ModelViewSet):
    queryset = Dossier.objects.all()
    serializer_class = DossierSerializer

    @action(detail=True, methods=['post'])
    def analyze(self, request, pk=None):
        dossier = self.get_object()
        service = DossierService()
        # In a real app, this should be a background task (Celery)
        service.process_dossier(dossier.id)
        
        dossier.refresh_from_db()
        return Response({'status': dossier.status})

class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

class ReportViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer

