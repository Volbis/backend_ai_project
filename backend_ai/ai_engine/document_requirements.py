# Document requirements configuration
# Define what documents are required for different types of applications

DOCUMENT_REQUIREMENTS = {
    'student_visa': {
        'required': [
            'ID_Card',
            'Academic_Transcript',
            'Birth_Certificate',
            'Proof_of_Residence'
        ],
        'optional': [
            'Passport',
            'Photo'
        ]
    },
    'work_permit': {
        'required': [
            'ID_Card',
            'Birth_Certificate',
            'Proof_of_Residence'
        ],
        'optional': [
            'Academic_Transcript'
        ]
    },
    'residence_permit': {
        'required': [
            'ID_Card',
            'Proof_of_Residence',
            'Birth_Certificate'
        ],
        'optional': [
            'Passport'
        ]
    },
    'general': {
        'required': [
            'ID_Card'
        ],
        'optional': []
    }
}


def get_required_documents(application_type: str = 'general') -> dict:
    """
    Get the required and optional documents for an application type
    
    Args:
        application_type: Type of application (student_visa, work_permit, etc.)
    
    Returns:
        Dictionary with 'required' and 'optional' document lists
    """
    return DOCUMENT_REQUIREMENTS.get(application_type, DOCUMENT_REQUIREMENTS['general'])


def check_missing_documents(submitted_docs: list, application_type: str = 'general') -> list:
    """
    Check which required documents are missing
    
    Args:
        submitted_docs: List of document types that were submitted
        application_type: Type of application
    
    Returns:
        List of missing required document types
    """
    requirements = get_required_documents(application_type)
    required_docs = set(requirements['required'])
    submitted_set = set(submitted_docs)
    
    missing = list(required_docs - submitted_set)
    return missing
