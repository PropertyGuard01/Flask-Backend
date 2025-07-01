from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from src.models.user import db

class FinancialInstitution(db.Model):
    """Represents banks and other financial institutions"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    institution_type = db.Column(db.String(100), nullable=False)  # Bank, Credit Union, Mortgage Company, etc.
    registration_number = db.Column(db.String(100))
    contact_person = db.Column(db.String(200))
    phone = db.Column(db.String(50))
    email = db.Column(db.String(120))
    address = db.Column(db.String(500))
    regulatory_body = db.Column(db.String(200))  # SARB, NCR, etc.
    license_number = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    loans = db.relationship('PropertyLoan', backref='financial_institution', lazy=True)
    risk_policies = db.relationship('InstitutionRiskPolicy', backref='financial_institution', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'institution_type': self.institution_type,
            'registration_number': self.registration_number,
            'contact_person': self.contact_person,
            'phone': self.phone,
            'email': self.email,
            'address': self.address,
            'regulatory_body': self.regulatory_body,
            'license_number': self.license_number,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }

class PropertyLoan(db.Model):
    """Represents a loan secured against a property"""
    id = db.Column(db.Integer, primary_key=True)
    loan_number = db.Column(db.String(100), unique=True, nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    financial_institution_id = db.Column(db.Integer, db.ForeignKey('financial_institution.id'), nullable=False)
    borrower_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    loan_amount = db.Column(db.Float, nullable=False)
    outstanding_balance = db.Column(db.Float)
    interest_rate = db.Column(db.Float)
    loan_term_months = db.Column(db.Integer)
    start_date = db.Column(db.Date)
    maturity_date = db.Column(db.Date)
    loan_purpose = db.Column(db.String(200))  # Purchase, Construction, Renovation, etc.
    loan_status = db.Column(db.String(50), default='Active')  # Active, Paid Off, Default, etc.
    ltv_ratio = db.Column(db.Float)  # Loan to Value ratio
    property_valuation = db.Column(db.Float)
    valuation_date = db.Column(db.Date)
    last_payment_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    risk_assessments = db.relationship('LoanRiskAssessment', backref='loan', lazy=True, cascade='all, delete-orphan')
    defect_claims = db.relationship('DefectClaim', backref='loan', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'loan_number': self.loan_number,
            'property_id': self.property_id,
            'financial_institution_id': self.financial_institution_id,
            'borrower_id': self.borrower_id,
            'loan_amount': self.loan_amount,
            'outstanding_balance': self.outstanding_balance,
            'interest_rate': self.interest_rate,
            'loan_term_months': self.loan_term_months,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'maturity_date': self.maturity_date.isoformat() if self.maturity_date else None,
            'loan_purpose': self.loan_purpose,
            'loan_status': self.loan_status,
            'ltv_ratio': self.ltv_ratio,
            'property_valuation': self.property_valuation,
            'valuation_date': self.valuation_date.isoformat() if self.valuation_date else None,
            'last_payment_date': self.last_payment_date.isoformat() if self.last_payment_date else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class LoanRiskAssessment(db.Model):
    """Risk assessments performed by financial institutions"""
    id = db.Column(db.Integer, primary_key=True)
    loan_id = db.Column(db.Integer, db.ForeignKey('property_loan.id'), nullable=False)
    assessment_date = db.Column(db.Date, default=date.today)
    assessment_type = db.Column(db.String(100), nullable=False)  # Initial, Annual Review, Triggered, etc.
    overall_risk_score = db.Column(db.Float)  # 1-10 scale
    property_condition_score = db.Column(db.Float)
    contractor_reliability_score = db.Column(db.Float)
    insurance_adequacy_score = db.Column(db.Float)
    compliance_score = db.Column(db.Float)
    market_risk_score = db.Column(db.Float)
    
    # Risk factors
    identified_risks = db.Column(db.Text)
    mitigation_measures = db.Column(db.Text)
    recommendations = db.Column(db.Text)
    
    # Insurance requirements
    required_coverage_types = db.Column(db.Text)  # JSON list of required insurance types
    minimum_coverage_amounts = db.Column(db.Text)  # JSON object with coverage amounts
    
    # Monitoring requirements
    monitoring_frequency = db.Column(db.String(50))  # Monthly, Quarterly, Annually
    next_review_date = db.Column(db.Date)
    
    assessed_by = db.Column(db.String(200))
    approved_by = db.Column(db.String(200))
    status = db.Column(db.String(50), default='Active')  # Active, Superseded, Archived
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'loan_id': self.loan_id,
            'assessment_date': self.assessment_date.isoformat(),
            'assessment_type': self.assessment_type,
            'overall_risk_score': self.overall_risk_score,
            'property_condition_score': self.property_condition_score,
            'contractor_reliability_score': self.contractor_reliability_score,
            'insurance_adequacy_score': self.insurance_adequacy_score,
            'compliance_score': self.compliance_score,
            'market_risk_score': self.market_risk_score,
            'identified_risks': self.identified_risks,
            'mitigation_measures': self.mitigation_measures,
            'recommendations': self.recommendations,
            'required_coverage_types': self.required_coverage_types,
            'minimum_coverage_amounts': self.minimum_coverage_amounts,
            'monitoring_frequency': self.monitoring_frequency,
            'next_review_date': self.next_review_date.isoformat() if self.next_review_date else None,
            'assessed_by': self.assessed_by,
            'approved_by': self.approved_by,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat()
        }

class DefectClaim(db.Model):
    """Tracks defect claims that could impact loan security"""
    id = db.Column(db.Integer, primary_key=True)
    loan_id = db.Column(db.Integer, db.ForeignKey('property_loan.id'), nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))  # If related to specific project
    
    # Claim details
    claim_number = db.Column(db.String(100))
    defect_description = db.Column(db.Text, nullable=False)
    defect_category = db.Column(db.String(100))  # Structural, Waterproofing, Electrical, etc.
    discovery_date = db.Column(db.Date)
    reported_date = db.Column(db.Date, default=date.today)
    estimated_repair_cost = db.Column(db.Float)
    actual_repair_cost = db.Column(db.Float)
    
    # Responsible parties
    responsible_contractor_id = db.Column(db.Integer, db.ForeignKey('project_stakeholder.id'))
    responsible_engineer_id = db.Column(db.Integer, db.ForeignKey('project_stakeholder.id'))
    responsible_supplier_id = db.Column(db.Integer, db.ForeignKey('project_stakeholder.id'))
    
    # Insurance claims
    homeowner_insurance_claim_number = db.Column(db.String(100))
    homeowner_insurance_status = db.Column(db.String(50))  # Pending, Approved, Rejected, Settled
    homeowner_insurance_payout = db.Column(db.Float)
    
    contractor_insurance_claim_number = db.Column(db.String(100))
    contractor_insurance_status = db.Column(db.String(50))
    contractor_insurance_payout = db.Column(db.Float)
    
    # Legal proceedings
    legal_action_required = db.Column(db.Boolean, default=False)
    legal_case_number = db.Column(db.String(100))
    legal_status = db.Column(db.String(50))  # Pending, Settled, Judgment, etc.
    legal_outcome = db.Column(db.Text)
    
    # Impact on loan
    property_value_impact = db.Column(db.Float)  # Estimated impact on property value
    loan_security_affected = db.Column(db.Boolean, default=False)
    bank_action_required = db.Column(db.Boolean, default=False)
    bank_action_taken = db.Column(db.Text)
    
    # Resolution
    resolution_status = db.Column(db.String(50), default='Open')  # Open, In Progress, Resolved, Closed
    resolution_date = db.Column(db.Date)
    resolution_details = db.Column(db.Text)
    final_cost_to_borrower = db.Column(db.Float)
    
    # Documentation
    photos_available = db.Column(db.Boolean, default=False)
    expert_reports_available = db.Column(db.Boolean, default=False)
    correspondence_file = db.Column(db.String(500))  # Path to correspondence file
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'loan_id': self.loan_id,
            'property_id': self.property_id,
            'project_id': self.project_id,
            'claim_number': self.claim_number,
            'defect_description': self.defect_description,
            'defect_category': self.defect_category,
            'discovery_date': self.discovery_date.isoformat() if self.discovery_date else None,
            'reported_date': self.reported_date.isoformat(),
            'estimated_repair_cost': self.estimated_repair_cost,
            'actual_repair_cost': self.actual_repair_cost,
            'responsible_contractor_id': self.responsible_contractor_id,
            'responsible_engineer_id': self.responsible_engineer_id,
            'responsible_supplier_id': self.responsible_supplier_id,
            'homeowner_insurance_claim_number': self.homeowner_insurance_claim_number,
            'homeowner_insurance_status': self.homeowner_insurance_status,
            'homeowner_insurance_payout': self.homeowner_insurance_payout,
            'contractor_insurance_claim_number': self.contractor_insurance_claim_number,
            'contractor_insurance_status': self.contractor_insurance_status,
            'contractor_insurance_payout': self.contractor_insurance_payout,
            'legal_action_required': self.legal_action_required,
            'legal_case_number': self.legal_case_number,
            'legal_status': self.legal_status,
            'legal_outcome': self.legal_outcome,
            'property_value_impact': self.property_value_impact,
            'loan_security_affected': self.loan_security_affected,
            'bank_action_required': self.bank_action_required,
            'bank_action_taken': self.bank_action_taken,
            'resolution_status': self.resolution_status,
            'resolution_date': self.resolution_date.isoformat() if self.resolution_date else None,
            'resolution_details': self.resolution_details,
            'final_cost_to_borrower': self.final_cost_to_borrower,
            'photos_available': self.photos_available,
            'expert_reports_available': self.expert_reports_available,
            'correspondence_file': self.correspondence_file,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class InstitutionRiskPolicy(db.Model):
    """Risk management policies and requirements set by financial institutions"""
    id = db.Column(db.Integer, primary_key=True)
    financial_institution_id = db.Column(db.Integer, db.ForeignKey('financial_institution.id'), nullable=False)
    policy_name = db.Column(db.String(200), nullable=False)
    policy_type = db.Column(db.String(100), nullable=False)  # Insurance Requirements, Contractor Standards, etc.
    
    # Requirements
    minimum_insurance_coverage = db.Column(db.Text)  # JSON object with coverage requirements
    required_certifications = db.Column(db.Text)  # JSON list of required certifications
    contractor_vetting_requirements = db.Column(db.Text)
    compliance_monitoring_frequency = db.Column(db.String(50))
    
    # Risk thresholds
    maximum_ltv_ratio = db.Column(db.Float)
    minimum_property_age = db.Column(db.Integer)  # Years
    maximum_property_age = db.Column(db.Integer)  # Years
    excluded_property_types = db.Column(db.Text)  # JSON list
    excluded_construction_types = db.Column(db.Text)  # JSON list
    
    # Monitoring requirements
    mandatory_inspections = db.Column(db.Text)  # JSON list of required inspections
    documentation_requirements = db.Column(db.Text)
    reporting_requirements = db.Column(db.Text)
    
    effective_date = db.Column(db.Date)
    expiry_date = db.Column(db.Date)
    is_active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.String(200))
    approved_by = db.Column(db.String(200))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'financial_institution_id': self.financial_institution_id,
            'policy_name': self.policy_name,
            'policy_type': self.policy_type,
            'minimum_insurance_coverage': self.minimum_insurance_coverage,
            'required_certifications': self.required_certifications,
            'contractor_vetting_requirements': self.contractor_vetting_requirements,
            'compliance_monitoring_frequency': self.compliance_monitoring_frequency,
            'maximum_ltv_ratio': self.maximum_ltv_ratio,
            'minimum_property_age': self.minimum_property_age,
            'maximum_property_age': self.maximum_property_age,
            'excluded_property_types': self.excluded_property_types,
            'excluded_construction_types': self.excluded_construction_types,
            'mandatory_inspections': self.mandatory_inspections,
            'documentation_requirements': self.documentation_requirements,
            'reporting_requirements': self.reporting_requirements,
            'effective_date': self.effective_date.isoformat() if self.effective_date else None,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'is_active': self.is_active,
            'created_by': self.created_by,
            'approved_by': self.approved_by,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class PortfolioRiskSummary(db.Model):
    """Aggregated risk summary for a financial institution's property portfolio"""
    id = db.Column(db.Integer, primary_key=True)
    financial_institution_id = db.Column(db.Integer, db.ForeignKey('financial_institution.id'), nullable=False)
    summary_date = db.Column(db.Date, default=date.today)
    
    # Portfolio metrics
    total_loans = db.Column(db.Integer)
    total_exposure = db.Column(db.Float)
    average_ltv = db.Column(db.Float)
    
    # Risk distribution
    high_risk_loans = db.Column(db.Integer)
    medium_risk_loans = db.Column(db.Integer)
    low_risk_loans = db.Column(db.Integer)
    
    # Defect claims
    open_defect_claims = db.Column(db.Integer)
    total_claims_value = db.Column(db.Float)
    resolved_claims_this_period = db.Column(db.Integer)
    
    # Insurance coverage
    loans_with_adequate_coverage = db.Column(db.Integer)
    loans_with_coverage_gaps = db.Column(db.Integer)
    expiring_policies_next_30_days = db.Column(db.Integer)
    
    # Compliance
    compliant_properties = db.Column(db.Integer)
    non_compliant_properties = db.Column(db.Integer)
    expiring_certificates_next_30_days = db.Column(db.Integer)
    
    # Recommendations
    recommended_actions = db.Column(db.Text)
    priority_reviews_required = db.Column(db.Integer)
    
    generated_by = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'financial_institution_id': self.financial_institution_id,
            'summary_date': self.summary_date.isoformat(),
            'total_loans': self.total_loans,
            'total_exposure': self.total_exposure,
            'average_ltv': self.average_ltv,
            'high_risk_loans': self.high_risk_loans,
            'medium_risk_loans': self.medium_risk_loans,
            'low_risk_loans': self.low_risk_loans,
            'open_defect_claims': self.open_defect_claims,
            'total_claims_value': self.total_claims_value,
            'resolved_claims_this_period': self.resolved_claims_this_period,
            'loans_with_adequate_coverage': self.loans_with_adequate_coverage,
            'loans_with_coverage_gaps': self.loans_with_coverage_gaps,
            'expiring_policies_next_30_days': self.expiring_policies_next_30_days,
            'compliant_properties': self.compliant_properties,
            'non_compliant_properties': self.non_compliant_properties,
            'expiring_certificates_next_30_days': self.expiring_certificates_next_30_days,
            'recommended_actions': self.recommended_actions,
            'priority_reviews_required': self.priority_reviews_required,
            'generated_by': self.generated_by,
            'created_at': self.created_at.isoformat()
        }

