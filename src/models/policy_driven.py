from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from src.models.user import db
import json

class InsurancePolicy(db.Model):
    """Represents an insurance policy with parsed requirements"""
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    policy_number = db.Column(db.String(100), nullable=False)
    insurer_name = db.Column(db.String(200), nullable=False)
    policy_type = db.Column(db.String(100), nullable=False)  # Home, Building, Contents, etc.
    
    # Policy details
    coverage_amount = db.Column(db.Float)
    premium_amount = db.Column(db.Float)
    deductible = db.Column(db.Float)
    policy_start_date = db.Column(db.Date)
    policy_end_date = db.Column(db.Date)
    
    # Document management
    policy_document_path = db.Column(db.String(500))  # Path to uploaded policy document
    parsed_text = db.Column(db.Text)  # Extracted text from policy document
    parsing_status = db.Column(db.String(50), default='Pending')  # Pending, Completed, Failed
    parsing_date = db.Column(db.DateTime)
    
    # Policy analysis
    coverage_summary = db.Column(db.Text)  # JSON summary of what's covered
    exclusions_summary = db.Column(db.Text)  # JSON summary of exclusions
    requirements_extracted = db.Column(db.Text)  # JSON list of requirements
    local_standards_referenced = db.Column(db.Text)  # JSON list of standards referenced
    
    # Compliance status
    compliance_score = db.Column(db.Float)  # 0-100% compliance with policy requirements
    last_compliance_check = db.Column(db.DateTime)
    compliance_status = db.Column(db.String(50), default='Unknown')  # Compliant, Non-Compliant, Partial, Unknown
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    requirements = db.relationship('PolicyRequirement', backref='policy', lazy=True, cascade='all, delete-orphan')
    compliance_checks = db.relationship('ComplianceCheck', backref='policy', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'property_id': self.property_id,
            'policy_number': self.policy_number,
            'insurer_name': self.insurer_name,
            'policy_type': self.policy_type,
            'coverage_amount': self.coverage_amount,
            'premium_amount': self.premium_amount,
            'deductible': self.deductible,
            'policy_start_date': self.policy_start_date.isoformat() if self.policy_start_date else None,
            'policy_end_date': self.policy_end_date.isoformat() if self.policy_end_date else None,
            'policy_document_path': self.policy_document_path,
            'parsing_status': self.parsing_status,
            'parsing_date': self.parsing_date.isoformat() if self.parsing_date else None,
            'coverage_summary': json.loads(self.coverage_summary) if self.coverage_summary else None,
            'exclusions_summary': json.loads(self.exclusions_summary) if self.exclusions_summary else None,
            'requirements_extracted': json.loads(self.requirements_extracted) if self.requirements_extracted else None,
            'local_standards_referenced': json.loads(self.local_standards_referenced) if self.local_standards_referenced else None,
            'compliance_score': self.compliance_score,
            'last_compliance_check': self.last_compliance_check.isoformat() if self.last_compliance_check else None,
            'compliance_status': self.compliance_status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class PolicyRequirement(db.Model):
    """Individual requirements extracted from insurance policies"""
    id = db.Column(db.Integer, primary_key=True)
    policy_id = db.Column(db.Integer, db.ForeignKey('insurance_policy.id'), nullable=False)
    
    # Requirement details
    requirement_type = db.Column(db.String(100), nullable=False)  # Certificate, Inspection, Maintenance, Standard Compliance
    requirement_description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100))  # Electrical, Plumbing, Structural, Fire Safety, etc.
    
    # Compliance details
    is_mandatory = db.Column(db.Boolean, default=True)  # Required for coverage vs. recommended
    frequency = db.Column(db.String(50))  # Annual, Bi-annual, One-time, As-needed
    validity_period_months = db.Column(db.Integer)  # How long the requirement remains valid
    
    # Standards and regulations
    referenced_standard = db.Column(db.String(200))  # SANS 10142, SABS 0400, etc.
    standard_version = db.Column(db.String(50))  # Version of the standard
    regulatory_body = db.Column(db.String(200))  # Who enforces this requirement
    
    # Documentation requirements
    required_document_type = db.Column(db.String(100))  # COC, Certificate, Report, etc.
    issuing_authority = db.Column(db.String(200))  # Who must issue the document
    professional_registration_required = db.Column(db.Boolean, default=False)
    
    # Compliance tracking
    current_status = db.Column(db.String(50), default='Not Met')  # Met, Not Met, Expired, Pending
    last_satisfied_date = db.Column(db.Date)
    next_due_date = db.Column(db.Date)
    
    # Impact on coverage
    coverage_impact = db.Column(db.String(100))  # Full Coverage, Partial Coverage, No Coverage
    exclusion_details = db.Column(db.Text)  # What's excluded if requirement not met
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    evidence_documents = db.relationship('RequirementEvidence', backref='requirement', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'policy_id': self.policy_id,
            'requirement_type': self.requirement_type,
            'requirement_description': self.requirement_description,
            'category': self.category,
            'is_mandatory': self.is_mandatory,
            'frequency': self.frequency,
            'validity_period_months': self.validity_period_months,
            'referenced_standard': self.referenced_standard,
            'standard_version': self.standard_version,
            'regulatory_body': self.regulatory_body,
            'required_document_type': self.required_document_type,
            'issuing_authority': self.issuing_authority,
            'professional_registration_required': self.professional_registration_required,
            'current_status': self.current_status,
            'last_satisfied_date': self.last_satisfied_date.isoformat() if self.last_satisfied_date else None,
            'next_due_date': self.next_due_date.isoformat() if self.next_due_date else None,
            'coverage_impact': self.coverage_impact,
            'exclusion_details': self.exclusion_details,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class RequirementEvidence(db.Model):
    """Evidence documents that satisfy policy requirements"""
    id = db.Column(db.Integer, primary_key=True)
    requirement_id = db.Column(db.Integer, db.ForeignKey('policy_requirement.id'), nullable=False)
    document_id = db.Column(db.Integer, db.ForeignKey('document.id'))  # Link to uploaded document
    
    # Evidence details
    evidence_type = db.Column(db.String(100), nullable=False)  # Certificate, Report, Photo, etc.
    evidence_description = db.Column(db.Text)
    issue_date = db.Column(db.Date)
    expiry_date = db.Column(db.Date)
    issuer_name = db.Column(db.String(200))
    issuer_registration = db.Column(db.String(100))  # Professional registration number
    
    # Validation
    is_valid = db.Column(db.Boolean, default=True)
    validation_status = db.Column(db.String(50), default='Pending')  # Pending, Validated, Invalid
    validation_notes = db.Column(db.Text)
    validated_by = db.Column(db.String(200))
    validation_date = db.Column(db.DateTime)
    
    # Compliance contribution
    satisfies_requirement = db.Column(db.Boolean, default=False)
    partial_satisfaction = db.Column(db.Float)  # 0-1 scale for partial compliance
    satisfaction_notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'requirement_id': self.requirement_id,
            'document_id': self.document_id,
            'evidence_type': self.evidence_type,
            'evidence_description': self.evidence_description,
            'issue_date': self.issue_date.isoformat() if self.issue_date else None,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'issuer_name': self.issuer_name,
            'issuer_registration': self.issuer_registration,
            'is_valid': self.is_valid,
            'validation_status': self.validation_status,
            'validation_notes': self.validation_notes,
            'validated_by': self.validated_by,
            'validation_date': self.validation_date.isoformat() if self.validation_date else None,
            'satisfies_requirement': self.satisfies_requirement,
            'partial_satisfaction': self.partial_satisfaction,
            'satisfaction_notes': self.satisfaction_notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class LocalStandard(db.Model):
    """Database of local standards and regulations"""
    id = db.Column(db.Integer, primary_key=True)
    standard_code = db.Column(db.String(100), unique=True, nullable=False)  # SANS 10142, SABS 0400
    standard_name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100))  # Electrical, Plumbing, Building, Fire Safety
    
    # Version management
    current_version = db.Column(db.String(50))
    version_date = db.Column(db.Date)
    previous_version = db.Column(db.String(50))
    superseded_date = db.Column(db.Date)
    
    # Authority and enforcement
    issuing_body = db.Column(db.String(200))  # SABS, SANS, Municipal, etc.
    enforcing_authority = db.Column(db.String(200))
    legal_status = db.Column(db.String(100))  # Mandatory, Recommended, Voluntary
    
    # Content summary
    scope_description = db.Column(db.Text)
    key_requirements = db.Column(db.Text)  # JSON list of key requirements
    compliance_methods = db.Column(db.Text)  # JSON list of how to comply
    
    # Updates and changes
    last_updated = db.Column(db.Date)
    update_frequency = db.Column(db.String(50))  # Annual, Bi-annual, As-needed
    next_review_date = db.Column(db.Date)
    change_summary = db.Column(db.Text)  # Summary of recent changes
    
    # Related standards
    related_standards = db.Column(db.Text)  # JSON list of related standard codes
    supersedes_standards = db.Column(db.Text)  # JSON list of superseded standards
    
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'standard_code': self.standard_code,
            'standard_name': self.standard_name,
            'category': self.category,
            'current_version': self.current_version,
            'version_date': self.version_date.isoformat() if self.version_date else None,
            'previous_version': self.previous_version,
            'superseded_date': self.superseded_date.isoformat() if self.superseded_date else None,
            'issuing_body': self.issuing_body,
            'enforcing_authority': self.enforcing_authority,
            'legal_status': self.legal_status,
            'scope_description': self.scope_description,
            'key_requirements': json.loads(self.key_requirements) if self.key_requirements else None,
            'compliance_methods': json.loads(self.compliance_methods) if self.compliance_methods else None,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
            'update_frequency': self.update_frequency,
            'next_review_date': self.next_review_date.isoformat() if self.next_review_date else None,
            'change_summary': self.change_summary,
            'related_standards': json.loads(self.related_standards) if self.related_standards else None,
            'supersedes_standards': json.loads(self.supersedes_standards) if self.supersedes_standards else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class ComplianceCheck(db.Model):
    """Automated compliance checks against policy requirements"""
    id = db.Column(db.Integer, primary_key=True)
    policy_id = db.Column(db.Integer, db.ForeignKey('insurance_policy.id'), nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    
    # Check details
    check_date = db.Column(db.DateTime, default=datetime.utcnow)
    check_type = db.Column(db.String(100), nullable=False)  # Scheduled, Triggered, Manual
    trigger_reason = db.Column(db.String(200))  # Policy upload, Document expiry, Standard update
    
    # Results
    overall_compliance_score = db.Column(db.Float)  # 0-100%
    requirements_checked = db.Column(db.Integer)
    requirements_met = db.Column(db.Integer)
    requirements_partial = db.Column(db.Integer)
    requirements_not_met = db.Column(db.Integer)
    
    # Risk assessment
    coverage_risk_level = db.Column(db.String(50))  # Low, Medium, High, Critical
    potential_exclusions = db.Column(db.Text)  # JSON list of potential exclusions
    recommended_actions = db.Column(db.Text)  # JSON list of recommended actions
    
    # Gaps identified
    missing_documents = db.Column(db.Text)  # JSON list of missing documents
    expired_certificates = db.Column(db.Text)  # JSON list of expired certificates
    outdated_standards = db.Column(db.Text)  # JSON list of outdated standard references
    
    # Next steps
    immediate_actions_required = db.Column(db.Text)  # JSON list of urgent actions
    next_check_date = db.Column(db.Date)
    monitoring_frequency = db.Column(db.String(50))  # Daily, Weekly, Monthly
    
    # Validation
    checked_by = db.Column(db.String(200))  # System, User, Expert
    validated_by = db.Column(db.String(200))
    validation_date = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'policy_id': self.policy_id,
            'property_id': self.property_id,
            'check_date': self.check_date.isoformat(),
            'check_type': self.check_type,
            'trigger_reason': self.trigger_reason,
            'overall_compliance_score': self.overall_compliance_score,
            'requirements_checked': self.requirements_checked,
            'requirements_met': self.requirements_met,
            'requirements_partial': self.requirements_partial,
            'requirements_not_met': self.requirements_not_met,
            'coverage_risk_level': self.coverage_risk_level,
            'potential_exclusions': json.loads(self.potential_exclusions) if self.potential_exclusions else None,
            'recommended_actions': json.loads(self.recommended_actions) if self.recommended_actions else None,
            'missing_documents': json.loads(self.missing_documents) if self.missing_documents else None,
            'expired_certificates': json.loads(self.expired_certificates) if self.expired_certificates else None,
            'outdated_standards': json.loads(self.outdated_standards) if self.outdated_standards else None,
            'immediate_actions_required': json.loads(self.immediate_actions_required) if self.immediate_actions_required else None,
            'next_check_date': self.next_check_date.isoformat() if self.next_check_date else None,
            'monitoring_frequency': self.monitoring_frequency,
            'checked_by': self.checked_by,
            'validated_by': self.validated_by,
            'validation_date': self.validation_date.isoformat() if self.validation_date else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat()
        }

class BankBond(db.Model):
    """Bank bond/mortgage requirements that must be met"""
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    loan_id = db.Column(db.Integer, db.ForeignKey('property_loan.id'))
    
    # Bond details
    bond_number = db.Column(db.String(100), nullable=False)
    bank_name = db.Column(db.String(200), nullable=False)
    bond_amount = db.Column(db.Float)
    
    # Insurance requirements from bond
    minimum_building_cover = db.Column(db.Float)
    minimum_contents_cover = db.Column(db.Float)
    required_policy_types = db.Column(db.Text)  # JSON list of required policy types
    
    # Compliance requirements
    bond_requirements = db.Column(db.Text)  # JSON list of bond-specific requirements
    maintenance_obligations = db.Column(db.Text)  # JSON list of maintenance requirements
    insurance_obligations = db.Column(db.Text)  # JSON list of insurance obligations
    
    # Monitoring
    compliance_monitoring_required = db.Column(db.Boolean, default=True)
    reporting_frequency = db.Column(db.String(50))  # Annual, Bi-annual, As-required
    last_compliance_report = db.Column(db.Date)
    next_compliance_report = db.Column(db.Date)
    
    # Status
    bond_status = db.Column(db.String(50), default='Active')  # Active, Paid Off, Default
    compliance_status = db.Column(db.String(50), default='Unknown')  # Compliant, Non-Compliant, Under Review
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'property_id': self.property_id,
            'loan_id': self.loan_id,
            'bond_number': self.bond_number,
            'bank_name': self.bank_name,
            'bond_amount': self.bond_amount,
            'minimum_building_cover': self.minimum_building_cover,
            'minimum_contents_cover': self.minimum_contents_cover,
            'required_policy_types': json.loads(self.required_policy_types) if self.required_policy_types else None,
            'bond_requirements': json.loads(self.bond_requirements) if self.bond_requirements else None,
            'maintenance_obligations': json.loads(self.maintenance_obligations) if self.maintenance_obligations else None,
            'insurance_obligations': json.loads(self.insurance_obligations) if self.insurance_obligations else None,
            'compliance_monitoring_required': self.compliance_monitoring_required,
            'reporting_frequency': self.reporting_frequency,
            'last_compliance_report': self.last_compliance_report.isoformat() if self.last_compliance_report else None,
            'next_compliance_report': self.next_compliance_report.isoformat() if self.next_compliance_report else None,
            'bond_status': self.bond_status,
            'compliance_status': self.compliance_status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

