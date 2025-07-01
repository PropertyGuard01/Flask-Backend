from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date, timedelta
from src.models.user import db
import json

class SubscriptionPlan(db.Model):
    """Subscription plans available for PropertyGuard.com"""
    id = db.Column(db.Integer, primary_key=True)
    plan_name = db.Column(db.String(100), unique=True, nullable=False)
    plan_code = db.Column(db.String(50), unique=True, nullable=False)  # starter, professional, enterprise
    
    # Pricing
    monthly_price = db.Column(db.Float, nullable=False)
    annual_price = db.Column(db.Float)  # Discounted annual pricing
    currency = db.Column(db.String(3), default='USD')  # USD, ZAR, EUR, etc.
    
    # Plan limits
    max_properties = db.Column(db.Integer)  # null = unlimited
    max_documents_per_property = db.Column(db.Integer)  # null = unlimited
    max_storage_gb = db.Column(db.Float)  # null = unlimited
    max_users = db.Column(db.Integer, default=1)  # Additional users for enterprise
    
    # Features included
    features_included = db.Column(db.Text)  # JSON list of features
    api_access = db.Column(db.Boolean, default=False)
    priority_support = db.Column(db.Boolean, default=False)
    white_label = db.Column(db.Boolean, default=False)
    custom_integrations = db.Column(db.Boolean, default=False)
    
    # Advanced features
    policy_analysis = db.Column(db.Boolean, default=True)
    compliance_tracking = db.Column(db.Boolean, default=True)
    risk_assessment = db.Column(db.Boolean, default=False)
    property_transfer = db.Column(db.Boolean, default=False)
    gap_insurance_marketplace = db.Column(db.Boolean, default=False)
    professional_network = db.Column(db.Boolean, default=False)
    
    # Plan status
    is_active = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    sort_order = db.Column(db.Integer, default=0)
    
    # Trial settings
    trial_days = db.Column(db.Integer, default=14)
    trial_features = db.Column(db.Text)  # JSON list of features available in trial
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    subscriptions = db.relationship('UserSubscription', backref='plan', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'plan_name': self.plan_name,
            'plan_code': self.plan_code,
            'monthly_price': self.monthly_price,
            'annual_price': self.annual_price,
            'currency': self.currency,
            'max_properties': self.max_properties,
            'max_documents_per_property': self.max_documents_per_property,
            'max_storage_gb': self.max_storage_gb,
            'max_users': self.max_users,
            'features_included': json.loads(self.features_included) if self.features_included else None,
            'api_access': self.api_access,
            'priority_support': self.priority_support,
            'white_label': self.white_label,
            'custom_integrations': self.custom_integrations,
            'policy_analysis': self.policy_analysis,
            'compliance_tracking': self.compliance_tracking,
            'risk_assessment': self.risk_assessment,
            'property_transfer': self.property_transfer,
            'gap_insurance_marketplace': self.gap_insurance_marketplace,
            'professional_network': self.professional_network,
            'is_active': self.is_active,
            'is_featured': self.is_featured,
            'trial_days': self.trial_days,
            'trial_features': json.loads(self.trial_features) if self.trial_features else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class UserSubscription(db.Model):
    """User subscription records"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey('subscription_plan.id'), nullable=False)
    
    # Subscription details
    subscription_status = db.Column(db.String(50), default='trial')  # trial, active, cancelled, expired, suspended
    billing_cycle = db.Column(db.String(20), default='monthly')  # monthly, annual
    
    # Dates
    trial_start_date = db.Column(db.Date)
    trial_end_date = db.Column(db.Date)
    subscription_start_date = db.Column(db.Date)
    subscription_end_date = db.Column(db.Date)
    next_billing_date = db.Column(db.Date)
    cancelled_date = db.Column(db.Date)
    
    # Pricing
    current_price = db.Column(db.Float)  # Price locked in at subscription time
    currency = db.Column(db.String(3), default='USD')
    
    # Payment details
    payment_method_id = db.Column(db.String(200))  # Stripe payment method ID
    customer_id = db.Column(db.String(200))  # Stripe customer ID
    subscription_id = db.Column(db.String(200))  # Stripe subscription ID
    
    # Usage tracking
    properties_count = db.Column(db.Integer, default=0)
    documents_count = db.Column(db.Integer, default=0)
    storage_used_gb = db.Column(db.Float, default=0.0)
    api_calls_this_month = db.Column(db.Integer, default=0)
    
    # Cancellation details
    cancellation_reason = db.Column(db.String(500))
    cancelled_by_user = db.Column(db.Boolean, default=True)
    
    # Auto-renewal
    auto_renew = db.Column(db.Boolean, default=True)
    renewal_reminder_sent = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    payments = db.relationship('Payment', backref='subscription', lazy=True)
    usage_logs = db.relationship('UsageLog', backref='subscription', lazy=True)

    def is_trial_active(self):
        if self.subscription_status == 'trial' and self.trial_end_date:
            return date.today() <= self.trial_end_date
        return False

    def is_subscription_active(self):
        return self.subscription_status == 'active' and (
            not self.subscription_end_date or date.today() <= self.subscription_end_date
        )

    def days_until_expiry(self):
        if self.subscription_status == 'trial' and self.trial_end_date:
            return (self.trial_end_date - date.today()).days
        elif self.subscription_status == 'active' and self.subscription_end_date:
            return (self.subscription_end_date - date.today()).days
        return None

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'plan_id': self.plan_id,
            'subscription_status': self.subscription_status,
            'billing_cycle': self.billing_cycle,
            'trial_start_date': self.trial_start_date.isoformat() if self.trial_start_date else None,
            'trial_end_date': self.trial_end_date.isoformat() if self.trial_end_date else None,
            'subscription_start_date': self.subscription_start_date.isoformat() if self.subscription_start_date else None,
            'subscription_end_date': self.subscription_end_date.isoformat() if self.subscription_end_date else None,
            'next_billing_date': self.next_billing_date.isoformat() if self.next_billing_date else None,
            'current_price': self.current_price,
            'currency': self.currency,
            'properties_count': self.properties_count,
            'documents_count': self.documents_count,
            'storage_used_gb': self.storage_used_gb,
            'api_calls_this_month': self.api_calls_this_month,
            'auto_renew': self.auto_renew,
            'is_trial_active': self.is_trial_active(),
            'is_subscription_active': self.is_subscription_active(),
            'days_until_expiry': self.days_until_expiry(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Payment(db.Model):
    """Payment transaction records"""
    id = db.Column(db.Integer, primary_key=True)
    subscription_id = db.Column(db.Integer, db.ForeignKey('user_subscription.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Payment details
    payment_intent_id = db.Column(db.String(200))  # Stripe payment intent ID
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), nullable=False)
    payment_status = db.Column(db.String(50), default='pending')  # pending, succeeded, failed, cancelled
    
    # Payment method
    payment_method = db.Column(db.String(50))  # card, bank_transfer, etc.
    payment_method_details = db.Column(db.Text)  # JSON with payment method details
    
    # Billing period
    billing_period_start = db.Column(db.Date)
    billing_period_end = db.Column(db.Date)
    
    # Transaction details
    transaction_fee = db.Column(db.Float, default=0.0)
    net_amount = db.Column(db.Float)  # Amount after fees
    tax_amount = db.Column(db.Float, default=0.0)
    
    # Failure details
    failure_reason = db.Column(db.String(500))
    failure_code = db.Column(db.String(100))
    
    # Refund details
    refunded_amount = db.Column(db.Float, default=0.0)
    refund_reason = db.Column(db.String(500))
    refund_date = db.Column(db.DateTime)
    
    # Invoice details
    invoice_number = db.Column(db.String(100))
    invoice_url = db.Column(db.String(500))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'subscription_id': self.subscription_id,
            'user_id': self.user_id,
            'payment_intent_id': self.payment_intent_id,
            'amount': self.amount,
            'currency': self.currency,
            'payment_status': self.payment_status,
            'payment_method': self.payment_method,
            'payment_method_details': json.loads(self.payment_method_details) if self.payment_method_details else None,
            'billing_period_start': self.billing_period_start.isoformat() if self.billing_period_start else None,
            'billing_period_end': self.billing_period_end.isoformat() if self.billing_period_end else None,
            'transaction_fee': self.transaction_fee,
            'net_amount': self.net_amount,
            'tax_amount': self.tax_amount,
            'failure_reason': self.failure_reason,
            'refunded_amount': self.refunded_amount,
            'invoice_number': self.invoice_number,
            'invoice_url': self.invoice_url,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class UsageLog(db.Model):
    """Track feature usage for billing and analytics"""
    id = db.Column(db.Integer, primary_key=True)
    subscription_id = db.Column(db.Integer, db.ForeignKey('user_subscription.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Usage details
    feature_used = db.Column(db.String(100), nullable=False)  # policy_analysis, risk_assessment, etc.
    usage_type = db.Column(db.String(50), nullable=False)  # api_call, document_upload, analysis, etc.
    usage_count = db.Column(db.Integer, default=1)
    
    # Resource consumption
    storage_used_mb = db.Column(db.Float, default=0.0)
    processing_time_seconds = db.Column(db.Float, default=0.0)
    
    # Context
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'))
    document_id = db.Column(db.Integer, db.ForeignKey('document.id'))
    
    # Metadata
    user_agent = db.Column(db.String(500))
    ip_address = db.Column(db.String(45))
    session_id = db.Column(db.String(200))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'subscription_id': self.subscription_id,
            'user_id': self.user_id,
            'feature_used': self.feature_used,
            'usage_type': self.usage_type,
            'usage_count': self.usage_count,
            'storage_used_mb': self.storage_used_mb,
            'processing_time_seconds': self.processing_time_seconds,
            'property_id': self.property_id,
            'document_id': self.document_id,
            'created_at': self.created_at.isoformat()
        }

class FeatureFlag(db.Model):
    """Feature flags for A/B testing and gradual rollouts"""
    id = db.Column(db.Integer, primary_key=True)
    flag_name = db.Column(db.String(100), unique=True, nullable=False)
    flag_description = db.Column(db.String(500))
    
    # Flag configuration
    is_enabled = db.Column(db.Boolean, default=False)
    rollout_percentage = db.Column(db.Float, default=0.0)  # 0-100%
    
    # Targeting
    target_plans = db.Column(db.Text)  # JSON list of plan codes
    target_user_segments = db.Column(db.Text)  # JSON list of user segments
    target_regions = db.Column(db.Text)  # JSON list of region codes
    
    # A/B testing
    ab_test_active = db.Column(db.Boolean, default=False)
    ab_test_variants = db.Column(db.Text)  # JSON object with variant configurations
    
    # Scheduling
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'flag_name': self.flag_name,
            'flag_description': self.flag_description,
            'is_enabled': self.is_enabled,
            'rollout_percentage': self.rollout_percentage,
            'target_plans': json.loads(self.target_plans) if self.target_plans else None,
            'target_user_segments': json.loads(self.target_user_segments) if self.target_user_segments else None,
            'target_regions': json.loads(self.target_regions) if self.target_regions else None,
            'ab_test_active': self.ab_test_active,
            'ab_test_variants': json.loads(self.ab_test_variants) if self.ab_test_variants else None,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Coupon(db.Model):
    """Discount coupons and promotional codes"""
    id = db.Column(db.Integer, primary_key=True)
    coupon_code = db.Column(db.String(50), unique=True, nullable=False)
    coupon_name = db.Column(db.String(200))
    
    # Discount details
    discount_type = db.Column(db.String(20), nullable=False)  # percentage, fixed_amount
    discount_value = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='USD')
    
    # Usage limits
    max_uses = db.Column(db.Integer)  # null = unlimited
    max_uses_per_user = db.Column(db.Integer, default=1)
    current_uses = db.Column(db.Integer, default=0)
    
    # Validity
    valid_from = db.Column(db.DateTime)
    valid_until = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    # Targeting
    applicable_plans = db.Column(db.Text)  # JSON list of plan codes
    minimum_purchase_amount = db.Column(db.Float)
    first_time_users_only = db.Column(db.Boolean, default=False)
    
    # Tracking
    created_by = db.Column(db.String(200))
    campaign_name = db.Column(db.String(200))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    coupon_uses = db.relationship('CouponUse', backref='coupon', lazy=True)

    def is_valid(self):
        now = datetime.utcnow()
        return (
            self.is_active and
            (not self.valid_from or now >= self.valid_from) and
            (not self.valid_until or now <= self.valid_until) and
            (not self.max_uses or self.current_uses < self.max_uses)
        )

    def to_dict(self):
        return {
            'id': self.id,
            'coupon_code': self.coupon_code,
            'coupon_name': self.coupon_name,
            'discount_type': self.discount_type,
            'discount_value': self.discount_value,
            'currency': self.currency,
            'max_uses': self.max_uses,
            'max_uses_per_user': self.max_uses_per_user,
            'current_uses': self.current_uses,
            'valid_from': self.valid_from.isoformat() if self.valid_from else None,
            'valid_until': self.valid_until.isoformat() if self.valid_until else None,
            'is_active': self.is_active,
            'applicable_plans': json.loads(self.applicable_plans) if self.applicable_plans else None,
            'minimum_purchase_amount': self.minimum_purchase_amount,
            'first_time_users_only': self.first_time_users_only,
            'campaign_name': self.campaign_name,
            'is_valid': self.is_valid(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class CouponUse(db.Model):
    """Track coupon usage"""
    id = db.Column(db.Integer, primary_key=True)
    coupon_id = db.Column(db.Integer, db.ForeignKey('coupon.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subscription_id = db.Column(db.Integer, db.ForeignKey('user_subscription.id'))
    payment_id = db.Column(db.Integer, db.ForeignKey('payment.id'))
    
    # Usage details
    discount_amount = db.Column(db.Float, nullable=False)
    original_amount = db.Column(db.Float, nullable=False)
    final_amount = db.Column(db.Float, nullable=False)
    
    used_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'coupon_id': self.coupon_id,
            'user_id': self.user_id,
            'subscription_id': self.subscription_id,
            'payment_id': self.payment_id,
            'discount_amount': self.discount_amount,
            'original_amount': self.original_amount,
            'final_amount': self.final_amount,
            'used_at': self.used_at.isoformat()
        }

class ReferralProgram(db.Model):
    """Referral program for user acquisition"""
    id = db.Column(db.Integer, primary_key=True)
    referrer_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    referred_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Referral details
    referral_code = db.Column(db.String(50), unique=True, nullable=False)
    referral_email = db.Column(db.String(120))  # Email of referred person
    referral_status = db.Column(db.String(50), default='pending')  # pending, signed_up, converted, expired
    
    # Rewards
    referrer_reward_type = db.Column(db.String(50))  # discount, credit, free_months
    referrer_reward_value = db.Column(db.Float)
    referrer_reward_applied = db.Column(db.Boolean, default=False)
    
    referred_reward_type = db.Column(db.String(50))
    referred_reward_value = db.Column(db.Float)
    referred_reward_applied = db.Column(db.Boolean, default=False)
    
    # Tracking
    signup_date = db.Column(db.DateTime)
    conversion_date = db.Column(db.DateTime)  # When referred user becomes paying customer
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'referrer_user_id': self.referrer_user_id,
            'referred_user_id': self.referred_user_id,
            'referral_code': self.referral_code,
            'referral_email': self.referral_email,
            'referral_status': self.referral_status,
            'referrer_reward_type': self.referrer_reward_type,
            'referrer_reward_value': self.referrer_reward_value,
            'referrer_reward_applied': self.referrer_reward_applied,
            'referred_reward_type': self.referred_reward_type,
            'referred_reward_value': self.referred_reward_value,
            'referred_reward_applied': self.referred_reward_applied,
            'signup_date': self.signup_date.isoformat() if self.signup_date else None,
            'conversion_date': self.conversion_date.isoformat() if self.conversion_date else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

