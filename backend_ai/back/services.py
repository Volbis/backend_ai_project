from .models import Dossier, Document, Report
from ai_engine.pipeline import AIPipeline
from ai_engine.utils import pdf_to_images, preprocess_image
from ai_engine.document_requirements import check_missing_documents
from django.core.files.storage import default_storage
import os
import logging

logger = logging.getLogger('ai_engine')

class DossierService: 
    def __init__(self):
        self.ai_pipeline = AIPipeline()
 
    def process_dossier(self, dossier_id: int):
        try:
            dossier = Dossier.objects.get(id=dossier_id)
            dossier.status = 'PROCESSING'
            dossier.save()
            
            logger.info(f"Processing dossier {dossier_id}")

            # Aggregate results from all documents
            documents = dossier.documents.all()
            if not documents:
                logger.warning(f"No documents found for dossier {dossier_id}")
                dossier.status = 'ERROR'
                dossier.save()
                return

            # Simple aggregation logic for MVP
            combined_details = {}
            total_compliance = 0 
            count = 0
            detected_doc_types = []  # Track detected document types

            for doc in documents:
                file_path = doc.file.path
                logger.info(f"Processing document {doc.id}: {file_path}")
                
                # Handle PDF files - convert to images
                files_to_process = []
                if file_path.lower().endswith('.pdf'):
                    temp_dir = os.path.join(os.path.dirname(file_path), 'temp')
                    os.makedirs(temp_dir, exist_ok=True)
                    files_to_process = pdf_to_images(file_path, temp_dir)
                else:
                    # Preprocess image
                    file_path = preprocess_image(file_path)
                    files_to_process = [file_path]
                
                # Process each page/image
                for img_path in files_to_process:
                    # TODO: Get application_type from dossier metadata if available
                    result = self.ai_pipeline.process_document(img_path, application_type='general')
                    
                    # Track document types
                    if result.document_type not in ['Unknown', 'error']:
                        detected_doc_types.append(result.document_type)
                    
                    combined_details[f"{doc.id}_{os.path.basename(img_path)}"] = {
                        "document_type": result.document_type,
                        "extracted_data": result.extracted_data,
                        "inconsistencies": result.inconsistencies,
                        "recommendations": result.recommendations
                    }
                    total_compliance += result.compliance_score
                    count += 1

            avg_compliance = total_compliance / count if count > 0 else 0
            
            # Check for missing documents
            missing_docs = check_missing_documents(detected_doc_types, application_type='general')
            
            logger.info(f"Dossier {dossier_id} analysis complete. Compliance: {avg_compliance:.2f}")
            if missing_docs:
                logger.info(f"Missing documents: {', '.join(missing_docs)}")
            
            # Create Report
            Report.objects.create(
                dossier=dossier,
                compliance_score=avg_compliance,
                rejection_probability=1.0 - avg_compliance,
                details={
                    'documents': combined_details,
                    'missing_documents': missing_docs,
                    'detected_types': detected_doc_types
                })

        except Exception as e:
            logger.error(f"Error processing dossier {dossier_id}: {e}", exc_info=True)
            dossier.status = 'ERROR'
            dossier.save()
