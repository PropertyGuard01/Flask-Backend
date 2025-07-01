from flask import Blueprint, request, jsonify, current_app
from flask_cors import cross_origin
from src.models.user import db, User
from src.models.subscription import (
    SubscriptionPlan, UserSubscription, Payment, UsageLog, 
    FeatureFlag, Coupon, CouponUse, ReferralProgram
)
from datetime import datetime, date, timedelta
import json
import secrets
import string

subscription_bp = Blueprint('subscription', __name__)

@subscription_bp.route('/plans', methods=['GET'])
@cross_origin()
def get_subscription_plans():
    """Get all active subscription plans"""
    try:
        plans = SubscriptionPlan.query.filter_by(is_active=True).order_by(SubscriptionPlan.sort_order).all()
        return jsonify({
            'success': True,
            'plans': [plan.to_dict() for plan in plans]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@subscription_bp.route('/plans/<plan_code>', methods=['GET'])
@cross_origin()
def get_subscription_plan(plan_code):
    """Get specific subscription plan details"""
    try:
        plan = SubscriptionPlan.query.filter_by(plan_code=plan_code, is_active=True).first()
        if not plan:
            return jsonify({'success': False, 'error': 'Plan not found'}), 404
        
        return jsonify({
            'success': True,
            'plan': plan.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@subscription_bp.route('/user/<int:user_id>/subscription', methods=['GET'])
@cross_origin()
def get_user_subscription(user_id):
    """Get user's current subscription"""
    try:
        subscription = UserSubscription.query.filter_by(user_id=user_id).order_by(UserSubscription.created_at.desc()).first()
        if not subscription:
            return jsonify({'success': False, 'error': 'No subscription found'}), 404
        
        return jsonify({
            'success': True,
            'subscription': subscription.to_dict(),
            'plan': subscription.plan.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@subscription_bp.route('/user/<int:user_id>/start-trial', methods=['POST'])
@cross_origin()
def start_trial(user_id):
    """Start a free trial for a user"""
    try:
        data = request.get_json()
        plan_code = data.get('plan_code', 'starter')
        
        # Check if user already has a subscription
        existing_subscription = UserSubscription.query.filter_by(user_id=user_id).first()
        if existing_subscription:
            return jsonify({'success': False, 'error': 'User already has a subscription'}), 400
        
        # Get the plan
        plan = SubscriptionPlan.query.filter_by(plan_code=plan_code, is_active=True).first()
        if not plan:
            return jsonify({'success': False, 'error': 'Plan not found'}), 404
        
        # Create trial subscription
        trial_start = date.today()
        trial_end = trial_start + timedelta(days=plan.trial_days)
        
        subscription = UserSubscription(
            user_id=user_id,
            plan_id=plan.id,
            subscription_status='trial',
            trial_start_date=trial_start,
            trial_end_date=trial_end,
            current_price=0.0,
            currency=plan.currency
        )
        
        db.session.add(subscription)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'subscription': subscription.to_dict(),
            'message': f'Trial started successfully. Expires on {trial_end.isoformat()}'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@subscription_bp.route('/user/<int:user_id>/upgrade', methods=['POST'])
@cross_origin()
def upgrade_subscription(user_id):
    """Upgrade user subscription to paid plan"""
    try:
        data = request.get_json()
        plan_code = data.get('plan_code')
        billing_cycle = data.get('billing_cycle', 'monthly')
        payment_method_id = data.get('payment_method_id')
        coupon_code = data.get('coupon_code')
        
        if not plan_code or not payment_method_id:
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        # Get the plan
        plan = SubscriptionPlan.query.filter_by(plan_code=plan_code, is_active=True).first()
        if not plan:
            return jsonify({'success': False, 'error': 'Plan not found'}), 404
        
        # Calculate price
        price = plan.annual_price if billing_cycle == 'annual' and plan.annual_price else plan.monthly_price
        
        # Apply coupon if provided
        discount_amount = 0
        if coupon_code:
            coupon = Coupon.query.filter_by(coupon_code=coupon_code).first()
            if coupon and coupon.is_valid():
                if coupon.discount_type == 'percentage':
                    discount_amount = price * (coupon.discount_value / 100)
                else:
                    discount_amount = coupon.discount_value
                
                # Update coupon usage
                coupon.current_uses += 1
        
        final_price = max(0, price - discount_amount)
        
        # Get or create user subscription
        subscription = UserSubscription.query.filter_by(user_id=user_id).first()
        if not subscription:
            subscription = UserSubscription(user_id=user_id)
        
        # Update subscription
        subscription.plan_id = plan.id
        subscription.subscription_status = 'active'
        subscription.billing_cycle = billing_cycle
        subscription.current_price = final_price
        subscription.currency = plan.currency
        subscription.payment_method_id = payment_method_id
        subscription.subscription_start_date = date.today()
        
        if billing_cycle == 'annual':
            subscription.subscription_end_date = date.today() + timedelta(days=365)
            subscription.next_billing_date = date.today() + timedelta(days=365)
        else:
            subscription.subscription_end_date = date.today() + timedelta(days=30)
            subscription.next_billing_date = date.today() + timedelta(days=30)
        
        db.session.add(subscription)
        
        # Create payment record
        payment = Payment(
            subscription_id=subscription.id,
            user_id=user_id,
            amount=final_price,
            currency=plan.currency,
            payment_status='succeeded',  # In real implementation, this would come from Stripe
            payment_method='card',
            billing_period_start=subscription.subscription_start_date,
            billing_period_end=subscription.subscription_end_date,
            net_amount=final_price * 0.97,  # Assuming 3% payment processing fee
            transaction_fee=final_price * 0.03
        )
        
        db.session.add(payment)
        
        # Record coupon usage if applicable
        if coupon_code and discount_amount > 0:
            coupon_use = CouponUse(
                coupon_id=coupon.id,
                user_id=user_id,
                subscription_id=subscription.id,
                payment_id=payment.id,
                discount_amount=discount_amount,
                original_amount=price,
                final_amount=final_price
            )
            db.session.add(coupon_use)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'subscription': subscription.to_dict(),
            'payment': payment.to_dict(),
            'message': 'Subscription upgraded successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@subscription_bp.route('/user/<int:user_id>/cancel', methods=['POST'])
@cross_origin()
def cancel_subscription(user_id):
    """Cancel user subscription"""
    try:
        data = request.get_json()
        cancellation_reason = data.get('reason', '')
        immediate = data.get('immediate', False)
        
        subscription = UserSubscription.query.filter_by(user_id=user_id, subscription_status='active').first()
        if not subscription:
            return jsonify({'success': False, 'error': 'No active subscription found'}), 404
        
        if immediate:
            subscription.subscription_status = 'cancelled'
            subscription.subscription_end_date = date.today()
        else:
            # Cancel at end of billing period
            subscription.auto_renew = False
            subscription.subscription_status = 'cancelled'
        
        subscription.cancelled_date = date.today()
        subscription.cancellation_reason = cancellation_reason
        subscription.cancelled_by_user = True
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'subscription': subscription.to_dict(),
            'message': 'Subscription cancelled successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@subscription_bp.route('/user/<int:user_id>/usage', methods=['GET'])
@cross_origin()
def get_usage_stats(user_id):
    """Get user's current usage statistics"""
    try:
        subscription = UserSubscription.query.filter_by(user_id=user_id).order_by(UserSubscription.created_at.desc()).first()
        if not subscription:
            return jsonify({'success': False, 'error': 'No subscription found'}), 404
        
        # Get current month usage
        current_month_start = date.today().replace(day=1)
        usage_logs = UsageLog.query.filter(
            UsageLog.subscription_id == subscription.id,
            UsageLog.created_at >= current_month_start
        ).all()
        
        # Aggregate usage by feature
        usage_summary = {}
        for log in usage_logs:
            if log.feature_used not in usage_summary:
                usage_summary[log.feature_used] = {
                    'count': 0,
                    'storage_mb': 0,
                    'processing_time': 0
                }
            usage_summary[log.feature_used]['count'] += log.usage_count
            usage_summary[log.feature_used]['storage_mb'] += log.storage_used_mb
            usage_summary[log.feature_used]['processing_time'] += log.processing_time_seconds
        
        return jsonify({
            'success': True,
            'subscription': subscription.to_dict(),
            'plan_limits': subscription.plan.to_dict(),
            'current_usage': {
                'properties': subscription.properties_count,
                'documents': subscription.documents_count,
                'storage_gb': subscription.storage_used_gb,
                'api_calls': subscription.api_calls_this_month
            },
            'usage_by_feature': usage_summary
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@subscription_bp.route('/user/<int:user_id>/log-usage', methods=['POST'])
@cross_origin()
def log_usage(user_id):
    """Log feature usage for billing and analytics"""
    try:
        data = request.get_json()
        feature_used = data.get('feature_used')
        usage_type = data.get('usage_type')
        usage_count = data.get('usage_count', 1)
        storage_used_mb = data.get('storage_used_mb', 0.0)
        processing_time_seconds = data.get('processing_time_seconds', 0.0)
        property_id = data.get('property_id')
        document_id = data.get('document_id')
        
        if not feature_used or not usage_type:
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        subscription = UserSubscription.query.filter_by(user_id=user_id).order_by(UserSubscription.created_at.desc()).first()
        if not subscription:
            return jsonify({'success': False, 'error': 'No subscription found'}), 404
        
        # Create usage log
        usage_log = UsageLog(
            subscription_id=subscription.id,
            user_id=user_id,
            feature_used=feature_used,
            usage_type=usage_type,
            usage_count=usage_count,
            storage_used_mb=storage_used_mb,
            processing_time_seconds=processing_time_seconds,
            property_id=property_id,
            document_id=document_id,
            user_agent=request.headers.get('User-Agent'),
            ip_address=request.remote_addr
        )
        
        db.session.add(usage_log)
        
        # Update subscription usage counters
        if usage_type == 'api_call':
            subscription.api_calls_this_month += usage_count
        
        if storage_used_mb > 0:
            subscription.storage_used_gb += storage_used_mb / 1024
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Usage logged successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@subscription_bp.route('/coupons/validate', methods=['POST'])
@cross_origin()
def validate_coupon():
    """Validate a coupon code"""
    try:
        data = request.get_json()
        coupon_code = data.get('coupon_code')
        user_id = data.get('user_id')
        plan_code = data.get('plan_code')
        
        if not coupon_code:
            return jsonify({'success': False, 'error': 'Coupon code required'}), 400
        
        coupon = Coupon.query.filter_by(coupon_code=coupon_code.upper()).first()
        if not coupon:
            return jsonify({'success': False, 'error': 'Invalid coupon code'}), 404
        
        if not coupon.is_valid():
            return jsonify({'success': False, 'error': 'Coupon has expired or reached usage limit'}), 400
        
        # Check if user has already used this coupon
        if user_id:
            existing_use = CouponUse.query.filter_by(coupon_id=coupon.id, user_id=user_id).first()
            if existing_use and coupon.max_uses_per_user == 1:
                return jsonify({'success': False, 'error': 'Coupon already used'}), 400
        
        # Check if coupon applies to the selected plan
        if plan_code and coupon.applicable_plans:
            applicable_plans = json.loads(coupon.applicable_plans)
            if plan_code not in applicable_plans:
                return jsonify({'success': False, 'error': 'Coupon not applicable to selected plan'}), 400
        
        return jsonify({
            'success': True,
            'coupon': coupon.to_dict(),
            'message': 'Coupon is valid'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@subscription_bp.route('/user/<int:user_id>/referral-code', methods=['GET'])
@cross_origin()
def get_referral_code(user_id):
    """Get user's referral code"""
    try:
        # Check if user already has a referral code
        referral = ReferralProgram.query.filter_by(referrer_user_id=user_id).first()
        
        if not referral:
            # Generate new referral code
            referral_code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
            
            referral = ReferralProgram(
                referrer_user_id=user_id,
                referral_code=referral_code,
                referrer_reward_type='discount',
                referrer_reward_value=25.0,  # 25% discount
                referred_reward_type='discount',
                referred_reward_value=25.0   # 25% discount
            )
            
            db.session.add(referral)
            db.session.commit()
        
        # Get referral statistics
        total_referrals = ReferralProgram.query.filter_by(referrer_user_id=user_id).count()
        successful_referrals = ReferralProgram.query.filter_by(
            referrer_user_id=user_id, 
            referral_status='converted'
        ).count()
        
        return jsonify({
            'success': True,
            'referral_code': referral.referral_code,
            'total_referrals': total_referrals,
            'successful_referrals': successful_referrals,
            'reward_details': {
                'referrer_reward': f"{referral.referrer_reward_value}% discount",
                'referred_reward': f"{referral.referred_reward_value}% discount"
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@subscription_bp.route('/feature-flags/<int:user_id>', methods=['GET'])
@cross_origin()
def get_feature_flags(user_id):
    """Get feature flags for a user"""
    try:
        subscription = UserSubscription.query.filter_by(user_id=user_id).order_by(UserSubscription.created_at.desc()).first()
        
        flags = FeatureFlag.query.filter_by(is_enabled=True).all()
        user_flags = {}
        
        for flag in flags:
            # Check if flag applies to user's plan
            if flag.target_plans:
                target_plans = json.loads(flag.target_plans)
                if subscription and subscription.plan.plan_code not in target_plans:
                    continue
            
            # Simple rollout percentage check (in production, use more sophisticated logic)
            import random
            if random.random() * 100 <= flag.rollout_percentage:
                user_flags[flag.flag_name] = True
            else:
                user_flags[flag.flag_name] = False
        
        return jsonify({
            'success': True,
            'feature_flags': user_flags
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Admin routes for managing subscriptions
@subscription_bp.route('/admin/plans', methods=['POST'])
@cross_origin()
def create_subscription_plan():
    """Create a new subscription plan (admin only)"""
    try:
        data = request.get_json()
        
        plan = SubscriptionPlan(
            plan_name=data['plan_name'],
            plan_code=data['plan_code'],
            monthly_price=data['monthly_price'],
            annual_price=data.get('annual_price'),
            currency=data.get('currency', 'USD'),
            max_properties=data.get('max_properties'),
            max_documents_per_property=data.get('max_documents_per_property'),
            max_storage_gb=data.get('max_storage_gb'),
            max_users=data.get('max_users', 1),
            features_included=json.dumps(data.get('features_included', [])),
            api_access=data.get('api_access', False),
            priority_support=data.get('priority_support', False),
            white_label=data.get('white_label', False),
            custom_integrations=data.get('custom_integrations', False),
            policy_analysis=data.get('policy_analysis', True),
            compliance_tracking=data.get('compliance_tracking', True),
            risk_assessment=data.get('risk_assessment', False),
            property_transfer=data.get('property_transfer', False),
            gap_insurance_marketplace=data.get('gap_insurance_marketplace', False),
            professional_network=data.get('professional_network', False),
            trial_days=data.get('trial_days', 14),
            trial_features=json.dumps(data.get('trial_features', [])),
            sort_order=data.get('sort_order', 0)
        )
        
        db.session.add(plan)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'plan': plan.to_dict(),
            'message': 'Subscription plan created successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

