from flask import Blueprint, request, jsonify
from datetime import datetime
import openai
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

chatbot_bp = Blueprint('chatbot', __name__)

# OpenAI configuration (you'll need to set this environment variable)
openai.api_key = os.getenv('OPENAI_API_KEY')

# PropertyGuard knowledge base
PROPERTYGUARD_CONTEXT = """
You are PropertyGuard's helpful AI assistant. PropertyGuard is a comprehensive property management platform that helps homeowners, investors, and property managers track and manage their properties with a focus on compliance, warranties, and protection against Expropriation Without Compensation (EWC) in South Africa.

Key PropertyGuard Features:
1. EWC Protection: Maintains comprehensive documentation to support legal challenges against expropriation
2. Warranty Tracking: Monitors all property warranties, expiration dates, and maintenance requirements
3. Compliance Management: Tracks Certificates of Compliance (COCs), building regulations, and inspection requirements
4. Insurance Policy Analysis: Analyzes policies to extract requirements and ensure valid coverage
5. Property Pedigree: Complete property history and documentation for due diligence
6. Document Management: Secure storage of all property-related documents
7. Liability Chain Mapping: Tracks all contractors, suppliers, and their insurance coverage
8. Automated Reminders: Alerts for expiring certificates, required maintenance, and renewals

Pricing:
- Starter: $9/month (individual homeowners, 1 property, 1GB storage)
- Professional: $29/month (property investors, 5 properties, 10GB storage)
- Business: $59/month (property managers, unlimited properties, 100GB storage)
- Enterprise: Custom pricing for large organizations

South African Context:
- Focus on EWC (Expropriation Without Compensation) protection
- SANS standards compliance
- Municipal regulations and COC requirements
- Building industry challenges and liability gaps

Always be helpful, professional, and focus on how PropertyGuard solves real property management problems. If asked about technical issues or complex problems, suggest contacting support@propertyguard.co.za.
"""

def get_ai_response(user_message, user_context=None):
    """Get response from OpenAI API with PropertyGuard context"""
    try:
        messages = [
            {"role": "system", "content": PROPERTYGUARD_CONTEXT},
            {"role": "user", "content": user_message}
        ]
        
        # Add user context if available
        if user_context:
            context_message = f"User context: {user_context}"
            messages.insert(1, {"role": "system", "content": context_message})
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Using 3.5-turbo for cost efficiency
            messages=messages,
            max_tokens=500,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        logger.error(f"OpenAI API error: {str(e)}")
        return get_fallback_response(user_message)

def get_fallback_response(message):
    """Provide fallback responses when AI service is unavailable"""
    message_lower = message.lower()
    
    # EWC related questions
    if any(keyword in message_lower for keyword in ['ewc', 'expropriation', 'land', 'government']):
        return """PropertyGuard helps protect your property rights by maintaining comprehensive documentation that can be crucial for EWC challenges. Our platform:

• Stores all ownership documents securely
• Maintains proof of property improvements and investments
• Tracks compliance with all regulations
• Creates tamper-proof documentation chains
• Provides legal-ready documentation packages

This comprehensive record can support challenges in constitutional courts and international human rights forums."""

    # Warranty related questions
    elif any(keyword in message_lower for keyword in ['warranty', 'guarantee', 'maintenance']):
        return """PropertyGuard's warranty tracking system helps you:

• Upload and organize all warranty documents
• Set automatic reminders before warranties expire
• Track required maintenance to keep warranties valid
• Monitor contractor insurance coverage
• Ensure you meet all warranty conditions

This prevents warranty voids and protects your investments."""

    # Compliance related questions
    elif any(keyword in message_lower for keyword in ['compliance', 'coc', 'certificate', 'inspection']):
        return """Our compliance management system ensures you stay compliant with:

• Certificates of Compliance (COCs) for electrical, plumbing, gas
• Building regulations and municipal requirements
• SANS standards and industry regulations
• Regular inspection schedules
• Professional certification renewals

We send automated reminders and help you maintain full regulatory compliance."""

    # Insurance related questions
    elif any(keyword in message_lower for keyword in ['insurance', 'policy', 'coverage', 'claim']):
        return """PropertyGuard analyzes your insurance policies to:

• Extract specific coverage requirements
• Identify maintenance obligations for valid coverage
• Track policy renewal dates
• Monitor insurer financial stability
• Identify potential coverage gaps

This ensures your insurance actually protects you when you need it most."""

    # Pricing questions
    elif any(keyword in message_lower for keyword in ['price', 'cost', 'subscription', 'plan']):
        return """PropertyGuard offers flexible pricing:

**Starter Plan - $9/month:**
• 1 property
• 1GB storage
• Basic compliance tracking
• Document management

**Professional Plan - $29/month:**
• 5 properties
• 10GB storage
• Advanced compliance features
• Warranty tracking
• EWC protection tools

**Business Plan - $59/month:**
• Unlimited properties
• 100GB storage
• Full feature access
• Priority support
• API access

All plans include core features like document storage, compliance tracking, and automated reminders."""

    # General help
    elif any(keyword in message_lower for keyword in ['help', 'support', 'how', 'what']):
        return """I'm here to help with PropertyGuard! I can assist with:

• Understanding PropertyGuard features
• EWC protection strategies
• Warranty and compliance tracking
• Property documentation best practices
• Subscription and pricing questions

For technical issues or account problems, please contact our support team at support@propertyguard.co.za."""

    # Default response
    else:
        return """Thank you for your question! PropertyGuard is designed to help property owners manage their properties comprehensively, with special focus on:

• EWC protection through comprehensive documentation
• Warranty and compliance tracking
• Insurance policy analysis
• Property pedigree maintenance

Could you tell me more specifically what you'd like to know about? Or feel free to contact our support team at support@propertyguard.co.za for detailed assistance."""

def log_conversation(user_id, user_message, bot_response, context=None):
    """Log conversation for analytics (implement database storage as needed)"""
    try:
        conversation_log = {
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'user_message': user_message,
            'bot_response': bot_response,
            'context': context
        }
        
        # For now, just log to console
        # In production, save to database for analytics
        logger.info(f"Chatbot conversation: {conversation_log}")
        
        # TODO: Implement database storage for conversation analytics
        # This data will be valuable for:
        # - Understanding user needs
        # - Improving responses
        # - Identifying feature requests
        # - Measuring chatbot effectiveness
        
    except Exception as e:
        logger.error(f"Error logging conversation: {str(e)}")

@chatbot_bp.route('/message', methods=['POST'])
def chatbot_message():
    """Handle chatbot message requests"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({'error': 'Message is required'}), 400
        
        user_message = data.get('message', '').strip()
        user_id = data.get('user_id')
        context = data.get('context', 'general')
        
        if not user_message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        # Get AI response
        if openai.api_key:
            bot_response = get_ai_response(user_message, context)
        else:
            logger.warning("OpenAI API key not configured, using fallback responses")
            bot_response = get_fallback_response(user_message)
        
        # Log conversation for analytics
        log_conversation(user_id, user_message, bot_response, context)
        
        return jsonify({
            'response': bot_response,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Chatbot error: {str(e)}")
        return jsonify({
            'response': "I'm sorry, I'm experiencing technical difficulties. Please try again or contact support@propertyguard.co.za for assistance.",
            'error': True
        }), 500

@chatbot_bp.route('/analytics', methods=['GET'])
def chatbot_analytics():
    """Get chatbot analytics (admin only)"""
    # TODO: Implement authentication check for admin users
    # TODO: Implement database queries for conversation analytics
    
    try:
        # Placeholder analytics data
        analytics = {
            'total_conversations': 0,
            'common_topics': [],
            'user_satisfaction': 0,
            'escalation_rate': 0,
            'response_time': 0
        }
        
        return jsonify(analytics)
    
    except Exception as e:
        logger.error(f"Analytics error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve analytics'}), 500

@chatbot_bp.route('/feedback', methods=['POST'])
def chatbot_feedback():
    """Handle user feedback on chatbot responses"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Feedback data is required'}), 400
        
        feedback = {
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': data.get('user_id'),
            'conversation_id': data.get('conversation_id'),
            'rating': data.get('rating'),  # 1-5 stars
            'comment': data.get('comment'),
            'helpful': data.get('helpful')  # boolean
        }
        
        # Log feedback
        logger.info(f"Chatbot feedback: {feedback}")
        
        # TODO: Store in database for analysis
        
        return jsonify({'message': 'Feedback received successfully'})
    
    except Exception as e:
        logger.error(f"Feedback error: {str(e)}")
        return jsonify({'error': 'Failed to process feedback'}), 500

