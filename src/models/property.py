from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from src.models.user import db

class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(500), nullable=False)
    property_type = db.Column(db.String(100), nullable=False)
    purchase_date = db.Column(db.Date)
    estimated_value = db.Column(db.Float)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    documents = db.relationship('Document', backref='property', lazy=True, cascade='all, delete-orphan')
    warranties = db.relationship('Warranty', backref='property', lazy=True, cascade='all, delete-orphan')
    maintenance_tasks = db.relationship('MaintenanceTask', backref='property', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'property_type': self.property_type,
            'purchase_date': self.purchase_date.isoformat() if self.purchase_date else None,
            'estimated_value': self.estimated_value,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat()
        }

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    document_type = db.Column(db.String(100), nullable=False)  # Insurance, Warranty, COC, Plans, Report, etc.
    category = db.Column(db.String(100), nullable=False)  # Kitchen, HVAC, Electrical, General, etc.
    file_path = db.Column(db.String(500))  # Path to uploaded file
    file_name = db.Column(db.String(200))  # Original filename
    file_size = db.Column(db.Integer)  # File size in bytes
    mime_type = db.Column(db.String(100))  # MIME type of the file
    upload_date = db.Column(db.Date, default=datetime.utcnow)
    expiry_date = db.Column(db.Date)
    notes = db.Column(db.Text)
    tags = db.Column(db.String(500))  # Comma-separated tags
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'document_type': self.document_type,
            'category': self.category,
            'file_path': self.file_path,
            'file_name': self.file_name,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'upload_date': self.upload_date.isoformat() if self.upload_date else None,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'notes': self.notes,
            'tags': self.tags.split(',') if self.tags else [],
            'property_id': self.property_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Warranty(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(200), nullable=False)
    manufacturer = db.Column(db.String(200))
    model_number = db.Column(db.String(100))
    serial_number = db.Column(db.String(100))
    purchase_date = db.Column(db.Date)
    warranty_start_date = db.Column(db.Date)
    warranty_end_date = db.Column(db.Date)
    warranty_period_months = db.Column(db.Integer)
    category = db.Column(db.String(100), nullable=False)  # HVAC, Appliances, Electronics, etc.
    purchase_price = db.Column(db.Float)
    retailer = db.Column(db.String(200))
    warranty_type = db.Column(db.String(100))  # Manufacturer, Extended, Service Plan
    contact_info = db.Column(db.Text)  # Contact information for warranty claims
    notes = db.Column(db.Text)
    status = db.Column(db.String(50), default='Active')  # Active, Expired, Claimed
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    document_id = db.Column(db.Integer, db.ForeignKey('document.id'))  # Link to warranty document
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'product_name': self.product_name,
            'manufacturer': self.manufacturer,
            'model_number': self.model_number,
            'serial_number': self.serial_number,
            'purchase_date': self.purchase_date.isoformat() if self.purchase_date else None,
            'warranty_start_date': self.warranty_start_date.isoformat() if self.warranty_start_date else None,
            'warranty_end_date': self.warranty_end_date.isoformat() if self.warranty_end_date else None,
            'warranty_period_months': self.warranty_period_months,
            'category': self.category,
            'purchase_price': self.purchase_price,
            'retailer': self.retailer,
            'warranty_type': self.warranty_type,
            'contact_info': self.contact_info,
            'notes': self.notes,
            'status': self.status,
            'property_id': self.property_id,
            'document_id': self.document_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class MaintenanceTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100))  # HVAC, Plumbing, Electrical, General, etc.
    priority = db.Column(db.String(50), default='Medium')  # Low, Medium, High, Urgent
    status = db.Column(db.String(50), default='Pending')  # Pending, In Progress, Completed, Cancelled
    due_date = db.Column(db.Date)
    completed_date = db.Column(db.Date)
    estimated_cost = db.Column(db.Float)
    actual_cost = db.Column(db.Float)
    contractor_name = db.Column(db.String(200))
    contractor_contact = db.Column(db.String(200))
    notes = db.Column(db.Text)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'priority': self.priority,
            'status': self.status,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'completed_date': self.completed_date.isoformat() if self.completed_date else None,
            'estimated_cost': self.estimated_cost,
            'actual_cost': self.actual_cost,
            'contractor_name': self.contractor_name,
            'contractor_contact': self.contractor_contact,
            'notes': self.notes,
            'property_id': self.property_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Contractor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    company = db.Column(db.String(200))
    phone = db.Column(db.String(50))
    email = db.Column(db.String(120))
    address = db.Column(db.String(500))
    specialties = db.Column(db.String(500))  # Comma-separated specialties
    license_number = db.Column(db.String(100))
    insurance_info = db.Column(db.Text)
    rating = db.Column(db.Float)  # 1-5 star rating
    notes = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'company': self.company,
            'phone': self.phone,
            'email': self.email,
            'address': self.address,
            'specialties': self.specialties.split(',') if self.specialties else [],
            'license_number': self.license_number,
            'insurance_info': self.insurance_info,
            'rating': self.rating,
            'notes': self.notes,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

