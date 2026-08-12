# Requirements Analysis

## Explicit requirements
* **Tech Stack**: Python 3.12+, Django, Django REST Framework, PostgreSQL, Django ORM, Pytest, pytest-django, Requests, Razorpay API. No Docker, no Celery, no Redis, no MongoDB.
* **Architecture**: Modular monolith with clear separation of concerns (Views -> Services -> Selectors -> ORM).
* **Entities**: `Parent`, `LSAProfile`, `BookingRequest`, `Payment`.
* **Endpoints**: 
  * `POST /api/v1/bookings/`: Create bookings transactionally.
  * `GET /api/v1/lsas/search/`: Search LSAs with N+1 query optimization.
  * `POST /api/v1/payments/webhook/`: Handle Razorpay events idempotently.
* **Core Business Logic**: 
  * Prevent double-bookings (existing_start < new_end AND existing_end > new_start).
  * Calculate payment securely on the server-side.
  * Validate LSA availability in the database (not in Python loops).
* **Security & Reliability**: 
  * Server-side Razorpay signature verification.
  * Idempotent webhook handling.
  * Global exception handling with request correlation IDs.
* **Quality Assurance**: 
  * Automated tests (unit, integration, mock external calls, query count assertion).
  * Swagger/OpenAPI documentation.
  * GitHub Actions CI pipeline.

## Assumptions
* **LSA Skills**: Since PostgreSQL is explicitly required and skills must be filterable, we will use PostgreSQL's `ArrayField(models.CharField())`. This provides efficient indexing and searching without the complexity of a many-to-many relationship table.
* **Payment Amount Calculation**: The `LSAProfile` will have an `hourly_rate`. The total amount will be calculated as `(session duration in hours) * hourly_rate`. We will assume the currency is INR and amounts passed to Razorpay will be in minor units (paise).
* **Authentication**: Authentication is explicitly stated as not required for this assessment. We will use unauthenticated endpoints and pass `parent_id` and `lsa_id` in the request payloads. 
* **Pagination**: Standard DRF `PageNumberPagination` will be used with sensible defaults.
* **Concurrency**: We will rely on Django's `transaction.atomic()` and potentially row-level locking (`select_for_update()`) or PostgreSQL `ExclusionConstraint` to guarantee double-booking prevention under concurrent load.

## Ambiguities
* **Skill matching**: The specification asks to filter by skill. We will assume an exact match on individual skills within the array (e.g., if searching for "autism", any LSA with "autism" in their skills array will match).
* **Booking granularity**: Are bookings restricted to full hours? We will assume minute-level precision is allowed but billing is proportional to exact duration.

## Risks
* **Race Conditions in Booking**: A high risk of double booking exists if two requests arrive simultaneously for the same LSA. We mitigate this with database-level constraints.
* **Razorpay Webhook Reliability**: Webhooks may be delayed, duplicated, or fail. We mitigate this with a strict state machine and idempotent processing logic.
* **Timezones**: Timezone mismatches between client and server can lead to incorrect availability. We mitigate this by strictly enforcing ISO-8601 UTC timestamps in the API and using Django's timezone-aware datetime handling.

## Deferred features
* User authentication and authorization (JWT, session auth).
* Asynchronous task processing (Celery/RabbitMQ).
* Caching layers (Redis).
* Docker/containerization.
