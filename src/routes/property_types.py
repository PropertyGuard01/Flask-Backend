from flask import Blueprint, request, jsonify
from src.models.property_types import (
    db, EnhancedProperty, PropertyType, OwnershipType, FloorLevel,
    ComplianceItem, SharedResponsibility, CouncilDocument,
    PropertyDocumentationGap, MunicipalityIntegration,
    get_applicable_compliance_items, calculate_documentation_score,
    identify_documentation_gaps
)
from datetime import datetime
import json

property_types_bp = Blueprint('property_types', __name__)

@property_types_bp.route('/property-types', methods=['GET'])
def get_property_types():
    """Get all available property types"""
    types = [{'value': pt.value, 'name': pt.name} for pt in PropertyType]
    ownership_types = [{'value': ot.value, 'name': ot.name} for ot in OwnershipType]
    floor_levels = [{'value': fl.value, 'name': fl.name} for fl in FloorLevel]
    
    return jsonify({
        'property_types': types,
        'ownership_types': ownership_types,
        'floor_levels': floor_levels
    })

@property_types_bp.route('/enhanced-properties', methods=['POST'])
def create_enhanced_property():
    """Create a new enhanced property with intelligent compliance mapping"""
    data = request.get_json()
    
    try:
        # Create the property
        property_obj = EnhancedProperty(
            user_id=data['user_id'],
            name=data['name'],
            address=data['address'],
            property_type=PropertyType(data['property_type']),
            ownership_type=OwnershipType(data['ownership_type']),
            floor_level=FloorLevel(data.get('floor_level')) if data.get('floor_level') else None,
            erf_number=data.get('erf_number'),
            stand_number=data.get('stand_number'),
            municipal_account_number=data.get('municipal_account_number'),
            zoning=data.get('zoning'),
            floor_area=data.get('floor_area'),
            land_area=data.get('land_area'),
            year_built=data.get('year_built'),
            number_of_bedrooms=data.get('number_of_bedrooms'),
            number_of_bathrooms=data.get('number_of_bathrooms'),
            unit_number=data.get('unit_number'),
            body_corporate_name=data.get('body_corporate_name'),
            levy_amount=data.get('levy_amount')
        )
        
        db.session.add(property_obj)
        db.session.flush()  # Get the ID
        
        # Generate applicable compliance items
        compliance_requirements = get_applicable_compliance_items(
            property_obj.property_type,
            property_obj.ownership_type,
            property_obj.floor_level
        )
        
        # Create compliance items
        for req in compliance_requirements:
            compliance_item = ComplianceItem(
                property_id=property_obj.id,
                name=req['name'],
                category=req['category'],
                is_individual_responsibility=req['individual_responsibility'],
                responsible_party="Owner" if req['individual_responsibility'] else "Body Corporate",
                is_required=True,
                is_compliant=False
            )
            db.session.add(compliance_item)
        
        # Identify initial documentation gaps
        identify_documentation_gaps(property_obj.id)
        
        # Calculate initial documentation score
        calculate_documentation_score(property_obj.id)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'property_id': property_obj.id,
            'message': 'Enhanced property created successfully',
            'compliance_items_created': len(compliance_requirements)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

@property_types_bp.route('/enhanced-properties/<int:property_id>', methods=['GET'])
def get_enhanced_property(property_id):
    """Get detailed property information with compliance status"""
    property_obj = EnhancedProperty.query.get_or_404(property_id)
    
    # Get compliance items
    compliance_items = ComplianceItem.query.filter_by(property_id=property_id).all()
    
    # Get shared responsibilities
    shared_responsibilities = SharedResponsibility.query.filter_by(property_id=property_id).all()
    
    # Get council documents
    council_documents = CouncilDocument.query.filter_by(property_id=property_id).all()
    
    # Get documentation gaps
    documentation_gaps = PropertyDocumentationGap.query.filter_by(
        property_id=property_id,
        is_resolved=False
    ).all()
    
    return jsonify({
        'property': {
            'id': property_obj.id,
            'name': property_obj.name,
            'address': property_obj.address,
            'property_type': property_obj.property_type.value,
            'ownership_type': property_obj.ownership_type.value,
            'floor_level': property_obj.floor_level.value if property_obj.floor_level else None,
            'erf_number': property_obj.erf_number,
            'stand_number': property_obj.stand_number,
            'municipal_account_number': property_obj.municipal_account_number,
            'zoning': property_obj.zoning,
            'floor_area': property_obj.floor_area,
            'land_area': property_obj.land_area,
            'year_built': property_obj.year_built,
            'number_of_bedrooms': property_obj.number_of_bedrooms,
            'number_of_bathrooms': property_obj.number_of_bathrooms,
            'unit_number': property_obj.unit_number,
            'body_corporate_name': property_obj.body_corporate_name,
            'levy_amount': property_obj.levy_amount,
            'documentation_score': property_obj.documentation_score,
            'council_data_imported': property_obj.council_data_imported,
            'created_at': property_obj.created_at.isoformat(),
            'updated_at': property_obj.updated_at.isoformat()
        },
        'compliance_items': [{
            'id': item.id,
            'name': item.name,
            'description': item.description,
            'category': item.category,
            'is_individual_responsibility': item.is_individual_responsibility,
            'responsible_party': item.responsible_party,
            'is_required': item.is_required,
            'is_compliant': item.is_compliant,
            'due_date': item.due_date.isoformat() if item.due_date else None,
            'last_inspection_date': item.last_inspection_date.isoformat() if item.last_inspection_date else None,
            'next_inspection_date': item.next_inspection_date.isoformat() if item.next_inspection_date else None,
            'certificate_number': item.certificate_number,
            'issuing_authority': item.issuing_authority
        } for item in compliance_items],
        'shared_responsibilities': [{
            'id': resp.id,
            'area_or_system': resp.area_or_system,
            'description': resp.description,
            'individual_percentage': resp.individual_percentage,
            'body_corporate_percentage': resp.body_corporate_percentage,
            'hoa_percentage': resp.hoa_percentage,
            'insurance_provider': resp.insurance_provider,
            'maintenance_schedule': resp.maintenance_schedule
        } for resp in shared_responsibilities],
        'council_documents': [{
            'id': doc.id,
            'document_type': doc.document_type,
            'document_name': doc.document_name,
            'description': doc.description,
            'municipality': doc.municipality,
            'reference_number': doc.reference_number,
            'approval_date': doc.approval_date.isoformat() if doc.approval_date else None,
            'import_method': doc.import_method,
            'verified': doc.verified
        } for doc in council_documents],
        'documentation_gaps': [{
            'id': gap.id,
            'gap_type': gap.gap_type,
            'description': gap.description,
            'severity': gap.severity,
            'estimated_cost_to_resolve': gap.estimated_cost_to_resolve,
            'identified_date': gap.identified_date.isoformat()
        } for gap in documentation_gaps]
    })

@property_types_bp.route('/enhanced-properties/<int:property_id>/compliance/<int:compliance_id>', methods=['PUT'])
def update_compliance_item(property_id, compliance_id):
    """Update a compliance item status"""
    compliance_item = ComplianceItem.query.filter_by(
        id=compliance_id,
        property_id=property_id
    ).first_or_404()
    
    data = request.get_json()
    
    # Update fields
    if 'is_compliant' in data:
        compliance_item.is_compliant = data['is_compliant']
    if 'certificate_number' in data:
        compliance_item.certificate_number = data['certificate_number']
    if 'issuing_authority' in data:
        compliance_item.issuing_authority = data['issuing_authority']
    if 'last_inspection_date' in data:
        compliance_item.last_inspection_date = datetime.fromisoformat(data['last_inspection_date'])
    if 'next_inspection_date' in data:
        compliance_item.next_inspection_date = datetime.fromisoformat(data['next_inspection_date'])
    if 'document_path' in data:
        compliance_item.document_path = data['document_path']
    
    compliance_item.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    # Recalculate documentation score
    new_score = calculate_documentation_score(property_id)
    
    return jsonify({
        'success': True,
        'message': 'Compliance item updated successfully',
        'new_documentation_score': new_score
    })

@property_types_bp.route('/enhanced-properties/<int:property_id>/council-import', methods=['POST'])
def import_council_data(property_id):
    """Import council data for a property (placeholder for future integration)"""
    property_obj = EnhancedProperty.query.get_or_404(property_id)
    data = request.get_json()
    
    municipality = data.get('municipality', 'Unknown Municipality')
    
    # Placeholder council documents (in real implementation, this would fetch from council APIs)
    sample_documents = [
        {
            'document_type': 'Building Plan',
            'document_name': f'Original Building Plan - {property_obj.erf_number}',
            'description': 'Original approved building plans from council records',
            'municipality': municipality,
            'reference_number': f'BP-{property_obj.erf_number}-{property_obj.year_built or "UNKNOWN"}',
            'import_method': 'manual'
        },
        {
            'document_type': 'Stand Plan',
            'document_name': f'Stand Plan - Erf {property_obj.erf_number}',
            'description': 'Official surveyed stand boundaries and measurements',
            'municipality': municipality,
            'reference_number': f'SP-{property_obj.erf_number}',
            'import_method': 'manual'
        }
    ]
    
    # Create council documents
    for doc_data in sample_documents:
        council_doc = CouncilDocument(
            property_id=property_id,
            **doc_data
        )
        db.session.add(council_doc)
    
    # Mark council data as imported
    property_obj.council_data_imported = True
    property_obj.council_data_import_date = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'Council data imported successfully for {municipality}',
        'documents_imported': len(sample_documents)
    })

@property_types_bp.route('/enhanced-properties/<int:property_id>/gaps/resolve/<int:gap_id>', methods=['PUT'])
def resolve_documentation_gap(property_id, gap_id):
    """Mark a documentation gap as resolved"""
    gap = PropertyDocumentationGap.query.filter_by(
        id=gap_id,
        property_id=property_id
    ).first_or_404()
    
    data = request.get_json()
    
    gap.is_resolved = True
    gap.resolution_date = datetime.utcnow()
    gap.resolution_notes = data.get('resolution_notes', '')
    gap.actual_cost_to_resolve = data.get('actual_cost_to_resolve')
    
    db.session.commit()
    
    # Recalculate documentation score
    new_score = calculate_documentation_score(property_id)
    
    return jsonify({
        'success': True,
        'message': 'Documentation gap resolved successfully',
        'new_documentation_score': new_score
    })

@property_types_bp.route('/enhanced-properties/<int:property_id>/shared-responsibilities', methods=['POST'])
def add_shared_responsibility(property_id):
    """Add a shared responsibility for sectional title properties"""
    property_obj = EnhancedProperty.query.get_or_404(property_id)
    data = request.get_json()
    
    shared_resp = SharedResponsibility(
        property_id=property_id,
        area_or_system=data['area_or_system'],
        description=data.get('description', ''),
        individual_percentage=data.get('individual_percentage', 0.0),
        body_corporate_percentage=data.get('body_corporate_percentage', 0.0),
        hoa_percentage=data.get('hoa_percentage', 0.0),
        insurance_provider=data.get('insurance_provider', ''),
        maintenance_schedule=data.get('maintenance_schedule', '')
    )
    
    db.session.add(shared_resp)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Shared responsibility added successfully',
        'shared_responsibility_id': shared_resp.id
    })

@property_types_bp.route('/municipalities', methods=['GET'])
def get_municipalities():
    """Get list of municipalities and their integration status"""
    municipalities = MunicipalityIntegration.query.all()
    
    return jsonify({
        'municipalities': [{
            'id': muni.id,
            'name': muni.municipality_name,
            'province': muni.province,
            'integration_status': muni.integration_status,
            'has_api_access': muni.has_api_access,
            'has_building_plans': muni.has_building_plans,
            'has_stand_plans': muni.has_stand_plans,
            'has_coc_records': muni.has_coc_records,
            'last_sync_date': muni.last_sync_date.isoformat() if muni.last_sync_date else None
        } for muni in municipalities]
    })

@property_types_bp.route('/enhanced-properties/<int:property_id>/documentation-score', methods=['GET'])
def get_documentation_score(property_id):
    """Get current documentation score and breakdown"""
    property_obj = EnhancedProperty.query.get_or_404(property_id)
    
    # Get compliance breakdown
    total_items = ComplianceItem.query.filter_by(property_id=property_id).count()
    compliant_items = ComplianceItem.query.filter_by(property_id=property_id, is_compliant=True).count()
    
    # Get gaps breakdown
    total_gaps = PropertyDocumentationGap.query.filter_by(property_id=property_id).count()
    resolved_gaps = PropertyDocumentationGap.query.filter_by(property_id=property_id, is_resolved=True).count()
    
    # Calculate current score
    current_score = calculate_documentation_score(property_id)
    
    return jsonify({
        'property_id': property_id,
        'documentation_score': current_score,
        'compliance_breakdown': {
            'total_items': total_items,
            'compliant_items': compliant_items,
            'compliance_percentage': (compliant_items / total_items * 100) if total_items > 0 else 0
        },
        'gaps_breakdown': {
            'total_gaps': total_gaps,
            'resolved_gaps': resolved_gaps,
            'resolution_percentage': (resolved_gaps / total_gaps * 100) if total_gaps > 0 else 100
        },
        'council_data_imported': property_obj.council_data_imported,
        'last_updated': property_obj.updated_at.isoformat()
    })

