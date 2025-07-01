from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.property import Property, Document, Warranty, MaintenanceTask, Contractor
from datetime import datetime, date
import os
from werkzeug.utils import secure_filename

property_bp = Blueprint('property', __name__)

# Helper function to parse date strings
def parse_date(date_string):
    if not date_string:
        return None
    try:
        return datetime.strptime(date_string, '%Y-%m-%d').date()
    except ValueError:
        return None

# Properties endpoints
@property_bp.route('/properties', methods=['GET'])
def get_properties():
    """Get all properties for a user"""
    user_id = request.args.get('user_id', 1)  # Default to user 1 for demo
    properties = Property.query.filter_by(user_id=user_id).all()
    return jsonify([prop.to_dict() for prop in properties])

@property_bp.route('/properties', methods=['POST'])
def create_property():
    """Create a new property"""
    data = request.get_json()
    
    property = Property(
        name=data.get('name'),
        address=data.get('address'),
        property_type=data.get('property_type'),
        purchase_date=parse_date(data.get('purchase_date')),
        estimated_value=data.get('estimated_value'),
        user_id=data.get('user_id', 1)  # Default to user 1 for demo
    )
    
    db.session.add(property)
    db.session.commit()
    
    return jsonify(property.to_dict()), 201

@property_bp.route('/properties/<int:property_id>', methods=['GET'])
def get_property(property_id):
    """Get a specific property"""
    property = Property.query.get_or_404(property_id)
    return jsonify(property.to_dict())

@property_bp.route('/properties/<int:property_id>', methods=['PUT'])
def update_property(property_id):
    """Update a property"""
    property = Property.query.get_or_404(property_id)
    data = request.get_json()
    
    property.name = data.get('name', property.name)
    property.address = data.get('address', property.address)
    property.property_type = data.get('property_type', property.property_type)
    property.purchase_date = parse_date(data.get('purchase_date')) or property.purchase_date
    property.estimated_value = data.get('estimated_value', property.estimated_value)
    
    db.session.commit()
    return jsonify(property.to_dict())

@property_bp.route('/properties/<int:property_id>', methods=['DELETE'])
def delete_property(property_id):
    """Delete a property"""
    property = Property.query.get_or_404(property_id)
    db.session.delete(property)
    db.session.commit()
    return '', 204

# Documents endpoints
@property_bp.route('/properties/<int:property_id>/documents', methods=['GET'])
def get_documents(property_id):
    """Get all documents for a property"""
    documents = Document.query.filter_by(property_id=property_id).all()
    return jsonify([doc.to_dict() for doc in documents])

@property_bp.route('/documents', methods=['GET'])
def get_all_documents():
    """Get all documents with optional filtering"""
    user_id = request.args.get('user_id', 1)
    document_type = request.args.get('type')
    category = request.args.get('category')
    search = request.args.get('search')
    
    # Join with Property to filter by user
    query = db.session.query(Document).join(Property).filter(Property.user_id == user_id)
    
    if document_type:
        query = query.filter(Document.document_type == document_type)
    if category:
        query = query.filter(Document.category == category)
    if search:
        query = query.filter(Document.name.contains(search))
    
    documents = query.all()
    return jsonify([doc.to_dict() for doc in documents])

@property_bp.route('/properties/<int:property_id>/documents', methods=['POST'])
def create_document(property_id):
    """Create a new document"""
    data = request.get_json()
    
    document = Document(
        name=data.get('name'),
        document_type=data.get('document_type'),
        category=data.get('category'),
        file_path=data.get('file_path'),
        file_name=data.get('file_name'),
        file_size=data.get('file_size'),
        mime_type=data.get('mime_type'),
        upload_date=parse_date(data.get('upload_date')) or date.today(),
        expiry_date=parse_date(data.get('expiry_date')),
        notes=data.get('notes'),
        tags=','.join(data.get('tags', [])) if isinstance(data.get('tags'), list) else data.get('tags'),
        property_id=property_id
    )
    
    db.session.add(document)
    db.session.commit()
    
    return jsonify(document.to_dict()), 201

@property_bp.route('/documents/<int:document_id>', methods=['PUT'])
def update_document(document_id):
    """Update a document"""
    document = Document.query.get_or_404(document_id)
    data = request.get_json()
    
    document.name = data.get('name', document.name)
    document.document_type = data.get('document_type', document.document_type)
    document.category = data.get('category', document.category)
    document.expiry_date = parse_date(data.get('expiry_date')) or document.expiry_date
    document.notes = data.get('notes', document.notes)
    document.tags = ','.join(data.get('tags', [])) if isinstance(data.get('tags'), list) else data.get('tags', document.tags)
    document.updated_at = datetime.utcnow()
    
    db.session.commit()
    return jsonify(document.to_dict())

@property_bp.route('/documents/<int:document_id>', methods=['DELETE'])
def delete_document(document_id):
    """Delete a document"""
    document = Document.query.get_or_404(document_id)
    db.session.delete(document)
    db.session.commit()
    return '', 204

# Warranties endpoints
@property_bp.route('/properties/<int:property_id>/warranties', methods=['GET'])
def get_warranties(property_id):
    """Get all warranties for a property"""
    warranties = Warranty.query.filter_by(property_id=property_id).all()
    return jsonify([warranty.to_dict() for warranty in warranties])

@property_bp.route('/warranties', methods=['GET'])
def get_all_warranties():
    """Get all warranties with optional filtering"""
    user_id = request.args.get('user_id', 1)
    status = request.args.get('status')
    category = request.args.get('category')
    
    # Join with Property to filter by user
    query = db.session.query(Warranty).join(Property).filter(Property.user_id == user_id)
    
    if status:
        query = query.filter(Warranty.status == status)
    if category:
        query = query.filter(Warranty.category == category)
    
    warranties = query.all()
    return jsonify([warranty.to_dict() for warranty in warranties])

@property_bp.route('/properties/<int:property_id>/warranties', methods=['POST'])
def create_warranty(property_id):
    """Create a new warranty"""
    data = request.get_json()
    
    warranty = Warranty(
        product_name=data.get('product_name'),
        manufacturer=data.get('manufacturer'),
        model_number=data.get('model_number'),
        serial_number=data.get('serial_number'),
        purchase_date=parse_date(data.get('purchase_date')),
        warranty_start_date=parse_date(data.get('warranty_start_date')),
        warranty_end_date=parse_date(data.get('warranty_end_date')),
        warranty_period_months=data.get('warranty_period_months'),
        category=data.get('category'),
        purchase_price=data.get('purchase_price'),
        retailer=data.get('retailer'),
        warranty_type=data.get('warranty_type'),
        contact_info=data.get('contact_info'),
        notes=data.get('notes'),
        status=data.get('status', 'Active'),
        property_id=property_id,
        document_id=data.get('document_id')
    )
    
    db.session.add(warranty)
    db.session.commit()
    
    return jsonify(warranty.to_dict()), 201

@property_bp.route('/warranties/<int:warranty_id>', methods=['PUT'])
def update_warranty(warranty_id):
    """Update a warranty"""
    warranty = Warranty.query.get_or_404(warranty_id)
    data = request.get_json()
    
    warranty.product_name = data.get('product_name', warranty.product_name)
    warranty.manufacturer = data.get('manufacturer', warranty.manufacturer)
    warranty.model_number = data.get('model_number', warranty.model_number)
    warranty.serial_number = data.get('serial_number', warranty.serial_number)
    warranty.purchase_date = parse_date(data.get('purchase_date')) or warranty.purchase_date
    warranty.warranty_start_date = parse_date(data.get('warranty_start_date')) or warranty.warranty_start_date
    warranty.warranty_end_date = parse_date(data.get('warranty_end_date')) or warranty.warranty_end_date
    warranty.warranty_period_months = data.get('warranty_period_months', warranty.warranty_period_months)
    warranty.category = data.get('category', warranty.category)
    warranty.purchase_price = data.get('purchase_price', warranty.purchase_price)
    warranty.retailer = data.get('retailer', warranty.retailer)
    warranty.warranty_type = data.get('warranty_type', warranty.warranty_type)
    warranty.contact_info = data.get('contact_info', warranty.contact_info)
    warranty.notes = data.get('notes', warranty.notes)
    warranty.status = data.get('status', warranty.status)
    warranty.document_id = data.get('document_id', warranty.document_id)
    warranty.updated_at = datetime.utcnow()
    
    db.session.commit()
    return jsonify(warranty.to_dict())

@property_bp.route('/warranties/<int:warranty_id>', methods=['DELETE'])
def delete_warranty(warranty_id):
    """Delete a warranty"""
    warranty = Warranty.query.get_or_404(warranty_id)
    db.session.delete(warranty)
    db.session.commit()
    return '', 204

# Dashboard endpoints
@property_bp.route('/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    """Get dashboard statistics"""
    user_id = request.args.get('user_id', 1)
    
    # Count documents by joining with Property
    total_documents = db.session.query(Document).join(Property).filter(Property.user_id == user_id).count()
    
    # Count active warranties
    active_warranties = db.session.query(Warranty).join(Property).filter(
        Property.user_id == user_id,
        Warranty.status == 'Active'
    ).count()
    
    # Count upcoming expirations (next 60 days)
    from datetime import timedelta
    upcoming_date = date.today() + timedelta(days=60)
    upcoming_expirations = db.session.query(Document).join(Property).filter(
        Property.user_id == user_id,
        Document.expiry_date.isnot(None),
        Document.expiry_date <= upcoming_date,
        Document.expiry_date >= date.today()
    ).count()
    
    # Get property value (sum of all properties)
    total_value = db.session.query(db.func.sum(Property.estimated_value)).filter(
        Property.user_id == user_id
    ).scalar() or 0
    
    return jsonify({
        'total_documents': total_documents,
        'active_warranties': active_warranties,
        'upcoming_expirations': upcoming_expirations,
        'total_property_value': total_value
    })

@property_bp.route('/dashboard/recent-documents', methods=['GET'])
def get_recent_documents():
    """Get recent documents for dashboard"""
    user_id = request.args.get('user_id', 1)
    limit = request.args.get('limit', 5)
    
    documents = db.session.query(Document).join(Property).filter(
        Property.user_id == user_id
    ).order_by(Document.created_at.desc()).limit(limit).all()
    
    return jsonify([doc.to_dict() for doc in documents])

@property_bp.route('/dashboard/upcoming-expirations', methods=['GET'])
def get_upcoming_expirations():
    """Get upcoming expirations for dashboard"""
    user_id = request.args.get('user_id', 1)
    
    from datetime import timedelta
    upcoming_date = date.today() + timedelta(days=90)
    
    # Get documents with upcoming expirations
    documents = db.session.query(Document).join(Property).filter(
        Property.user_id == user_id,
        Document.expiry_date.isnot(None),
        Document.expiry_date <= upcoming_date,
        Document.expiry_date >= date.today()
    ).order_by(Document.expiry_date.asc()).all()
    
    # Get warranties with upcoming expirations
    warranties = db.session.query(Warranty).join(Property).filter(
        Property.user_id == user_id,
        Warranty.warranty_end_date.isnot(None),
        Warranty.warranty_end_date <= upcoming_date,
        Warranty.warranty_end_date >= date.today(),
        Warranty.status == 'Active'
    ).order_by(Warranty.warranty_end_date.asc()).all()
    
    # Combine and format results
    expirations = []
    
    for doc in documents:
        days_left = (doc.expiry_date - date.today()).days
        expirations.append({
            'type': 'document',
            'name': doc.name,
            'category': doc.document_type,
            'expiry_date': doc.expiry_date.isoformat(),
            'days_left': days_left
        })
    
    for warranty in warranties:
        days_left = (warranty.warranty_end_date - date.today()).days
        expirations.append({
            'type': 'warranty',
            'name': warranty.product_name,
            'category': warranty.category,
            'expiry_date': warranty.warranty_end_date.isoformat(),
            'days_left': days_left
        })
    
    # Sort by expiry date
    expirations.sort(key=lambda x: x['expiry_date'])
    
    return jsonify(expirations)

