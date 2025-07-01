from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from enum import Enum
import json

db = SQLAlchemy()

class PropertyType(Enum):
    FREESTANDING_HOUSE = "freestanding_house"
    SECTIONAL_TITLE_APARTMENT = "sectional_title_apartment"
    SECTIONAL_TITLE_TOWNHOUSE = "sectional_title_townhouse"
    CLUSTER_HOME = "cluster_home"
    COMMERCIAL_OFFICE = "commercial_office"
    RETAIL_SPACE = "retail_space"
    SHOPPING_MALL = "shopping_mall"
    SCHOOL = "school"
    HOSPITAL = "hospital"
    INDUSTRIAL = "industrial"
    VACANT_LAND = "vacant_land"

class OwnershipType(Enum):
    INDIVIDUAL = "individual"
    SECTIONAL_TITLE = "sectional_title"
    SHARE_BLOCK = "share_block"
    COMPANY = "company"
    TRUST = "trust"
    BODY_CORPORATE = "body_corporate"

class FloorLevel(Enum):
    GROUND_FLOOR = "ground_floor"
    MIDDLE_FLOOR = "middle_floor"
    TOP_FLOOR = "top_floor"
    PENTHOUSE = "penthouse"
    BASEMENT = "basement"

class PropertyTypeDefinition(db.Model):
    __tablename__ = 'property_type_definitions'
    
    id = db.Column(db.Integer, primary_key=True)
    property_type = db.Column(db.Enum(PropertyType), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    # Compliance requirements as JSON
    compliance_requirements = db.Column(db.Text)  # JSON string
    
    # Insurance requirements as JSON
    insurance_requirements = db.Column(db.Text)  # JSON string
    
    # Maintenance requirements as JSON
    maintenance_requirements = db.Column(db.Text)  # JSON string
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_compliance_requirements(self):
        return json.loads(self.compliance_requirements) if self.compliance_requirements else {}
    
    def set_compliance_requirements(self, requirements):
        self.compliance_requirements = json.dumps(requirements)
    
    def get_insurance_requirements(self):
        return json.loads(self.insurance_requirements) if self.insurance_requirements else {}
    
    def set_insurance_requirements(self, requirements):
        self.insurance_requirements = json.dumps(requirements)
    
    def get_maintenance_requirements(self):
        return json.loads(self.maintenance_requirements) if self.maintenance_requirements else {}
    
    def set_maintenance_requirements(self, requirements):
        self.maintenance_requirements = json.dumps(requirements)

class EnhancedProperty(db.Model):
    __tablename__ = 'enhanced_properties'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    
    # Basic property information
    name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.Text, nullable=False)
    
    # Property classification
    property_type = db.Column(db.Enum(PropertyType), nullable=False)
    ownership_type = db.Column(db.Enum(OwnershipType), nullable=False)
    floor_level = db.Column(db.Enum(FloorLevel), nullable=True)
    
    # Council/Municipal data
    erf_number = db.Column(db.String(50))
    stand_number = db.Column(db.String(50))
    municipal_account_number = db.Column(db.String(100))
    zoning = db.Column(db.String(50))
    
    # Property characteristics
    floor_area = db.Column(db.Float)  # Square meters
    land_area = db.Column(db.Float)  # Square meters
    year_built = db.Column(db.Integer)
    number_of_bedrooms = db.Column(db.Integer)
    number_of_bathrooms = db.Column(db.Integer)
    
    # Sectional title specific
    unit_number = db.Column(db.String(20))
    body_corporate_name = db.Column(db.String(200))
    levy_amount = db.Column(db.Float)
    
    # Documentation completeness tracking
    documentation_score = db.Column(db.Float, default=0.0)  # 0-100%
    council_data_imported = db.Column(db.Boolean, default=False)
    council_data_import_date = db.Column(db.DateTime)
    
    # Property status
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    compliance_items = db.relationship('ComplianceItem', backref='property', lazy=True, cascade='all, delete-orphan')
    shared_responsibilities = db.relationship('SharedResponsibility', backref='property', lazy=True, cascade='all, delete-orphan')
    council_documents = db.relationship('CouncilDocument', backref='property', lazy=True, cascade='all, delete-orphan')

class ComplianceItem(db.Model):
    __tablename__ = 'compliance_items'
    
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('enhanced_properties.id'), nullable=False)
    
    # Compliance details
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100))  # electrical, plumbing, structural, etc.
    
    # Responsibility tracking
    is_individual_responsibility = db.Column(db.Boolean, default=True)
    responsible_party = db.Column(db.String(200))  # "Owner", "Body Corporate", "HOA", etc.
    
    # Status and dates
    is_required = db.Column(db.Boolean, default=True)
    is_compliant = db.Column(db.Boolean, default=False)
    due_date = db.Column(db.DateTime)
    last_inspection_date = db.Column(db.DateTime)
    next_inspection_date = db.Column(db.DateTime)
    
    # Documentation
    certificate_number = db.Column(db.String(100))
    issuing_authority = db.Column(db.String(200))
    document_path = db.Column(db.String(500))
    
    # Tracking
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SharedResponsibility(db.Model):
    __tablename__ = 'shared_responsibilities'
    
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('enhanced_properties.id'), nullable=False)
    
    # Responsibility details
    area_or_system = db.Column(db.String(200), nullable=False)  # "Roof", "Common Areas", "Lifts", etc.
    description = db.Column(db.Text)
    
    # Responsibility allocation
    individual_percentage = db.Column(db.Float, default=0.0)  # 0-100%
    body_corporate_percentage = db.Column(db.Float, default=0.0)  # 0-100%
    hoa_percentage = db.Column(db.Float, default=0.0)  # 0-100%
    
    # Insurance and maintenance
    insurance_provider = db.Column(db.String(200))
    maintenance_schedule = db.Column(db.String(200))
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CouncilDocument(db.Model):
    __tablename__ = 'council_documents'
    
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('enhanced_properties.id'), nullable=False)
    
    # Document details
    document_type = db.Column(db.String(100), nullable=False)  # "Building Plan", "Stand Plan", "COC", etc.
    document_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # Council information
    municipality = db.Column(db.String(200))
    reference_number = db.Column(db.String(100))
    approval_date = db.Column(db.DateTime)
    
    # File information
    file_path = db.Column(db.String(500))
    file_size = db.Column(db.Integer)
    file_type = db.Column(db.String(50))
    
    # Import tracking
    import_method = db.Column(db.String(50))  # "manual", "api", "scraping"
    import_date = db.Column(db.DateTime, default=datetime.utcnow)
    verified = db.Column(db.Boolean, default=False)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PropertyDocumentationGap(db.Model):
    __tablename__ = 'property_documentation_gaps'
    
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('enhanced_properties.id'), nullable=False)
    
    # Gap details
    gap_type = db.Column(db.String(100), nullable=False)  # "missing_coc", "expired_warranty", etc.
    description = db.Column(db.Text, nullable=False)
    severity = db.Column(db.String(20), default='medium')  # low, medium, high, critical
    
    # Resolution tracking
    is_resolved = db.Column(db.Boolean, default=False)
    resolution_date = db.Column(db.DateTime)
    resolution_notes = db.Column(db.Text)
    
    # Cost implications
    estimated_cost_to_resolve = db.Column(db.Float)
    actual_cost_to_resolve = db.Column(db.Float)
    
    # Tracking
    identified_date = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class MunicipalityIntegration(db.Model):
    __tablename__ = 'municipality_integrations'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Municipality details
    municipality_name = db.Column(db.String(200), nullable=False, unique=True)
    province = db.Column(db.String(100))
    contact_email = db.Column(db.String(200))
    contact_phone = db.Column(db.String(50))
    
    # Integration capabilities
    has_api_access = db.Column(db.Boolean, default=False)
    api_endpoint = db.Column(db.String(500))
    api_key_required = db.Column(db.Boolean, default=False)
    
    # Data availability
    has_building_plans = db.Column(db.Boolean, default=False)
    has_stand_plans = db.Column(db.Boolean, default=False)
    has_coc_records = db.Column(db.Boolean, default=False)
    has_rates_data = db.Column(db.Boolean, default=False)
    has_zoning_data = db.Column(db.Boolean, default=False)
    
    # Integration status
    integration_status = db.Column(db.String(50), default='not_integrated')  # not_integrated, manual, semi_automated, fully_automated
    last_sync_date = db.Column(db.DateTime)
    
    # Tracking
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Helper functions for property type logic
def get_applicable_compliance_items(property_type, ownership_type, floor_level=None):
    """
    Returns a list of compliance items applicable to a specific property configuration
    """
    base_requirements = []
    
    if property_type == PropertyType.FREESTANDING_HOUSE:
        base_requirements = [
            {'name': 'Electrical COC', 'category': 'electrical', 'individual_responsibility': True},
            {'name': 'Plumbing COC', 'category': 'plumbing', 'individual_responsibility': True},
            {'name': 'Gas COC', 'category': 'gas', 'individual_responsibility': True},
            {'name': 'Roof Inspection', 'category': 'structural', 'individual_responsibility': True},
            {'name': 'Pool COC', 'category': 'safety', 'individual_responsibility': True},
        ]
    
    elif property_type in [PropertyType.SECTIONAL_TITLE_APARTMENT, PropertyType.SECTIONAL_TITLE_TOWNHOUSE]:
        base_requirements = [
            {'name': 'Unit Electrical COC', 'category': 'electrical', 'individual_responsibility': True},
            {'name': 'Unit Plumbing COC', 'category': 'plumbing', 'individual_responsibility': True},
            {'name': 'Common Area Electrical', 'category': 'electrical', 'individual_responsibility': False},
            {'name': 'Building Structural', 'category': 'structural', 'individual_responsibility': False},
        ]
        
        # Floor-specific requirements
        if floor_level == FloorLevel.TOP_FLOOR:
            base_requirements.append({
                'name': 'Roof Access COC', 
                'category': 'structural', 
                'individual_responsibility': True
            })
        elif floor_level == FloorLevel.GROUND_FLOOR:
            base_requirements.append({
                'name': 'Foundation Inspection', 
                'category': 'structural', 
                'individual_responsibility': False
            })
    
    elif property_type == PropertyType.COMMERCIAL_OFFICE:
        base_requirements = [
            {'name': 'Fire Safety COC', 'category': 'safety', 'individual_responsibility': True},
            {'name': 'Occupancy Certificate', 'category': 'legal', 'individual_responsibility': True},
            {'name': 'HVAC System COC', 'category': 'mechanical', 'individual_responsibility': True},
            {'name': 'Accessibility Compliance', 'category': 'accessibility', 'individual_responsibility': True},
        ]
    
    elif property_type == PropertyType.SCHOOL:
        base_requirements = [
            {'name': 'Fire Safety COC', 'category': 'safety', 'individual_responsibility': True},
            {'name': 'Playground Safety', 'category': 'safety', 'individual_responsibility': True},
            {'name': 'Food Service COC', 'category': 'health', 'individual_responsibility': True},
            {'name': 'Transportation Safety', 'category': 'safety', 'individual_responsibility': True},
            {'name': 'Accessibility Compliance', 'category': 'accessibility', 'individual_responsibility': True},
        ]
    
    elif property_type == PropertyType.HOSPITAL:
        base_requirements = [
            {'name': 'Medical Gas Systems', 'category': 'medical', 'individual_responsibility': True},
            {'name': 'Emergency Power Systems', 'category': 'electrical', 'individual_responsibility': True},
            {'name': 'Infection Control Systems', 'category': 'health', 'individual_responsibility': True},
            {'name': 'Waste Management COC', 'category': 'environmental', 'individual_responsibility': True},
            {'name': 'Radiation Safety', 'category': 'safety', 'individual_responsibility': True},
        ]
    
    return base_requirements

def calculate_documentation_score(property_id):
    """
    Calculates the documentation completeness score for a property
    """
    property_obj = EnhancedProperty.query.get(property_id)
    if not property_obj:
        return 0.0
    
    # Get required compliance items
    required_items = get_applicable_compliance_items(
        property_obj.property_type, 
        property_obj.ownership_type, 
        property_obj.floor_level
    )
    
    if not required_items:
        return 100.0
    
    # Count compliant items
    compliant_count = ComplianceItem.query.filter_by(
        property_id=property_id,
        is_compliant=True
    ).count()
    
    # Calculate score
    score = (compliant_count / len(required_items)) * 100
    
    # Update property score
    property_obj.documentation_score = score
    db.session.commit()
    
    return score

def identify_documentation_gaps(property_id):
    """
    Identifies and records documentation gaps for a property
    """
    property_obj = EnhancedProperty.query.get(property_id)
    if not property_obj:
        return []
    
    # Get required compliance items
    required_items = get_applicable_compliance_items(
        property_obj.property_type, 
        property_obj.ownership_type, 
        property_obj.floor_level
    )
    
    # Get existing compliance items
    existing_items = ComplianceItem.query.filter_by(property_id=property_id).all()
    existing_names = [item.name for item in existing_items]
    
    gaps = []
    for required_item in required_items:
        if required_item['name'] not in existing_names:
            gap = PropertyDocumentationGap(
                property_id=property_id,
                gap_type='missing_compliance',
                description=f"Missing {required_item['name']} for {required_item['category']} compliance",
                severity='high' if required_item['individual_responsibility'] else 'medium'
            )
            gaps.append(gap)
    
    # Save gaps to database
    for gap in gaps:
        db.session.add(gap)
    db.session.commit()
    
    return gaps

