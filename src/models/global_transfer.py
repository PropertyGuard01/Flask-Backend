from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from src.models.user import db
import json

class Region(db.Model):
    """Represents different geographical regions with their specific requirements"""
    id = db.Column(db.Integer, primary_key=True)
    region_code = db.Column(db.String(10), unique=True, nullable=False)  # ZA, US, UK, AU, etc.
    region_name = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    
    # Regional specifics
    currency_code = db.Column(db.String(3), nullable=False)  # ZAR, USD, GBP, etc.
    language_code = db.Column(db.String(5), default='en')  # en, af, zu, etc.
    timezone = db.Column(db.String(50))  # Africa/Johannesburg, etc.
    
    # Regulatory framework
    primary_building_code = db.Column(db.String(100))  # SANS, IBC, Building Regulations, etc.
    regulatory_authority = db.Column(db.String(200))  # SABS, Local Council, etc.
    insurance_regulator = db.Column(db.String(200))  # FSB, FCA, etc.
    
    # Standards and compliance
    electrical_standard = db.Column(db.String(100))  # SANS 10142, BS 7671, NEC, etc.
    plumbing_standard = db.Column(db.String(100))
    structural_standard = db.Column(db.String(100))
    fire_safety_standard = db.Column(db.String(100))
    
    # Professional requirements
    engineer_registration_body = db.Column(db.String(200))  # ECSA, ICE, etc.
    contractor_licensing_body = db.Column(db.String(200))
    inspector_certification_body = db.Column(db.String(200))
    
    # Insurance specifics
    mandatory_insurance_types = db.Column(db.Text)  # JSON list
    typical_coverage_amounts = db.Column(db.Text)  # JSON object
    common_exclusions = db.Column(db.Text)  # JSON list
    
    # Documentation requirements
    required_certificates = db.Column(db.Text)  # JSON list of required certificates
    certificate_validity_periods = db.Column(db.Text)  # JSON object with validity periods
    renewal_processes = db.Column(db.Text)  # JSON object with renewal procedures
    
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    properties = db.relationship('Property', backref='region', lazy=True)
    regional_standards = db.relationship('RegionalStandard', backref='region', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'region_code': self.region_code,
            'region_name': self.region_name,
            'country': self.country,
            'currency_code': self.currency_code,
            'language_code': self.language_code,
            'timezone': self.timezone,
            'primary_building_code': self.primary_building_code,
            'regulatory_authority': self.regulatory_authority,
            'insurance_regulator': self.insurance_regulator,
            'electrical_standard': self.electrical_standard,
            'plumbing_standard': self.plumbing_standard,
            'structural_standard': self.structural_standard,
            'fire_safety_standard': self.fire_safety_standard,
            'engineer_registration_body': self.engineer_registration_body,
            'contractor_licensing_body': self.contractor_licensing_body,
            'inspector_certification_body': self.inspector_certification_body,
            'mandatory_insurance_types': json.loads(self.mandatory_insurance_types) if self.mandatory_insurance_types else None,
            'typical_coverage_amounts': json.loads(self.typical_coverage_amounts) if self.typical_coverage_amounts else None,
            'common_exclusions': json.loads(self.common_exclusions) if self.common_exclusions else None,
            'required_certificates': json.loads(self.required_certificates) if self.required_certificates else None,
            'certificate_validity_periods': json.loads(self.certificate_validity_periods) if self.certificate_validity_periods else None,
            'renewal_processes': json.loads(self.renewal_processes) if self.renewal_processes else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class RegionalStandard(db.Model):
    """Regional variations of standards and regulations"""
    id = db.Column(db.Integer, primary_key=True)
    region_id = db.Column(db.Integer, db.ForeignKey('region.id'), nullable=False)
    standard_code = db.Column(db.String(100), nullable=False)
    standard_name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100))
    
    # Regional specifics
    local_equivalent = db.Column(db.String(100))  # Local standard that maps to international
    adoption_status = db.Column(db.String(50))  # Adopted, Modified, Not Applicable
    local_modifications = db.Column(db.Text)  # JSON list of local modifications
    
    # Implementation details
    enforcement_level = db.Column(db.String(50))  # Mandatory, Recommended, Voluntary
    inspection_frequency = db.Column(db.String(50))  # Annual, Bi-annual, One-time
    certification_required = db.Column(db.Boolean, default=False)
    professional_sign_off_required = db.Column(db.Boolean, default=False)
    
    # Version management
    current_version = db.Column(db.String(50))
    effective_date = db.Column(db.Date)
    superseded_date = db.Column(db.Date)
    transition_period_end = db.Column(db.Date)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'region_id': self.region_id,
            'standard_code': self.standard_code,
            'standard_name': self.standard_name,
            'category': self.category,
            'local_equivalent': self.local_equivalent,
            'adoption_status': self.adoption_status,
            'local_modifications': json.loads(self.local_modifications) if self.local_modifications else None,
            'enforcement_level': self.enforcement_level,
            'inspection_frequency': self.inspection_frequency,
            'certification_required': self.certification_required,
            'professional_sign_off_required': self.professional_sign_off_required,
            'current_version': self.current_version,
            'effective_date': self.effective_date.isoformat() if self.effective_date else None,
            'superseded_date': self.superseded_date.isoformat() if self.superseded_date else None,
            'transition_period_end': self.transition_period_end.isoformat() if self.transition_period_end else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class PropertyTransfer(db.Model):
    """Manages property ownership transfers and documentation handover"""
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    
    # Transfer parties
    current_owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    new_owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    new_owner_email = db.Column(db.String(120))  # For inviting new users
    
    # Transfer details
    transfer_type = db.Column(db.String(50), nullable=False)  # Sale, Inheritance, Gift, etc.
    transfer_date = db.Column(db.Date)
    sale_price = db.Column(db.Float)
    transfer_reference = db.Column(db.String(100))  # Deed reference, etc.
    
    # Legal and professional parties
    conveyancer_name = db.Column(db.String(200))
    conveyancer_contact = db.Column(db.String(200))
    estate_agent_name = db.Column(db.String(200))
    estate_agent_contact = db.Column(db.String(200))
    
    # Documentation status
    property_file_complete = db.Column(db.Boolean, default=False)
    documentation_score = db.Column(db.Float)  # 0-100% completeness
    missing_documents = db.Column(db.Text)  # JSON list of missing items
    outstanding_issues = db.Column(db.Text)  # JSON list of issues to resolve
    
    # Risk assessment
    compliance_gaps_identified = db.Column(db.Text)  # JSON list of compliance gaps
    estimated_rectification_cost = db.Column(db.Float)
    risk_level = db.Column(db.String(50))  # Low, Medium, High, Critical
    
    # Transfer process
    transfer_status = db.Column(db.String(50), default='Initiated')  # Initiated, In Progress, Completed, Cancelled
    documentation_handover_date = db.Column(db.Date)
    system_access_transferred = db.Column(db.Boolean, default=False)
    warranties_transferred = db.Column(db.Boolean, default=False)
    
    # Notifications and communications
    current_owner_notified = db.Column(db.Boolean, default=False)
    new_owner_invited = db.Column(db.Boolean, default=False)
    contractors_notified = db.Column(db.Boolean, default=False)
    insurers_notified = db.Column(db.Boolean, default=False)
    
    # Handover checklist
    handover_checklist = db.Column(db.Text)  # JSON checklist of items to transfer
    handover_notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # Relationships
    transfer_items = db.relationship('TransferItem', backref='transfer', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'property_id': self.property_id,
            'current_owner_id': self.current_owner_id,
            'new_owner_id': self.new_owner_id,
            'new_owner_email': self.new_owner_email,
            'transfer_type': self.transfer_type,
            'transfer_date': self.transfer_date.isoformat() if self.transfer_date else None,
            'sale_price': self.sale_price,
            'transfer_reference': self.transfer_reference,
            'conveyancer_name': self.conveyancer_name,
            'conveyancer_contact': self.conveyancer_contact,
            'estate_agent_name': self.estate_agent_name,
            'estate_agent_contact': self.estate_agent_contact,
            'property_file_complete': self.property_file_complete,
            'documentation_score': self.documentation_score,
            'missing_documents': json.loads(self.missing_documents) if self.missing_documents else None,
            'outstanding_issues': json.loads(self.outstanding_issues) if self.outstanding_issues else None,
            'compliance_gaps_identified': json.loads(self.compliance_gaps_identified) if self.compliance_gaps_identified else None,
            'estimated_rectification_cost': self.estimated_rectification_cost,
            'risk_level': self.risk_level,
            'transfer_status': self.transfer_status,
            'documentation_handover_date': self.documentation_handover_date.isoformat() if self.documentation_handover_date else None,
            'system_access_transferred': self.system_access_transferred,
            'warranties_transferred': self.warranties_transferred,
            'current_owner_notified': self.current_owner_notified,
            'new_owner_invited': self.new_owner_invited,
            'contractors_notified': self.contractors_notified,
            'insurers_notified': self.insurers_notified,
            'handover_checklist': json.loads(self.handover_checklist) if self.handover_checklist else None,
            'handover_notes': self.handover_notes,
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

class TransferItem(db.Model):
    """Individual items being transferred during property ownership change"""
    id = db.Column(db.Integer, primary_key=True)
    transfer_id = db.Column(db.Integer, db.ForeignKey('property_transfer.id'), nullable=False)
    
    # Item details
    item_type = db.Column(db.String(100), nullable=False)  # Document, Warranty, Contact, Key, etc.
    item_description = db.Column(db.String(500), nullable=False)
    category = db.Column(db.String(100))  # Legal, Technical, Maintenance, etc.
    
    # Transfer status
    transfer_status = db.Column(db.String(50), default='Pending')  # Pending, Transferred, Not Applicable
    transfer_date = db.Column(db.Date)
    transferred_by = db.Column(db.String(200))
    received_by = db.Column(db.String(200))
    
    # Item specifics
    document_id = db.Column(db.Integer, db.ForeignKey('document.id'))  # If it's a document
    warranty_id = db.Column(db.Integer, db.ForeignKey('warranty.id'))  # If it's a warranty
    contractor_id = db.Column(db.Integer, db.ForeignKey('contractor.id'))  # If it's a contractor contact
    
    # Transfer notes
    condition_notes = db.Column(db.Text)  # Condition of item being transferred
    special_instructions = db.Column(db.Text)
    new_owner_action_required = db.Column(db.Text)  # What new owner needs to do
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'transfer_id': self.transfer_id,
            'item_type': self.item_type,
            'item_description': self.item_description,
            'category': self.category,
            'transfer_status': self.transfer_status,
            'transfer_date': self.transfer_date.isoformat() if self.transfer_date else None,
            'transferred_by': self.transferred_by,
            'received_by': self.received_by,
            'document_id': self.document_id,
            'warranty_id': self.warranty_id,
            'contractor_id': self.contractor_id,
            'condition_notes': self.condition_notes,
            'special_instructions': self.special_instructions,
            'new_owner_action_required': self.new_owner_action_required,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class PropertyServiceHistory(db.Model):
    """Complete service history for a property - like a vehicle service manual"""
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    
    # Service/maintenance event
    service_date = db.Column(db.Date, nullable=False)
    service_type = db.Column(db.String(100), nullable=False)  # Maintenance, Repair, Upgrade, Inspection
    category = db.Column(db.String(100), nullable=False)  # Electrical, Plumbing, HVAC, Structural, etc.
    description = db.Column(db.Text, nullable=False)
    
    # Service provider
    service_provider_name = db.Column(db.String(200))
    service_provider_contact = db.Column(db.String(200))
    service_provider_license = db.Column(db.String(100))
    contractor_id = db.Column(db.Integer, db.ForeignKey('contractor.id'))
    
    # Work details
    work_performed = db.Column(db.Text)  # Detailed description of work
    materials_used = db.Column(db.Text)  # JSON list of materials and specifications
    standards_followed = db.Column(db.Text)  # JSON list of standards/codes followed
    
    # Documentation
    before_photos = db.Column(db.Text)  # JSON list of photo paths
    after_photos = db.Column(db.Text)  # JSON list of photo paths
    certificates_issued = db.Column(db.Text)  # JSON list of certificates/COCs
    warranty_provided = db.Column(db.Text)  # Warranty details
    
    # Costs and scheduling
    cost = db.Column(db.Float)
    scheduled_maintenance = db.Column(db.Boolean, default=False)  # Was this scheduled or emergency?
    next_service_due = db.Column(db.Date)  # When next service is due
    
    # Quality and compliance
    quality_rating = db.Column(db.Float)  # 1-5 star rating
    compliance_verified = db.Column(db.Boolean, default=False)
    inspection_passed = db.Column(db.Boolean, default=True)
    issues_identified = db.Column(db.Text)  # Any issues found during service
    
    # Impact on property
    property_value_impact = db.Column(db.Float)  # Estimated impact on property value
    warranty_status_changed = db.Column(db.Boolean, default=False)
    insurance_notification_required = db.Column(db.Boolean, default=False)
    
    # Record keeping
    recorded_by = db.Column(db.String(200))  # Who recorded this entry
    verified_by = db.Column(db.String(200))  # Who verified the work
    document_references = db.Column(db.Text)  # JSON list of related document IDs
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'property_id': self.property_id,
            'service_date': self.service_date.isoformat(),
            'service_type': self.service_type,
            'category': self.category,
            'description': self.description,
            'service_provider_name': self.service_provider_name,
            'service_provider_contact': self.service_provider_contact,
            'service_provider_license': self.service_provider_license,
            'contractor_id': self.contractor_id,
            'work_performed': self.work_performed,
            'materials_used': json.loads(self.materials_used) if self.materials_used else None,
            'standards_followed': json.loads(self.standards_followed) if self.standards_followed else None,
            'before_photos': json.loads(self.before_photos) if self.before_photos else None,
            'after_photos': json.loads(self.after_photos) if self.after_photos else None,
            'certificates_issued': json.loads(self.certificates_issued) if self.certificates_issued else None,
            'warranty_provided': self.warranty_provided,
            'cost': self.cost,
            'scheduled_maintenance': self.scheduled_maintenance,
            'next_service_due': self.next_service_due.isoformat() if self.next_service_due else None,
            'quality_rating': self.quality_rating,
            'compliance_verified': self.compliance_verified,
            'inspection_passed': self.inspection_passed,
            'issues_identified': self.issues_identified,
            'property_value_impact': self.property_value_impact,
            'warranty_status_changed': self.warranty_status_changed,
            'insurance_notification_required': self.insurance_notification_required,
            'recorded_by': self.recorded_by,
            'verified_by': self.verified_by,
            'document_references': json.loads(self.document_references) if self.document_references else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class GapInsuranceProduct(db.Model):
    """Insurance products that cover documentation and compliance gaps"""
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(200), nullable=False)
    insurer_name = db.Column(db.String(200), nullable=False)
    product_type = db.Column(db.String(100), nullable=False)  # Gap Coverage, Unknown Risk, Documentation Protection
    
    # Coverage details
    coverage_description = db.Column(db.Text)
    maximum_coverage_amount = db.Column(db.Float)
    deductible_amount = db.Column(db.Float)
    coverage_period_months = db.Column(db.Integer)
    
    # Eligibility and pricing
    minimum_documentation_score = db.Column(db.Float)  # Minimum score to qualify
    base_premium_rate = db.Column(db.Float)  # Base rate per R1000 coverage
    risk_multipliers = db.Column(db.Text)  # JSON object with risk-based multipliers
    
    # Coverage specifics
    covered_gap_types = db.Column(db.Text)  # JSON list of gap types covered
    exclusions = db.Column(db.Text)  # JSON list of exclusions
    claim_process = db.Column(db.Text)  # Description of claim process
    
    # Requirements
    inspection_required = db.Column(db.Boolean, default=False)
    professional_assessment_required = db.Column(db.Boolean, default=False)
    documentation_improvement_required = db.Column(db.Boolean, default=False)
    
    # Regional availability
    available_regions = db.Column(db.Text)  # JSON list of region codes
    regulatory_approval = db.Column(db.String(100))  # Regulatory approval status
    
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'product_name': self.product_name,
            'insurer_name': self.insurer_name,
            'product_type': self.product_type,
            'coverage_description': self.coverage_description,
            'maximum_coverage_amount': self.maximum_coverage_amount,
            'deductible_amount': self.deductible_amount,
            'coverage_period_months': self.coverage_period_months,
            'minimum_documentation_score': self.minimum_documentation_score,
            'base_premium_rate': self.base_premium_rate,
            'risk_multipliers': json.loads(self.risk_multipliers) if self.risk_multipliers else None,
            'covered_gap_types': json.loads(self.covered_gap_types) if self.covered_gap_types else None,
            'exclusions': json.loads(self.exclusions) if self.exclusions else None,
            'claim_process': self.claim_process,
            'inspection_required': self.inspection_required,
            'professional_assessment_required': self.professional_assessment_required,
            'documentation_improvement_required': self.documentation_improvement_required,
            'available_regions': json.loads(self.available_regions) if self.available_regions else None,
            'regulatory_approval': self.regulatory_approval,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class PropertyRiskAssessment(db.Model):
    """Comprehensive risk assessment for property transactions"""
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    assessment_date = db.Column(db.Date, default=date.today)
    assessment_type = db.Column(db.String(100), nullable=False)  # Pre-Purchase, Transfer, Insurance, Loan
    
    # Overall scores
    documentation_completeness_score = db.Column(db.Float)  # 0-100%
    compliance_score = db.Column(db.Float)  # 0-100%
    maintenance_score = db.Column(db.Float)  # 0-100%
    overall_risk_score = db.Column(db.Float)  # 0-100%
    
    # Risk categories
    structural_risk_level = db.Column(db.String(50))  # Low, Medium, High, Critical
    electrical_risk_level = db.Column(db.String(50))
    plumbing_risk_level = db.Column(db.String(50))
    hvac_risk_level = db.Column(db.String(50))
    fire_safety_risk_level = db.Column(db.String(50))
    
    # Financial impact
    estimated_immediate_costs = db.Column(db.Float)  # Costs to address immediate issues
    estimated_short_term_costs = db.Column(db.Float)  # Costs within 1-2 years
    estimated_long_term_costs = db.Column(db.Float)  # Costs over property lifetime
    property_value_adjustment = db.Column(db.Float)  # Suggested price adjustment
    
    # Identified issues
    critical_issues = db.Column(db.Text)  # JSON list of critical issues
    medium_issues = db.Column(db.Text)  # JSON list of medium priority issues
    low_issues = db.Column(db.Text)  # JSON list of low priority issues
    missing_documentation = db.Column(db.Text)  # JSON list of missing docs
    
    # Recommendations
    immediate_actions = db.Column(db.Text)  # JSON list of immediate actions
    short_term_actions = db.Column(db.Text)  # JSON list of short-term actions
    long_term_actions = db.Column(db.Text)  # JSON list of long-term actions
    insurance_recommendations = db.Column(db.Text)  # JSON list of insurance recommendations
    
    # Assessment details
    assessed_by = db.Column(db.String(200))
    assessment_method = db.Column(db.String(100))  # Automated, Professional, Hybrid
    confidence_level = db.Column(db.Float)  # 0-100% confidence in assessment
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'property_id': self.property_id,
            'assessment_date': self.assessment_date.isoformat(),
            'assessment_type': self.assessment_type,
            'documentation_completeness_score': self.documentation_completeness_score,
            'compliance_score': self.compliance_score,
            'maintenance_score': self.maintenance_score,
            'overall_risk_score': self.overall_risk_score,
            'structural_risk_level': self.structural_risk_level,
            'electrical_risk_level': self.electrical_risk_level,
            'plumbing_risk_level': self.plumbing_risk_level,
            'hvac_risk_level': self.hvac_risk_level,
            'fire_safety_risk_level': self.fire_safety_risk_level,
            'estimated_immediate_costs': self.estimated_immediate_costs,
            'estimated_short_term_costs': self.estimated_short_term_costs,
            'estimated_long_term_costs': self.estimated_long_term_costs,
            'property_value_adjustment': self.property_value_adjustment,
            'critical_issues': json.loads(self.critical_issues) if self.critical_issues else None,
            'medium_issues': json.loads(self.medium_issues) if self.medium_issues else None,
            'low_issues': json.loads(self.low_issues) if self.low_issues else None,
            'missing_documentation': json.loads(self.missing_documentation) if self.missing_documentation else None,
            'immediate_actions': json.loads(self.immediate_actions) if self.immediate_actions else None,
            'short_term_actions': json.loads(self.short_term_actions) if self.short_term_actions else None,
            'long_term_actions': json.loads(self.long_term_actions) if self.long_term_actions else None,
            'insurance_recommendations': json.loads(self.insurance_recommendations) if self.insurance_recommendations else None,
            'assessed_by': self.assessed_by,
            'assessment_method': self.assessment_method,
            'confidence_level': self.confidence_level,
            'created_at': self.created_at.isoformat()
        }

