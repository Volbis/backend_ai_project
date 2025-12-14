from rest_framework import serializers
from .models import Dossier, Document, Report

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = '__all__'

class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = '__all__'

class DossierSerializer(serializers.ModelSerializer):
    documents = DocumentSerializer(many=True, read_only=True)
    report = ReportSerializer(read_only=True)

    class Meta:
        model = Dossier
        fields = '__all__'
