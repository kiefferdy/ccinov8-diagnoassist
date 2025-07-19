"""
Seed data for ICD-10 codes database
"""

from clinical_api.database.connection import execute_many
from clinical_api.database.models import table_has_data


def get_sample_data():
    """Get sample ICD-10 data for initialization"""
    return [
        # Infectious diseases (A00-B99)
        ("A00.0", "Cholera due to Vibrio cholerae 01, biovar cholerae", "Infectious diseases"),
        ("A00.1", "Cholera due to Vibrio cholerae 01, biovar eltor", "Infectious diseases"),
        ("A09", "Infectious gastroenteritis and colitis, unspecified", "Infectious diseases"),
        
        # Neoplasms (C00-D49)
        ("C78.2", "Secondary malignant neoplasm of pleura", "Neoplasms"),
        ("C80.1", "Malignant neoplasm, unspecified", "Neoplasms"),
        
        # Endocrine diseases (E00-E89)
        ("E10.9", "Type 1 diabetes mellitus without complications", "Endocrine diseases"),
        ("E11.9", "Type 2 diabetes mellitus without complications", "Endocrine diseases"),
        ("E78.5", "Hyperlipidemia, unspecified", "Endocrine diseases"),
        
        # Circulatory system (I00-I99)
        ("I10", "Essential (primary) hypertension", "Circulatory system"),
        ("I20.0", "Unstable angina", "Circulatory system"),
        ("I20.9", "Angina pectoris, unspecified", "Circulatory system"),
        ("I21.9", "Acute myocardial infarction, unspecified", "Circulatory system"),
        ("I25.10", "Atherosclerotic heart disease of native coronary artery without angina pectoris", "Circulatory system"),
        ("I50.9", "Heart failure, unspecified", "Circulatory system"),
        
        # Respiratory system (J00-J99)
        ("J00", "Acute nasopharyngitis [common cold]", "Respiratory system"),
        ("J06.9", "Acute upper respiratory infection, unspecified", "Respiratory system"),
        ("J18.9", "Pneumonia, unspecified organism", "Respiratory system"),
        ("J20.9", "Acute bronchitis, unspecified", "Respiratory system"),
        ("J44.1", "Chronic obstructive pulmonary disease with acute exacerbation", "Respiratory system"),
        ("J45.901", "Unspecified asthma with acute exacerbation", "Respiratory system"),
        
        # Digestive system (K00-K95)
        ("K21.9", "Gastro-esophageal reflux disease without esophagitis", "Digestive system"),
        ("K27.9", "Peptic ulcer, site unspecified, unspecified as acute or chronic", "Digestive system"),
        ("K37", "Unspecified appendicitis", "Digestive system"),
        ("K52.9", "Gastroenteritis and colitis, unspecified", "Digestive system"),
        ("K81.9", "Cholecystitis, unspecified", "Digestive system"),
        
        # Genitourinary system (N00-N99)
        ("N39.0", "Urinary tract infection, site not specified", "Genitourinary system"),
        
        # Musculoskeletal system (M00-M99)
        ("M25.50", "Pain in unspecified joint", "Musculoskeletal system"),
        ("M54.5", "Low back pain", "Musculoskeletal system"),
        ("M79.3", "Panniculitis, unspecified", "Musculoskeletal system"),
        ("M94.0", "Chondrocostal junction syndrome [Tietze]", "Musculoskeletal system"),
        
        # Mental disorders (F00-F99)
        ("F32.9", "Major depressive disorder, single episode, unspecified", "Mental disorders"),
        ("F41.0", "Panic disorder [episodic paroxysmal anxiety]", "Mental disorders"),
        ("F41.1", "Generalized anxiety disorder", "Mental disorders"),
        
        # Nervous system (G00-G99)
        ("G43.9", "Migraine, unspecified", "Nervous system"),
        ("G44.0", "Cluster headaches and other trigeminal autonomic cephalalgias", "Nervous system"),
        ("G44.2", "Tension-type headache", "Nervous system"),
        
        # Symptoms and signs (R00-R99)
        ("R05", "Cough", "Symptoms and signs"),
        ("R50.9", "Fever, unspecified", "Symptoms and signs"),
        ("R06.00", "Dyspnea, unspecified", "Symptoms and signs"),
        ("R10.9", "Unspecified abdominal pain", "Symptoms and signs"),
        ("R51", "Headache", "Symptoms and signs"),
        
        # External causes (V00-Y99)
        ("W19", "Unspecified fall", "External causes"),
        
        # COVID-19
        ("U07.1", "COVID-19", "Special purposes"),
        ("U09.9", "Post COVID-19 condition, unspecified", "Special purposes"),
    ]


def prepare_data_for_insert(sample_data):
    """Prepare data with search terms for database insertion"""
    prepared_data = []
    for code, description, category in sample_data:
        # Create search terms (lowercase, remove punctuation)
        search_terms = f"{code.lower()} {description.lower()}".replace(",", " ").replace(".", " ")
        prepared_data.append((code, description, category, search_terms))
    return prepared_data


def seed_database():
    """Seed the database with initial ICD-10 data if empty"""
    if not table_has_data("icd10_codes"):
        sample_data = get_sample_data()
        prepared_data = prepare_data_for_insert(sample_data)
        
        insert_query = """
            INSERT OR IGNORE INTO icd10_codes (code, description, category, search_terms) 
            VALUES (?, ?, ?, ?)
        """
        execute_many(insert_query, prepared_data)
        print(f"Seeded database with {len(prepared_data)} ICD-10 codes")