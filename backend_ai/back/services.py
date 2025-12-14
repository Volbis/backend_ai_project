from .models import Dossier, Document, Report
from ai_engine.pipeline import AIPipeline
from django.core.files.storage import default_storage
import os

class DossierService:
    def __init__(self):
        self.ai_pipeline = AIPipeline()

    def process_dossier(self, dossier_id: int):
        try:
            dossier = Dossier.objects.get(id=dossier_id)
            dossier.status = 'PROCESSING'
            dossier.save()

            # Aggregate results from all documents
            documents = dossier.documents.all()
            if not documents:
                dossier.status = 'ERROR'
                dossier.save()
                return

            # Simple aggregation logic for MVP
            combined_details = {}
            total_compliance = 0
            count = 0

            for doc in documents:
                file_path = doc.file.path
                # In a real scenario, we might need to handle storage backends (S3, etc.)
                # Here we assume local file system for MVP
                
                result = self.ai_pipeline.process_document(file_path)
                
                combined_details[doc.id] = {
                    "document_type": result.document_type,
                    "extracted_data": result.extracted_data,
                    "inconsistencies": result.inconsistencies,
                    "recommendations": result.recommendations
                }
                total_compliance += result.compliance_score
                count += 1

            avg_compliance = total_compliance / count if count > 0 else 0
            
            # Create Report
            Report.objects.create(
                dossier=dossier,
                compliance_score=avg_compliance,
                rejection_probability=1.0 - avg_compliance,
                details=combined_details
            )

            dossier.status = 'COMPLETED'
            dossier.save()

        except Exception as e:
            print(f"Error processing dossier {dossier_id}: {e}")
            dossier.status = 'ERROR'
            dossier.save()
