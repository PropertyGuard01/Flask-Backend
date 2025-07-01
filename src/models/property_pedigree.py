from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class PropertyPedigree(db.Model):
    """Comprehensive property pedigree model - the digital twin of a property"""
    __tablename__ = 'property_pedigrees'
    
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)
    
    # Basic Property Information
    erf_number = db.Column(db.String(50))
    street_address = db.Column(db.String(255))
    suburb = db.Column(db.String(100))
    city = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    province = db.Column(db.String(100))
    country = db.Column(db.String(100), default='South Africa')
    
    # Property Characteristics
    property_type = db.Column(db.String(50))  # House, Apartment, Townhouse, etc.
    stand_size = db.Column(db.Float)  # in square meters
    building_size = db.Column(db.Float)  # in square meters
    year_built = db.Column(db.Integer)
    architectural_style = db.Column(db.String(100))
    
    # Zoning and Legal
    zoning = db.Column(db.String(50))
    title_deed_number = db.Column(db.String(100))
    sectional_title_scheme = db.Column(db.String(100))  # For apartments/complexes
    
    # Municipal Information
    municipal_account_number = db.Column(db.String(50))
    rates_account_number = db.Column(db.String(50))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    property = db.relationship('Property', backref='pedigree')
    features = db.relationship('PropertyFeature', backref='pedigree', lazy='dynamic')
    valuations = db.relationship('PropertyValuation', backref='pedigree', lazy='dynamic')
    architectural_plans = db.relationship('ArchitecturalPlan', backref='pedigree', lazy='dynamic')
    maintenance_records = db.relationship('MaintenanceRecord', backref='pedigree', lazy='dynamic')
    improvements = db.relationship('PropertyImprovement', backref='pedigree', lazy='dynamic')

class PropertyFeature(db.Model):
    """Individual features and amenities within a property"""
    __tablename__ = 'property_features'
    
    id = db.Column(db.Integer, primary_key=True)
    pedigree_id = db.Column(db.Integer, db.ForeignKey('property_pedigrees.id'), nullable=False)
    
    # Feature Details
    category = db.Column(db.String(50), nullable=False)  # Fixture, Finish, System, Outdoor, etc.
    subcategory = db.Column(db.String(50))  # Electrical, Plumbing, HVAC, etc.
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    # Product Information
    brand = db.Column(db.String(100))
    model = db.Column(db.String(100))
    serial_number = db.Column(db.String(100))
    
    # Installation Details
    installation_date = db.Column(db.Date)
    installer_name = db.Column(db.String(100))
    installer_contact = db.Column(db.String(100))
    
    # Warranty Information
    warranty_period_months = db.Column(db.Integer)
    warranty_expiry_date = db.Column(db.Date)
    warranty_provider = db.Column(db.String(100))
    warranty_document_path = db.Column(db.String(255))
    
    # Financial
    purchase_price = db.Column(db.Numeric(12, 2))
    installation_cost = db.Column(db.Numeric(12, 2))
    
    # Status
    status = db.Column(db.String(20), default='Active')  # Active, Replaced, Removed
    condition = db.Column(db.String(20))  # Excellent, Good, Fair, Poor
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PropertyValuation(db.Model):
    """Track all types of property valuations over time"""
    __tablename__ = 'property_valuations'
    
    id = db.Column(db.Integer, primary_key=True)
    pedigree_id = db.Column(db.Integer, db.ForeignKey('property_pedigrees.id'), nullable=False)
    
    # Valuation Details
    valuation_type = db.Column(db.String(20), nullable=False)  # Bank, Municipal, Market, Insurance
    valuation_amount = db.Column(db.Numeric(15, 2), nullable=False)
    valuation_date = db.Column(db.Date, nullable=False)
    
    # Valuer Information
    valuer_name = db.Column(db.String(100))
    valuer_company = db.Column(db.String(100))
    valuer_registration = db.Column(db.String(50))
    
    # Purpose and Context
    valuation_purpose = db.Column(db.String(100))  # Mortgage, Sale, Insurance, Rates
    market_conditions = db.Column(db.Text)
    notes = db.Column(db.Text)
    
    # Documentation
    valuation_report_path = db.Column(db.String(255))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ArchitecturalPlan(db.Model):
    """Store and manage architectural plans and blueprints"""
    __tablename__ = 'architectural_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    pedigree_id = db.Column(db.Integer, db.ForeignKey('property_pedigrees.id'), nullable=False)
    
    # Plan Details
    plan_type = db.Column(db.String(50), nullable=False)  # Site Plan, Floor Plan, Electrical, Plumbing, etc.
    plan_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    # Version Control
    version = db.Column(db.String(20))
    revision_date = db.Column(db.Date)
    is_current = db.Column(db.Boolean, default=True)
    
    # Professional Details
    architect_name = db.Column(db.String(100))
    architect_firm = db.Column(db.String(100))
    architect_registration = db.Column(db.String(50))
    draughtsman_name = db.Column(db.String(100))
    
    # Approval Information
    council_approval_number = db.Column(db.String(50))
    approval_date = db.Column(db.Date)
    approval_expiry_date = db.Column(db.Date)
    
    # File Information
    file_path = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(10))  # PDF, DWG, JPG, etc.
    file_size = db.Column(db.Integer)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class MaintenanceRecord(db.Model):
    """Comprehensive maintenance history for the property"""
    __tablename__ = 'maintenance_records'
    
    id = db.Column(db.Integer, primary_key=True)
    pedigree_id = db.Column(db.Integer, db.ForeignKey('property_pedigrees.id'), nullable=False)
    feature_id = db.Column(db.Integer, db.ForeignKey('property_features.id'), nullable=True)
    
    # Maintenance Details
    maintenance_type = db.Column(db.String(20), nullable=False)  # Routine, Reactive, Preventive, Emergency
    category = db.Column(db.String(50))  # Electrical, Plumbing, HVAC, Structural, etc.
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    
    # Scheduling
    scheduled_date = db.Column(db.Date)
    completed_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='Scheduled')  # Scheduled, In Progress, Completed, Cancelled
    
    # Service Provider
    service_provider_name = db.Column(db.String(100))
    service_provider_contact = db.Column(db.String(100))
    service_provider_registration = db.Column(db.String(50))
    
    # Financial
    estimated_cost = db.Column(db.Numeric(10, 2))
    actual_cost = db.Column(db.Numeric(10, 2))
    invoice_number = db.Column(db.String(50))
    
    # Quality and Compliance
    warranty_period_months = db.Column(db.Integer)
    warranty_expiry_date = db.Column(db.Date)
    coc_required = db.Column(db.Boolean, default=False)
    coc_issued = db.Column(db.Boolean, default=False)
    coc_number = db.Column(db.String(50))
    
    # Documentation
    before_photos = db.Column(db.JSON)  # Array of file paths
    after_photos = db.Column(db.JSON)  # Array of file paths
    invoice_path = db.Column(db.String(255))
    warranty_document_path = db.Column(db.String(255))
    coc_document_path = db.Column(db.String(255))
    
    # Notes and Follow-up
    notes = db.Column(db.Text)
    next_maintenance_due = db.Column(db.Date)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    feature = db.relationship('PropertyFeature', backref='maintenance_records')

class PropertyImprovement(db.Model):
    """Track all improvements, renovations, and additions to the property"""
    __tablename__ = 'property_improvements'
    
    id = db.Column(db.Integer, primary_key=True)
    pedigree_id = db.Column(db.Integer, db.ForeignKey('property_pedigrees.id'), nullable=False)
    
    # Improvement Details
    improvement_type = db.Column(db.String(50), nullable=False)  # Addition, Renovation, Upgrade, etc.
    category = db.Column(db.String(50))  # Kitchen, Bathroom, Bedroom, Outdoor, etc.
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    
    # Project Timeline
    start_date = db.Column(db.Date)
    completion_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='Planned')  # Planned, In Progress, Completed, On Hold
    
    # Financial
    budgeted_cost = db.Column(db.Numeric(12, 2))
    actual_cost = db.Column(db.Numeric(12, 2))
    financing_method = db.Column(db.String(50))  # Cash, Loan, Credit, etc.
    
    # Professional Services
    architect_name = db.Column(db.String(100))
    contractor_name = db.Column(db.String(100))
    contractor_registration = db.Column(db.String(50))
    
    # Permits and Approvals
    permits_required = db.Column(db.Boolean, default=False)
    permits_obtained = db.Column(db.Boolean, default=False)
    permit_numbers = db.Column(db.JSON)  # Array of permit numbers
    council_approval_required = db.Column(db.Boolean, default=False)
    council_approval_obtained = db.Column(db.Boolean, default=False)
    
    # Value Impact
    estimated_value_increase = db.Column(db.Numeric(12, 2))
    actual_value_increase = db.Column(db.Numeric(12, 2))
    
    # Documentation
    before_photos = db.Column(db.JSON)  # Array of file paths
    progress_photos = db.Column(db.JSON)  # Array of file paths
    after_photos = db.Column(db.JSON)  # Array of file paths
    plans_document_path = db.Column(db.String(255))
    permits_document_path = db.Column(db.String(255))
    invoices_document_path = db.Column(db.JSON)  # Array of invoice file paths
    
    # Quality Assurance
    warranty_period_months = db.Column(db.Integer)
    warranty_expiry_date = db.Column(db.Date)
    final_inspection_date = db.Column(db.Date)
    final_inspection_passed = db.Column(db.Boolean)
    
    # Notes
    notes = db.Column(db.Text)
    lessons_learned = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AssetGrowthMetric(db.Model):
    """Track various metrics for asset growth analysis"""
    __tablename__ = 'asset_growth_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    pedigree_id = db.Column(db.Integer, db.ForeignKey('property_pedigrees.id'), nullable=False)
    
    # Metric Details
    metric_type = db.Column(db.String(50), nullable=False)  # Total Investment, Market Value, Rental Income, etc.
    metric_value = db.Column(db.Numeric(15, 2), nullable=False)
    metric_date = db.Column(db.Date, nullable=False)
    
    # Context
    calculation_method = db.Column(db.String(100))
    data_source = db.Column(db.String(100))
    notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Building Compliance Module Models

class BuildingProject(db.Model):
    """Manage building projects with compliance tracking"""
    __tablename__ = 'building_projects'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    pedigree_id = db.Column(db.Integer, db.ForeignKey('property_pedigrees.id'), nullable=True)
    
    # Project Details
    project_name = db.Column(db.String(100), nullable=False)
    project_type = db.Column(db.String(50), nullable=False)  # New Build, Renovation, Addition, etc.
    description = db.Column(db.Text)
    
    # Location (if not linked to existing property)
    erf_number = db.Column(db.String(50))
    street_address = db.Column(db.String(255))
    suburb = db.Column(db.String(100))
    city = db.Column(db.String(100))
    
    # Project Timeline
    planned_start_date = db.Column(db.Date)
    planned_completion_date = db.Column(db.Date)
    actual_start_date = db.Column(db.Date)
    actual_completion_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='Planning')  # Planning, Approved, In Progress, Completed, On Hold
    
    # Financial
    total_budget = db.Column(db.Numeric(15, 2))
    actual_cost = db.Column(db.Numeric(15, 2))
    
    # Compliance Status
    compliance_score = db.Column(db.Float, default=0.0)  # 0-100%
    all_permits_obtained = db.Column(db.Boolean, default=False)
    all_cocs_obtained = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    permits = db.relationship('BuildingPermit', backref='project', lazy='dynamic')
    inspections = db.relationship('BuildingInspection', backref='project', lazy='dynamic')
    compliance_items = db.relationship('ComplianceItem', backref='project', lazy='dynamic')

class BuildingPermit(db.Model):
    """Track building permits and approvals"""
    __tablename__ = 'building_permits'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('building_projects.id'), nullable=False)
    
    # Permit Details
    permit_type = db.Column(db.String(50), nullable=False)  # Building Plan, Demolition, Electrical, etc.
    permit_number = db.Column(db.String(50))
    description = db.Column(db.Text)
    
    # Authority
    issuing_authority = db.Column(db.String(100))  # Municipal Council, Provincial Dept, etc.
    authority_contact = db.Column(db.String(100))
    
    # Status and Dates
    application_date = db.Column(db.Date)
    approval_date = db.Column(db.Date)
    expiry_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='Required')  # Required, Applied, Approved, Expired, Rejected
    
    # Financial
    application_fee = db.Column(db.Numeric(8, 2))
    
    # Documentation
    application_document_path = db.Column(db.String(255))
    approval_document_path = db.Column(db.String(255))
    
    # Notes
    notes = db.Column(db.Text)
    rejection_reason = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class BuildingInspection(db.Model):
    """Track required inspections during construction"""
    __tablename__ = 'building_inspections'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('building_projects.id'), nullable=False)
    
    # Inspection Details
    inspection_type = db.Column(db.String(50), nullable=False)  # Foundation, Frame, Electrical, Final, etc.
    description = db.Column(db.Text)
    
    # Scheduling
    required_date = db.Column(db.Date)
    scheduled_date = db.Column(db.Date)
    completed_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='Required')  # Required, Scheduled, Passed, Failed, Rescheduled
    
    # Inspector Details
    inspector_name = db.Column(db.String(100))
    inspector_company = db.Column(db.String(100))
    inspector_registration = db.Column(db.String(50))
    inspector_contact = db.Column(db.String(100))
    
    # Results
    passed = db.Column(db.Boolean)
    findings = db.Column(db.Text)
    corrective_actions_required = db.Column(db.Text)
    
    # Documentation
    inspection_report_path = db.Column(db.String(255))
    photos_paths = db.Column(db.JSON)  # Array of photo file paths
    
    # Follow-up
    reinspection_required = db.Column(db.Boolean, default=False)
    reinspection_date = db.Column(db.Date)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ComplianceItem(db.Model):
    """Track specific compliance requirements and their status"""
    __tablename__ = 'compliance_items'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('building_projects.id'), nullable=False)
    
    # Compliance Details
    category = db.Column(db.String(50), nullable=False)  # Health & Safety, Building Code, Environmental, etc.
    requirement_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    legal_reference = db.Column(db.String(100))  # SANS standard, municipal bylaw, etc.
    
    # Status
    status = db.Column(db.String(20), default='Required')  # Required, In Progress, Compliant, Non-Compliant
    priority = db.Column(db.String(10), default='Medium')  # High, Medium, Low
    
    # Dates
    due_date = db.Column(db.Date)
    completion_date = db.Column(db.Date)
    
    # Responsible Party
    responsible_party = db.Column(db.String(100))  # Contractor, Owner, Architect, etc.
    assigned_to = db.Column(db.String(100))
    
    # Evidence and Documentation
    evidence_required = db.Column(db.Text)
    evidence_provided = db.Column(db.Text)
    document_paths = db.Column(db.JSON)  # Array of supporting document paths
    
    # Notes
    notes = db.Column(db.Text)
    non_compliance_reason = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

