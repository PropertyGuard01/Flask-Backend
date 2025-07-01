from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from src.models.user import db

class Project(db.Model):
    """Represents a construction/renovation project with multiple stakeholders"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    project_type = db.Column(db.String(100), nullable=False)  # Roofing, Electrical, Plumbing, etc.
    start_date = db.Column(db.Date)
    completion_date = db.Column(db.Date)
    estimated_value = db.Column(db.Float)
    actual_value = db.Column(db.Float)
    status = db.Column(db.String(50), default='Planning')  # Planning, In Progress, Completed, On Hold
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    primary_contractor_id = db.Column(db.Integer, db.ForeignKey('contractor.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    stakeholders = db.relationship('ProjectStakeholder', backref='project', lazy=True, cascade='all, delete-orphan')
    liability_chains = db.relationship('LiabilityChain', backref='project', lazy=True, cascade='all, delete-orphan')
    compliance_items = db.relationship('ComplianceItem', backref='project', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'project_type': self.project_type,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'completion_date': self.completion_date.isoformat() if self.completion_date else None,
            'estimated_value': self.estimated_value,
            'actual_value': self.actual_value,
            'status': self.status,
            'property_id': self.property_id,
            'primary_contractor_id': self.primary_contractor_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class ProjectStakeholder(db.Model):
    """Represents all parties involved in a project (contractors, suppliers, engineers, etc.)"""
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    stakeholder_type = db.Column(db.String(100), nullable=False)  # Contractor, Supplier, Engineer, Inspector, Software Provider
    company_name = db.Column(db.String(200), nullable=False)
    contact_person = db.Column(db.String(200))
    phone = db.Column(db.String(50))
    email = db.Column(db.String(120))
    address = db.Column(db.String(500))
    role_description = db.Column(db.Text)  # Specific role in this project
    license_number = db.Column(db.String(100))
    registration_number = db.Column(db.String(100))  # Company registration
    is_active = db.Column(db.Boolean, default=True)  # Still in business
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    insurance_policies = db.relationship('StakeholderInsurance', backref='stakeholder', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'stakeholder_type': self.stakeholder_type,
            'company_name': self.company_name,
            'contact_person': self.contact_person,
            'phone': self.phone,
            'email': self.email,
            'address': self.address,
            'role_description': self.role_description,
            'license_number': self.license_number,
            'registration_number': self.registration_number,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }

class StakeholderInsurance(db.Model):
    """Insurance policies held by project stakeholders"""
    id = db.Column(db.Integer, primary_key=True)
    stakeholder_id = db.Column(db.Integer, db.ForeignKey('project_stakeholder.id'), nullable=False)
    insurance_type = db.Column(db.String(100), nullable=False)  # Public Liability, Product Liability, Professional Indemnity, Contractors All Risk
    policy_number = db.Column(db.String(100))
    insurer_name = db.Column(db.String(200))
    coverage_amount = db.Column(db.Float)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    premium_amount = db.Column(db.Float)
    deductible = db.Column(db.Float)
    coverage_details = db.Column(db.Text)  # What's covered
    exclusions = db.Column(db.Text)  # What's not covered
    status = db.Column(db.String(50), default='Active')  # Active, Expired, Cancelled
    document_id = db.Column(db.Integer, db.ForeignKey('document.id'))  # Link to policy document
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'stakeholder_id': self.stakeholder_id,
            'insurance_type': self.insurance_type,
            'policy_number': self.policy_number,
            'insurer_name': self.insurer_name,
            'coverage_amount': self.coverage_amount,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'premium_amount': self.premium_amount,
            'deductible': self.deductible,
            'coverage_details': self.coverage_details,
            'exclusions': self.exclusions,
            'status': self.status,
            'document_id': self.document_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class LiabilityChain(db.Model):
    """Maps the chain of liability for different aspects of a project"""
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    component = db.Column(db.String(200), nullable=False)  # e.g., "Roof Design", "Material Supply", "Installation"
    responsible_party_id = db.Column(db.Integer, db.ForeignKey('project_stakeholder.id'), nullable=False)
    liability_scope = db.Column(db.Text)  # What they're responsible for
    liability_limitations = db.Column(db.Text)  # What they're NOT responsible for
    insurance_coverage_required = db.Column(db.String(200))  # Type of insurance that should cover this
    coverage_amount_required = db.Column(db.Float)  # Minimum coverage amount
    warranty_period_months = db.Column(db.Integer)
    warranty_terms = db.Column(db.Text)
    risk_level = db.Column(db.String(50), default='Medium')  # Low, Medium, High, Critical
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    responsible_party = db.relationship('ProjectStakeholder', backref='liability_items')

    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'component': self.component,
            'responsible_party_id': self.responsible_party_id,
            'liability_scope': self.liability_scope,
            'liability_limitations': self.liability_limitations,
            'insurance_coverage_required': self.insurance_coverage_required,
            'coverage_amount_required': self.coverage_amount_required,
            'warranty_period_months': self.warranty_period_months,
            'warranty_terms': self.warranty_terms,
            'risk_level': self.risk_level,
            'notes': self.notes,
            'created_at': self.created_at.isoformat()
        }

class ComplianceItem(db.Model):
    """Tracks compliance requirements and certifications"""
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    compliance_type = db.Column(db.String(100), nullable=False)  # COC, Building Approval, Safety Certificate, etc.
    requirement_description = db.Column(db.Text)
    issuing_authority = db.Column(db.String(200))  # Who issues the certificate
    inspector_name = db.Column(db.String(200))
    inspector_contact = db.Column(db.String(200))
    engineer_name = db.Column(db.String(200))  # Responsible engineer
    engineer_contact = db.Column(db.String(200))
    engineer_registration = db.Column(db.String(100))  # Professional registration number
    issue_date = db.Column(db.Date)
    expiry_date = db.Column(db.Date)
    validity_period_months = db.Column(db.Integer)
    renewal_required = db.Column(db.Boolean, default=False)
    renewal_process = db.Column(db.Text)  # How to renew
    status = db.Column(db.String(50), default='Pending')  # Pending, Issued, Expired, Renewed
    certificate_number = db.Column(db.String(100))
    conditions = db.Column(db.Text)  # Any conditions or limitations
    document_id = db.Column(db.Integer, db.ForeignKey('document.id'))  # Link to certificate document
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'compliance_type': self.compliance_type,
            'requirement_description': self.requirement_description,
            'issuing_authority': self.issuing_authority,
            'inspector_name': self.inspector_name,
            'inspector_contact': self.inspector_contact,
            'engineer_name': self.engineer_name,
            'engineer_contact': self.engineer_contact,
            'engineer_registration': self.engineer_registration,
            'issue_date': self.issue_date.isoformat() if self.issue_date else None,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'validity_period_months': self.validity_period_months,
            'renewal_required': self.renewal_required,
            'renewal_process': self.renewal_process,
            'status': self.status,
            'certificate_number': self.certificate_number,
            'conditions': self.conditions,
            'document_id': self.document_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class RiskAssessment(db.Model):
    """Risk assessment for projects and liability chains"""
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    assessment_date = db.Column(db.Date, default=date.today)
    overall_risk_score = db.Column(db.Float)  # 1-10 scale
    insurance_coverage_adequacy = db.Column(db.String(50))  # Adequate, Inadequate, Unknown
    liability_gaps_identified = db.Column(db.Text)  # Description of gaps
    compliance_status = db.Column(db.String(50))  # Compliant, Non-Compliant, Partial
    recommendations = db.Column(db.Text)
    next_review_date = db.Column(db.Date)
    assessed_by = db.Column(db.String(200))  # Who performed the assessment
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'assessment_date': self.assessment_date.isoformat(),
            'overall_risk_score': self.overall_risk_score,
            'insurance_coverage_adequacy': self.insurance_coverage_adequacy,
            'liability_gaps_identified': self.liability_gaps_identified,
            'compliance_status': self.compliance_status,
            'recommendations': self.recommendations,
            'next_review_date': self.next_review_date.isoformat() if self.next_review_date else None,
            'assessed_by': self.assessed_by,
            'notes': self.notes,
            'created_at': self.created_at.isoformat()
        }

class Alert(db.Model):
    """System alerts for expiring insurance, compliance items, etc."""
    id = db.Column(db.Integer, primary_key=True)
    alert_type = db.Column(db.String(100), nullable=False)  # Insurance Expiry, COC Expiry, Risk Alert, etc.
    severity = db.Column(db.String(50), default='Medium')  # Low, Medium, High, Critical
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text)
    related_entity_type = db.Column(db.String(100))  # Project, Stakeholder, Insurance, Compliance
    related_entity_id = db.Column(db.Integer)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    is_read = db.Column(db.Boolean, default=False)
    is_resolved = db.Column(db.Boolean, default=False)
    due_date = db.Column(db.Date)  # When action is required
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)

    def to_dict(self):
        return {
            'id': self.id,
            'alert_type': self.alert_type,
            'severity': self.severity,
            'title': self.title,
            'message': self.message,
            'related_entity_type': self.related_entity_type,
            'related_entity_id': self.related_entity_id,
            'property_id': self.property_id,
            'user_id': self.user_id,
            'is_read': self.is_read,
            'is_resolved': self.is_resolved,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'created_at': self.created_at.isoformat(),
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None
        }

