# LSA Service Booking API - Detailed Usage Guide

This document provides a clear, step-by-step guide on how to test and interact with your backend API. It assumes you have your development server running and your `seed_db.py` data loaded (at least initially for your first login).

---

## 1. Getting Started

First, make sure your Django development server is running in your virtual environment:

```bash
# In your terminal (make sure (venv) is active)
python manage.py runserver
```

Next, open the built-in interactive API documentation (Swagger UI) in your web browser:
🔗 **http://127.0.0.1:8000/api/docs/swagger/**

---

## 2. Authentication (Login)

Almost all endpoints in this project require you to be authenticated using a JWT (JSON Web Token). We need to exchange your username (`vannuru` or `anil`) and password for a token.

### Step 2.1: Generate the Token
1. In the Swagger UI, scroll down to the **auth** section.
2. Click on the row for `POST /api/v1/auth/token/` to expand it.
3. Click the **Try it out** button on the right.
4. In the **Request body** text area, enter your credentials:
```json
{
  "username": "anil",
  "password": "anil07"
}
```
5. Click the large blue **Execute** button.
6. Scroll down to the **Responses** section. You should see a `200` status code and a response body that looks like this:
```json
{
  "refresh": "eyJhbGciOiJIUz...",
  "access": "eyJhbGciOiJIUzI1NiIsInR..."
}
```
7. **Copy the long text** inside the quotes of the `"access"` field. Make sure you do NOT copy the quotes themselves.

### Step 2.2: Authorize Swagger UI
Now that we have the access token, we must tell Swagger to attach it to all future requests.
1. Scroll to the very top of the Swagger webpage.
2. Click the green **Authorize** button (with a padlock icon).
3. A modal will pop up. In the `Value` field under **jwtAuth (http, Bearer)**, just paste your raw token (e.g., `eyJhbGci...`). *Do NOT type the word "Bearer"*.
4. Click **Authorize**, then click **Close**.

---

## 3. Creating New Accounts (New Feature)

You no longer have to rely exclusively on `seed_db.py` to create users. Since you are now authorized, you can create new accounts directly through Swagger:

- **Create a New Login User:** Expand `POST /api/v1/parents/register/`, enter a username, password, and email, then execute.
- **Create a Parent Profile:** Expand `POST /api/v1/parents/`, enter the parent details, and execute. Note down the `id`!
- **Create an LSA Profile:** Expand `POST /api/v1/lsas/`, enter the LSA details (ensure `"is_active": true`), and execute. Note down the `id`!

---

## 4. Searching for LSAs

Now let's search for available Learning Support Assistants (LSAs).
1. Scroll down to the **lsas** section in Swagger.
2. Expand `GET /api/v1/lsas/search/` and click **Try it out**.
3. You will see fields like `skill`, `start_time`, `end_time`, etc.
   - **To see all LSAs:** Leave everything blank and just click **Execute**.
   - **To filter by skill:** Type `autism` or `math` into the `skill` field and click **Execute**.
4. Check the **Responses** section. You will get a JSON list of LSAs. Note down the `"id"` of an LSA you want to book!

---

## 5. Making a Booking

Let's book an LSA for a Parent.
1. Scroll to the **bookings** section.
2. Expand `POST /api/v1/bookings/` and click **Try it out**.
3. The server will automatically pre-populate the text box. Change the `parent_id` and `lsa_id` to match the data you created earlier (or the ones from the seed).
```json
{
  "parent_id": 2,
  "lsa_id": 3,
  "session_start": "2026-08-11T10:00:00Z",
  "session_end": "2026-08-11T12:00:00Z"
}
```
4. Click **Execute**.

### Expected Result
If the LSA is available, you will receive a `201 Created` response. Thanks to recent updates, it will now explicitly include the `razorpay_order_id`:
```json
{
  "id": 1,
  "parent_id": 2,
  "lsa_id": 3,
  "status": "PENDING",
  "payment": {
    "id": 1,
    "razorpay_order_id": "order_XXXXXXX",
    "amount": 300000,
    "currency": "INR",
    "status": "CREATED"
  }
}
```
**Copy the `"razorpay_order_id"` from the payment block.** You need it for the final step.

---

## 6. Simulating the Payment Webhook (Updated)

Because this is a backend-only project without a frontend checkout screen, we need to simulate Razorpay confirming the payment. You no longer need to use the `simulate_webhook.py` script in the terminal!

1. Scroll down to the **payments** section in Swagger.
2. Expand `POST /api/v1/payments/simulate-webhook/` and click **Try it out**.
3. Enter the `razorpay_order_id` you copied from Step 5:
```json
{
  "order_id": "order_XXXXXXX"
}
```
4. Click **Execute**.
5. You should see a success message (`Status Code: 200`) in the response body!
6. The payment and booking statuses in your database have now been successfully updated from `PENDING/CREATED` to `CONFIRMED/SUCCESS`!
