from django.db import models
from django.contrib.auth.models import User

class Dossier(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'En attente'),
        ('PROCESSING', 'Analyse en cours'),
        ('COMPLETED', 'Terminé'),
        ('ERROR', 'Erreur'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    reference_number = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    def __str__(self):
        return f"Dossier {self.reference_number}"

class Document(models.Model):
    dossier = models.ForeignKey(Dossier, related_name='documents', on_delete=models.CASCADE)
    file = models.FileField(upload_to='documents/')
    document_type = models.CharField(max_length=50, blank=True) # e.g., "ID Card", "Transcript"
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.document_type} for {self.dossier.reference_number}"

class Report(models.Model):
    dossier = models.OneToOneField(Dossier, related_name='report', on_delete=models.CASCADE)
    generated_at = models.DateTimeField(auto_now_add=True)
    compliance_score = models.FloatField(default=0.0)
    rejection_probability = models.FloatField(default=0.0)
    details = models.JSONField(default=dict) # Stores the full analysis result
    
    def __str__(self):
        return f"Report for {self.dossier.reference_number}"
