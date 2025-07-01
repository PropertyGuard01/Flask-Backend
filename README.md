# PropertyGuard Flask Backend API

This is the backend API for PropertyGuard, a comprehensive property management application that helps homeowners track warranties, compliance certificates, maintenance schedules, and insurance requirements.

## Features

- User authentication and management
- Property management with multiple property types support
- Warranty and compliance tracking
- Insurance policy management
- Liability chain mapping
- Subscription management
- AI chatbot integration
- Document storage and management

## Technology Stack

- **Framework**: Flask
- **Database**: PostgreSQL
- **Authentication**: JWT tokens
- **File Storage**: Cloud storage integration
- **API Documentation**: OpenAPI/Swagger

## Installation

1. Clone the repository:
```bash
git clone https://github.com/PropertyGuard01/Flask-Backend.git
cd Flask-Backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run the application:
```bash
python src/main.py
```

## API Endpoints

The API provides endpoints for:
- User management (`/api/users`)
- Property management (`/api/properties`)
- Warranty tracking (`/api/warranties`)
- Compliance management (`/api/compliance`)
- Subscription management (`/api/subscriptions`)
- Chatbot integration (`/api/chatbot`)

## Deployment

This application is configured for deployment on Railway with PostgreSQL database.

## License

Proprietary - PropertyGuard by AirCapital

