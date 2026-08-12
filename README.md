# LSA Service Booking Platform

A comprehensive backend for the LSA (Learning Support Assistant) Service Booking Platform.

## Technology Stack
- **Framework**: Django 5.1 & Django REST Framework
- **Language**: Python 3.12+
- **Database**: PostgreSQL
- **Payments**: Razorpay
- **Authentication**: JWT (Simple JWT)
- **API Documentation**: OpenAPI / Swagger (drf-spectacular)

## Core Features
- **LSA Search**: Search for Learning Support Assistants by skill, rate, and availability. Includes pagination and ordering. Uses advanced query optimization (e.g., `Exists`) to prevent N+1 queries.
- **Booking Management**: Book an LSA for specific times. Employs row-level database locking (`select_for_update`) to prevent double-booking conflicts.
- **Payment Processing**: Integrated Razorpay API to generate orders.
- **Webhook Processing**: Secure endpoint (`X-Razorpay-Signature`) with idempotency guarantees to capture payment success/failure.
- **Robust Error Handling**: Standardized JSON error formats for all API exceptions.

## Setup Instructions

1. Clone the repository and navigate into it.
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file based on `.env.example`:
   ```bash
   cp .env.example .env
   # Update variables in .env with your local PostgreSQL and Razorpay keys
   ```
5. Apply migrations:
   ```bash
   python manage.py migrate
   ```
6. Run the development server:
   ```bash
   python manage.py runserver
   ```

## Testing

This project uses `pytest` for all unit and integration testing. Razorpay is fully mocked in test cases.

```bash
# Run the test suite
pytest

# Test coverage is comprehensive across domains, views, services, and webhooks.
```

## API Documentation

Interactive API documentation is generated using `drf-spectacular`.

1. Start the server.
2. Navigate to:
   - **Swagger UI**: `http://localhost:8000/api/docs/swagger/`
   - **ReDoc**: `http://localhost:8000/api/docs/redoc/`
   - **OpenAPI Schema**: `http://localhost:8000/api/schema/`

## Developer Tools

To make local testing seamless, two utility scripts are included:

1. **`seed_db.py`**: Automatically generates a test User, Parent, and multiple LSAs.
   ```bash
   python seed_db.py
   ```
2. **`simulate_webhook.py`**: Simulates Razorpay's `payment.captured` webhook securely using HMAC SHA256. Use this to finalize a booking after creating it via the API.
   ```bash
   python simulate_webhook.py order_XXXXXXX
   ```
