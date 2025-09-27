## Project Description
This is a Django REST Framework-based credit approval system. It provides APIs for customer registration, credit eligibility checks, and loan creation.

## Setup Instructions

### 1. Clone the Repository
If you haven't already, clone this repository to your local machine:
```bash
git clone https://github.com/abhishekvimukt/credit-approval.git
cd credit-approval
```

### 2. Install Dependencies
Ensure you have Python installed. Then, install the required packages using `pip`:
```bash
pip install -r requirements.txt
```

### 3. Database Migrations
Apply the database migrations to set up your database schema:
```bash
python manage.py migrate
```

### 4. Run the Development Server
Start the Django development server:
```bash
python manage.py runserver
```
The server will typically run on `http://127.0.0.1:8000/`.

## API Endpoints

The following are the main API endpoints available:

*   **`/api/register/`**:
    *   **Method:** `POST`
    *   **Description:** Registers a new customer in the system.

*   **`/api/check-eligibility/`**:
    *   **Method:** `POST`
    *   **Description:** Checks a customer's eligibility for a loan based on provided criteria.

*   **`/api/create-loan/`**:
    *   **Method:** `POST`
    *   **Description:** Creates a new loan for an eligible customer.

---
