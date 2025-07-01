from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.property import Property
from src.models.liability import (
    Project, ProjectStakeholder, StakeholderInsurance, 
    LiabilityChain, ComplianceItem, RiskAssessment, Alert
)
from datetime import datetime, date, timedelta
import json

liability_bp = Blueprint('liability', __name__)

# Helper function to parse date strings
def parse_date(date_string):
    if not date_string:
        return None
    try:
        return datetime.strptime(date_string, '%Y-%m-%d').date()
    except ValueError:
        return None

# Projects endpoints
@liability_bp.route('/projects', methods=['GET'])
def get_projects():
    """Get all projects for a user"""
    user_id = request.args.get('user_id', 1)
    
    # Join with Property to filter by user
    projects = db.session.query(Project).join(Property).filter(Property.user_id == user_id).all()
    return jsonify([project.to_dict() for project in projects])

@liability_bp.route('/projects', methods=['POST'])
def create_project():
    """Create a new project"""
    data = request.get_json()
    
    project = Project(
        name=data.get('name'),
        description=data.get('description'),
        project_type=data.get('project_type'),
        start_date=parse_date(data.get('start_date')),
        completion_date=parse_date(data.get('completion_date')),
        estimated_value=data.get('estimated_value'),
        actual_value=data.get('actual_value'),
        status=data.get('status', 'Planning'),
        property_id=data.get('property_id'),
        primary_contractor_id=data.get('primary_contractor_id')
    )
    
    db.session.add(project)
    db.session.commit()
    
    return jsonify(project.to_dict()), 201

@liability_bp.route('/projects/<int:project_id>', methods=['GET'])
def get_project(project_id):
    """Get a specific project with all related data"""
    project = Project.query.get_or_404(project_id)
    
    # Get related data
    stakeholders = [s.to_dict() for s in project.stakeholders]
    liability_chains = [l.to_dict() for l in project.liability_chains]
    compliance_items = [c.to_dict() for c in project.compliance_items]
    
    project_data = project.to_dict()
    project_data['stakeholders'] = stakeholders
    project_data['liability_chains'] = liability_chains
    project_data['compliance_items'] = compliance_items
    
    return jsonify(project_data)

@liability_bp.route('/projects/<int:project_id>', methods=['PUT'])
def update_project(project_id):
    """Update a project"""
    project = Project.query.get_or_404(project_id)
    data = request.get_json()
    
    project.name = data.get('name', project.name)
    project.description = data.get('description', project.description)
    project.project_type = data.get('project_type', project.project_type)
    project.start_date = parse_date(data.get('start_date')) or project.start_date
    project.completion_date = parse_date(data.get('completion_date')) or project.completion_date
    project.estimated_value = data.get('estimated_value', project.estimated_value)
    project.actual_value = data.get('actual_value', project.actual_value)
    project.status = data.get('status', project.status)
    project.primary_contractor_id = data.get('primary_contractor_id', project.primary_contractor_id)
    project.updated_at = datetime.utcnow()
    
    db.session.commit()
    return jsonify(project.to_dict())

# Project Stakeholders endpoints
@liability_bp.route('/projects/<int:project_id>/stakeholders', methods=['GET'])
def get_project_stakeholders(project_id):
    """Get all stakeholders for a project"""
    stakeholders = ProjectStakeholder.query.filter_by(project_id=project_id).all()
    
    # Include insurance information for each stakeholder
    result = []
    for stakeholder in stakeholders:
        stakeholder_data = stakeholder.to_dict()
        stakeholder_data['insurance_policies'] = [ins.to_dict() for ins in stakeholder.insurance_policies]
        result.append(stakeholder_data)
    
    return jsonify(result)

@liability_bp.route('/projects/<int:project_id>/stakeholders', methods=['POST'])
def create_project_stakeholder(project_id):
    """Add a stakeholder to a project"""
    data = request.get_json()
    
    stakeholder = ProjectStakeholder(
        project_id=project_id,
        stakeholder_type=data.get('stakeholder_type'),
        company_name=data.get('company_name'),
        contact_person=data.get('contact_person'),
        phone=data.get('phone'),
        email=data.get('email'),
        address=data.get('address'),
        role_description=data.get('role_description'),
        license_number=data.get('license_number'),
        registration_number=data.get('registration_number'),
        is_active=data.get('is_active', True)
    )
    
    db.session.add(stakeholder)
    db.session.commit()
    
    return jsonify(stakeholder.to_dict()), 201

# Insurance endpoints
@liability_bp.route('/stakeholders/<int:stakeholder_id>/insurance', methods=['GET'])
def get_stakeholder_insurance(stakeholder_id):
    """Get all insurance policies for a stakeholder"""
    insurance_policies = StakeholderInsurance.query.filter_by(stakeholder_id=stakeholder_id).all()
    return jsonify([policy.to_dict() for policy in insurance_policies])

@liability_bp.route('/stakeholders/<int:stakeholder_id>/insurance', methods=['POST'])
def create_stakeholder_insurance(stakeholder_id):
    """Add an insurance policy for a stakeholder"""
    data = request.get_json()
    
    insurance = StakeholderInsurance(
        stakeholder_id=stakeholder_id,
        insurance_type=data.get('insurance_type'),
        policy_number=data.get('policy_number'),
        insurer_name=data.get('insurer_name'),
        coverage_amount=data.get('coverage_amount'),
        start_date=parse_date(data.get('start_date')),
        end_date=parse_date(data.get('end_date')),
        premium_amount=data.get('premium_amount'),
        deductible=data.get('deductible'),
        coverage_details=data.get('coverage_details'),
        exclusions=data.get('exclusions'),
        status=data.get('status', 'Active'),
        document_id=data.get('document_id')
    )
    
    db.session.add(insurance)
    db.session.commit()
    
    return jsonify(insurance.to_dict()), 201

# Liability Chain endpoints
@liability_bp.route('/projects/<int:project_id>/liability-chain', methods=['GET'])
def get_liability_chain(project_id):
    """Get the liability chain for a project"""
    liability_items = LiabilityChain.query.filter_by(project_id=project_id).all()
    
    result = []
    for item in liability_items:
        item_data = item.to_dict()
        # Include stakeholder details
        if item.responsible_party:
            item_data['responsible_party'] = item.responsible_party.to_dict()
        result.append(item_data)
    
    return jsonify(result)

@liability_bp.route('/projects/<int:project_id>/liability-chain', methods=['POST'])
def create_liability_chain_item(project_id):
    """Add a liability chain item"""
    data = request.get_json()
    
    liability_item = LiabilityChain(
        project_id=project_id,
        component=data.get('component'),
        responsible_party_id=data.get('responsible_party_id'),
        liability_scope=data.get('liability_scope'),
        liability_limitations=data.get('liability_limitations'),
        insurance_coverage_required=data.get('insurance_coverage_required'),
        coverage_amount_required=data.get('coverage_amount_required'),
        warranty_period_months=data.get('warranty_period_months'),
        warranty_terms=data.get('warranty_terms'),
        risk_level=data.get('risk_level', 'Medium'),
        notes=data.get('notes')
    )
    
    db.session.add(liability_item)
    db.session.commit()
    
    return jsonify(liability_item.to_dict()), 201

# Compliance endpoints
@liability_bp.route('/projects/<int:project_id>/compliance', methods=['GET'])
def get_project_compliance(project_id):
    """Get all compliance items for a project"""
    compliance_items = ComplianceItem.query.filter_by(project_id=project_id).all()
    return jsonify([item.to_dict() for item in compliance_items])

@liability_bp.route('/projects/<int:project_id>/compliance', methods=['POST'])
def create_compliance_item(project_id):
    """Add a compliance item"""
    data = request.get_json()
    
    compliance_item = ComplianceItem(
        project_id=project_id,
        compliance_type=data.get('compliance_type'),
        requirement_description=data.get('requirement_description'),
        issuing_authority=data.get('issuing_authority'),
        inspector_name=data.get('inspector_name'),
        inspector_contact=data.get('inspector_contact'),
        engineer_name=data.get('engineer_name'),
        engineer_contact=data.get('engineer_contact'),
        engineer_registration=data.get('engineer_registration'),
        issue_date=parse_date(data.get('issue_date')),
        expiry_date=parse_date(data.get('expiry_date')),
        validity_period_months=data.get('validity_period_months'),
        renewal_required=data.get('renewal_required', False),
        renewal_process=data.get('renewal_process'),
        status=data.get('status', 'Pending'),
        certificate_number=data.get('certificate_number'),
        conditions=data.get('conditions'),
        document_id=data.get('document_id')
    )
    
    db.session.add(compliance_item)
    db.session.commit()
    
    return jsonify(compliance_item.to_dict()), 201

@liability_bp.route('/compliance/<int:compliance_id>', methods=['PUT'])
def update_compliance_item(compliance_id):
    """Update a compliance item"""
    compliance_item = ComplianceItem.query.get_or_404(compliance_id)
    data = request.get_json()
    
    compliance_item.status = data.get('status', compliance_item.status)
    compliance_item.issue_date = parse_date(data.get('issue_date')) or compliance_item.issue_date
    compliance_item.expiry_date = parse_date(data.get('expiry_date')) or compliance_item.expiry_date
    compliance_item.certificate_number = data.get('certificate_number', compliance_item.certificate_number)
    compliance_item.conditions = data.get('conditions', compliance_item.conditions)
    compliance_item.document_id = data.get('document_id', compliance_item.document_id)
    compliance_item.updated_at = datetime.utcnow()
    
    db.session.commit()
    return jsonify(compliance_item.to_dict())

# Risk Assessment endpoints
@liability_bp.route('/projects/<int:project_id>/risk-assessment', methods=['GET'])
def get_risk_assessments(project_id):
    """Get risk assessments for a project"""
    assessments = RiskAssessment.query.filter_by(project_id=project_id).order_by(RiskAssessment.assessment_date.desc()).all()
    return jsonify([assessment.to_dict() for assessment in assessments])

@liability_bp.route('/projects/<int:project_id>/risk-assessment', methods=['POST'])
def create_risk_assessment(project_id):
    """Create a risk assessment"""
    data = request.get_json()
    
    assessment = RiskAssessment(
        project_id=project_id,
        assessment_date=parse_date(data.get('assessment_date')) or date.today(),
        overall_risk_score=data.get('overall_risk_score'),
        insurance_coverage_adequacy=data.get('insurance_coverage_adequacy'),
        liability_gaps_identified=data.get('liability_gaps_identified'),
        compliance_status=data.get('compliance_status'),
        recommendations=data.get('recommendations'),
        next_review_date=parse_date(data.get('next_review_date')),
        assessed_by=data.get('assessed_by'),
        notes=data.get('notes')
    )
    
    db.session.add(assessment)
    db.session.commit()
    
    return jsonify(assessment.to_dict()), 201

# Alerts endpoints
@liability_bp.route('/alerts', methods=['GET'])
def get_alerts():
    """Get alerts for a user"""
    user_id = request.args.get('user_id', 1)
    unread_only = request.args.get('unread_only', 'false').lower() == 'true'
    
    query = Alert.query.filter_by(user_id=user_id)
    if unread_only:
        query = query.filter_by(is_read=False)
    
    alerts = query.order_by(Alert.created_at.desc()).all()
    return jsonify([alert.to_dict() for alert in alerts])

@liability_bp.route('/alerts/<int:alert_id>/mark-read', methods=['PUT'])
def mark_alert_read(alert_id):
    """Mark an alert as read"""
    alert = Alert.query.get_or_404(alert_id)
    alert.is_read = True
    db.session.commit()
    return jsonify(alert.to_dict())

@liability_bp.route('/alerts/<int:alert_id>/resolve', methods=['PUT'])
def resolve_alert(alert_id):
    """Resolve an alert"""
    alert = Alert.query.get_or_404(alert_id)
    alert.is_resolved = True
    alert.resolved_at = datetime.utcnow()
    db.session.commit()
    return jsonify(alert.to_dict())

# Dashboard endpoints for liability and compliance
@liability_bp.route('/dashboard/liability-overview', methods=['GET'])
def get_liability_overview():
    """Get liability overview for dashboard"""
    user_id = request.args.get('user_id', 1)
    
    # Get projects for user
    projects = db.session.query(Project).join(Property).filter(Property.user_id == user_id).all()
    project_ids = [p.id for p in projects]
    
    if not project_ids:
        return jsonify({
            'total_projects': 0,
            'high_risk_projects': 0,
            'insurance_gaps': 0,
            'compliance_issues': 0,
            'expiring_soon': 0
        })
    
    # Count high-risk projects (based on latest risk assessments)
    high_risk_count = 0
    for project_id in project_ids:
        latest_assessment = RiskAssessment.query.filter_by(project_id=project_id).order_by(RiskAssessment.assessment_date.desc()).first()
        if latest_assessment and latest_assessment.overall_risk_score and latest_assessment.overall_risk_score >= 7:
            high_risk_count += 1
    
    # Count insurance gaps (stakeholders without adequate insurance)
    insurance_gaps = 0
    stakeholders = ProjectStakeholder.query.filter(ProjectStakeholder.project_id.in_(project_ids)).all()
    for stakeholder in stakeholders:
        if not stakeholder.insurance_policies or not any(ins.status == 'Active' for ins in stakeholder.insurance_policies):
            insurance_gaps += 1
    
    # Count compliance issues (expired or expiring compliance items)
    today = date.today()
    upcoming_date = today + timedelta(days=30)
    
    compliance_issues = ComplianceItem.query.filter(
        ComplianceItem.project_id.in_(project_ids),
        ComplianceItem.status.in_(['Expired', 'Pending'])
    ).count()
    
    expiring_soon = ComplianceItem.query.filter(
        ComplianceItem.project_id.in_(project_ids),
        ComplianceItem.expiry_date.isnot(None),
        ComplianceItem.expiry_date <= upcoming_date,
        ComplianceItem.expiry_date >= today
    ).count()
    
    return jsonify({
        'total_projects': len(projects),
        'high_risk_projects': high_risk_count,
        'insurance_gaps': insurance_gaps,
        'compliance_issues': compliance_issues,
        'expiring_soon': expiring_soon
    })

@liability_bp.route('/dashboard/expiring-items', methods=['GET'])
def get_expiring_items():
    """Get items expiring soon"""
    user_id = request.args.get('user_id', 1)
    days_ahead = int(request.args.get('days_ahead', 90))
    
    # Get projects for user
    projects = db.session.query(Project).join(Property).filter(Property.user_id == user_id).all()
    project_ids = [p.id for p in projects]
    
    if not project_ids:
        return jsonify([])
    
    today = date.today()
    upcoming_date = today + timedelta(days=days_ahead)
    
    expiring_items = []
    
    # Get expiring compliance items
    compliance_items = ComplianceItem.query.filter(
        ComplianceItem.project_id.in_(project_ids),
        ComplianceItem.expiry_date.isnot(None),
        ComplianceItem.expiry_date <= upcoming_date,
        ComplianceItem.expiry_date >= today
    ).all()
    
    for item in compliance_items:
        days_left = (item.expiry_date - today).days
        expiring_items.append({
            'type': 'compliance',
            'name': f"{item.compliance_type} - {item.certificate_number or 'N/A'}",
            'category': item.compliance_type,
            'expiry_date': item.expiry_date.isoformat(),
            'days_left': days_left,
            'project_id': item.project_id,
            'severity': 'high' if days_left <= 30 else 'medium'
        })
    
    # Get expiring insurance policies
    stakeholders = ProjectStakeholder.query.filter(ProjectStakeholder.project_id.in_(project_ids)).all()
    for stakeholder in stakeholders:
        for insurance in stakeholder.insurance_policies:
            if insurance.end_date and insurance.end_date <= upcoming_date and insurance.end_date >= today:
                days_left = (insurance.end_date - today).days
                expiring_items.append({
                    'type': 'insurance',
                    'name': f"{insurance.insurance_type} - {stakeholder.company_name}",
                    'category': insurance.insurance_type,
                    'expiry_date': insurance.end_date.isoformat(),
                    'days_left': days_left,
                    'project_id': stakeholder.project_id,
                    'severity': 'high' if days_left <= 30 else 'medium'
                })
    
    # Sort by expiry date
    expiring_items.sort(key=lambda x: x['expiry_date'])
    
    return jsonify(expiring_items)

