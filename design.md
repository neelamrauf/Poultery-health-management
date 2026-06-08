# Design Document — Poultry Health & Medicine Management System

## Overview

The system is a full-stack web application built on a Django REST Framework (DRF) backend and a React (Vite + Tailwind CSS) frontend. It serves two roles — Farmer and Admin — and provides flock health diagnosis, medicine inventory management, a knowledge base, and a mock e-commerce flow. Authentication is handled with SimpleJWT; role enforcement is handled by custom DRF permission classes. The backend is structured following Django's MVC conventions (models → serializers → views → URLs). The frontend is component-based, using React Router for navigation and Axios for API calls.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Browser                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │            React SPA (Vite + Tailwind CSS)            │  │
│  │  Auth · Dashboard · Diagnosis · Inventory · Shop ·   │  │
│  │  Knowledge Base · Cart · Orders · Admin Guard         │  │
│  └──────────────────────┬───────────────────────────────┘  │
└─────────────────────────┼───────────────────────────────────┘
                          │ HTTPS  Axios + Bearer token
                          ▼
┌─────────────────────────────────────────────────────────────┐
│          Django + Django REST Framework  (/api/v1/)         │
│                                                             │
│  ┌──────────┐  ┌──────────────┐  ┌─────────────────────┐  │
│  │  Auth    │  │  Diagnosis   │  │  Medicine Inventory  │  │
│  │  Views   │  │  Engine      │  │  Views               │  │
│  └──────────┘  └──────────────┘  └─────────────────────┘  │
│  ┌──────────┐  ┌──────────────┐  ┌─────────────────────┐  │
│  │Knowledge │  │  E-Commerce  │  │  Order / Checkout    │  │
│  │Base Views│  │  Catalog     │  │  Views               │  │
│  └──────────┘  └──────────────┘  └─────────────────────┘  │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                Django Admin (/admin/)                │   │
│  └─────────────────────────────────────────────────────┘   │
└───────────────────────────────┬─────────────────────────────┘
                                │ ORM
                                ▼
                      ┌──────────────────┐
                      │   PostgreSQL DB   │
                      └──────────────────┘
```

### Key Architectural Decisions

- All API routes are prefixed `/api/v1/`.
- Authentication: SimpleJWT access tokens; no refresh token endpoint is required in the initial version.
- Permissions: Two custom DRF permission classes — `IsFarmer` and `IsAdmin` — applied per view.
- Cart state lives entirely in React state (not persisted server-side).
- The checkout endpoint records the order but performs no payment processing.
- Django Admin is the sole management interface for content (diseases, symptoms, knowledge base, orders).

---

## Data Models

### User (extends `AbstractUser`)

| Field      | Type          | Constraints                     |
|------------|---------------|---------------------------------|
| id         | UUID / PK     | auto                            |
| username   | CharField     | unique, max 150                 |
| email      | EmailField    | unique                          |
| password   | CharField     | hashed (Django default)         |
| role       | CharField(10) | choices: Farmer, Admin          |
| created_at | DateTimeField | auto_now_add                    |

### Symptom

| Field | Type          | Constraints      |
|-------|---------------|------------------|
| id    | AutoField/PK  |                  |
| name  | CharField(100)| unique           |

### Disease

| Field                   | Type           | Constraints                            |
|-------------------------|----------------|----------------------------------------|
| id                      | AutoField/PK   |                                        |
| name                    | CharField(150) | unique                                 |
| severity                | CharField(20)  | choices: Mild, Moderate, Severe        |
| treatment_recommendations| TextField      |                                        |
| symptoms                | M2M → Symptom  | through DiseaseSymptom                 |

### DiseaseSymptom (M2M through table)

| Field   | Type         | Constraints         |
|---------|--------------|---------------------|
| id      | AutoField/PK |                     |
| disease | FK → Disease | on_delete=CASCADE   |
| symptom | FK → Symptom | on_delete=CASCADE   |
| weight  | FloatField   | > 0, unique together: (disease, symptom) |

### Medicine

| Field             | Type           | Constraints                    |
|-------------------|----------------|--------------------------------|
| id                | AutoField/PK   |                                |
| name              | CharField(150) | unique                         |
| description       | TextField      |                                |
| category          | CharField(100) |                                |
| unit_price        | DecimalField   | max_digits=10, decimal_places=2, >= 0 |
| stock_quantity    | IntegerField   | >= 0                           |
| dosage_per_bird   | FloatField     | > 0                            |
| dosage_unit       | CharField(50)  | e.g., "ml", "g"                |
| expiry_date       | DateField      | must be future on creation     |
| created_at        | DateTimeField  | auto_now_add                   |
| updated_at        | DateTimeField  | auto_now                       |

### DiagnosisSession

| Field          | Type             | Constraints                  |
|----------------|------------------|------------------------------|
| id             | AutoField/PK     |                              |
| farmer         | FK → User        | on_delete=CASCADE            |
| submitted_at   | DateTimeField    | auto_now_add                 |
| symptoms       | M2M → Symptom    |                              |
| top_disease    | FK → Disease     | null=True, on_delete=SET_NULL|
| top_score      | FloatField       | null=True                    |

### KnowledgeBaseArticle

| Field        | Type           | Constraints                                              |
|--------------|----------------|----------------------------------------------------------|
| id           | AutoField/PK   |                                                          |
| title        | CharField(200) |                                                          |
| category     | CharField(30)  | choices: Best Practices, Vaccination Schedule, Nutrition |
| body         | TextField      |                                                          |
| last_updated | DateTimeField  | auto_now                                                 |

### Order

| Field          | Type           | Constraints              |
|----------------|----------------|--------------------------|
| id             | AutoField/PK   |                          |
| farmer         | FK → User      | on_delete=CASCADE        |
| submitted_at   | DateTimeField  | auto_now_add             |
| total_amount   | DecimalField   | max_digits=12, decimal_places=2 |

### OrderItem

| Field      | Type           | Constraints                         |
|------------|----------------|-------------------------------------|
| id         | AutoField/PK   |                                     |
| order      | FK → Order     | on_delete=CASCADE, related_name=items|
| medicine   | FK → Medicine  | on_delete=PROTECT                   |
| quantity   | PositiveIntegerField | >= 1                          |
| unit_price | DecimalField   | captured at time of order           |

---

## API Endpoints

All routes are prefixed with `/api/v1/`. All responses have `Content-Type: application/json`.

### Authentication

| Method | Path                   | Auth | Description                         |
|--------|------------------------|------|-------------------------------------|
| POST   | /auth/register/        | No   | Create a new user account           |
| POST   | /auth/login/           | No   | Obtain JWT access token             |

**Register request body:**
```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "role": "Farmer | Admin"
}
```

**Login response body:**
```json
{
  "access": "<jwt_token>",
  "role": "Farmer | Admin"
}
```

### Diagnosis

| Method | Path                   | Auth    | Role   | Description                              |
|--------|------------------------|---------|--------|------------------------------------------|
| GET    | /symptoms/             | Yes     | Farmer | List all symptoms                        |
| POST   | /diagnosis/            | Yes     | Farmer | Run diagnosis; persist session           |
| GET    | /diagnosis/history/    | Yes     | Farmer | List farmer's past diagnosis sessions    |

**Diagnosis POST request body:**
```json
{ "symptom_ids": [1, 3, 7] }
```

**Diagnosis POST response body:**
```json
{
  "session_id": 42,
  "results": [
    {
      "disease_id": 5,
      "name": "Newcastle Disease",
      "match_score": 83.3,
      "severity": "Severe",
      "treatment_recommendations": "..."
    }
  ]
}
```

### Medicine Inventory

| Method | Path                          | Auth | Role   | Description                          |
|--------|-------------------------------|------|--------|--------------------------------------|
| GET    | /medicines/                   | Yes  | Farmer | List all medicines (with expiry_alert)|
| POST   | /medicines/                   | Yes  | Farmer | Add a new medicine record            |
| GET    | /medicines/{id}/              | Yes  | Farmer | Retrieve a single medicine           |
| PATCH  | /medicines/{id}/              | Yes  | Farmer | Update stock quantity                |
| GET    | /medicines/dosage-calculator/ | Yes  | Farmer | Calculate total dosage               |

**Dosage calculator query params:** `?medicine_id=5&bird_count=200`

**Dosage calculator response:**
```json
{
  "medicine_id": 5,
  "bird_count": 200,
  "total_dosage": 400.0,
  "unit": "ml"
}
```

**Medicine response (with expiry_alert):**
```json
{
  "id": 5,
  "name": "Tylosin",
  "category": "Antibiotic",
  "unit_price": "12.50",
  "stock_quantity": 100,
  "dosage_per_bird": 2.0,
  "dosage_unit": "ml",
  "expiry_date": "2025-07-01",
  "expiry_alert": true
}
```

### Knowledge Base

| Method | Path                | Auth | Role   | Description                                        |
|--------|---------------------|------|--------|----------------------------------------------------|
| GET    | /knowledge-base/    | No   | Public | List articles; filterable by `?category=...`       |

### E-Commerce Catalog

| Method | Path        | Auth | Role   | Description                           |
|--------|-------------|------|--------|---------------------------------------|
| GET    | /catalog/   | Yes  | Farmer | List all medicines as catalog products|

### Orders

| Method | Path           | Auth | Role   | Description                               |
|--------|----------------|------|--------|-------------------------------------------|
| POST   | /orders/       | Yes  | Farmer | Submit cart as new order                  |
| GET    | /orders/       | Yes  | Farmer | List farmer's orders (timestamp desc)     |
| GET    | /orders/{id}/  | Yes  | Farmer | Retrieve a single order with line items   |

**Order POST request body:**
```json
{
  "items": [
    { "medicine_id": 5, "quantity": 2 },
    { "medicine_id": 8, "quantity": 1 }
  ]
}
```

---

## Component Architecture — Frontend

```
src/
├── api/
│   └── axios.js              # Axios instance, interceptor attaches Bearer token
├── context/
│   └── AuthContext.jsx        # User, token, role state; login/logout helpers
│   └── CartContext.jsx        # Cart state, addToCart, updateQty, clearCart
├── components/
│   ├── layout/
│   │   ├── Navbar.jsx          # Role-conditional nav; hamburger < 768px
│   │   └── ProtectedRoute.jsx  # Redirects unauthenticated / wrong-role users
│   ├── auth/
│   │   ├── LoginForm.jsx
│   │   └── RegisterForm.jsx
│   ├── diagnosis/
│   │   ├── SymptomSelector.jsx
│   │   └── DiagnosisResults.jsx
│   ├── inventory/
│   │   ├── MedicineList.jsx
│   │   ├── MedicineCard.jsx    # Shows expiry alert badge when expiry_alert=true
│   │   ├── MedicineForm.jsx
│   │   └── StockDashboard.jsx
│   ├── knowledgeBase/
│   │   ├── ArticleList.jsx
│   │   └── CategoryTabs.jsx
│   ├── shop/
│   │   ├── ProductCatalog.jsx
│   │   ├── ProductCard.jsx
│   │   └── CartView.jsx
│   └── orders/
│       ├── CheckoutConfirmation.jsx
│       └── OrderHistory.jsx
└── pages/
    ├── LoginPage.jsx
    ├── RegisterPage.jsx
    ├── FarmerDashboard.jsx
    ├── DiagnosisPage.jsx
    ├── InventoryPage.jsx
    ├── KnowledgeBasePage.jsx
    ├── ShopPage.jsx
    ├── CheckoutPage.jsx
    └── OrderHistoryPage.jsx
```

### State Management

- **AuthContext**: Holds `{ user, token, role }`. Token stored in `localStorage` for persistence across page reloads. Axios interceptor reads from context on each request.
- **CartContext**: Holds `{ items: [{ medicine, quantity }] }`. Pure React state — not persisted. `addToCart(medicine)` increments quantity if the product is already present or initialises with `quantity: 1`. Setting quantity to 0 removes the line item.

---

## Diagnosis Engine

The engine is a pure Python function that runs synchronously inside the DRF view.

```python
def run_diagnosis(symptom_ids: list[int]) -> list[dict]:
    """
    For each Disease, compute:
        matched_weight = sum of weights for symptoms in symptom_ids
        total_weight   = sum of all weights for all symptoms of that disease
        match_score    = round(matched_weight / total_weight * 100, 1)

    Returns a list of result dicts sorted by match_score descending,
    only including diseases with match_score > 0.
    """
    results = []
    for disease in Disease.objects.prefetch_related('diseasesymptom_set'):
        symptom_weights = {
            ds.symptom_id: ds.weight
            for ds in disease.diseasesymptom_set.all()
        }
        total_weight = sum(symptom_weights.values())
        if total_weight == 0:
            continue
        matched_weight = sum(
            w for sid, w in symptom_weights.items() if sid in set(symptom_ids)
        )
        if matched_weight == 0:
            continue
        score = round(matched_weight / total_weight * 100, 1)
        results.append({
            'disease': disease,
            'match_score': score,
        })
    return sorted(results, key=lambda r: r['match_score'], reverse=True)
```

**Match Score Formula:**

```
match_score = round(
    sum(weight for symptom in submitted_symptoms if symptom in disease.symptoms)
    / sum(weight for symptom in disease.symptoms)
    * 100,
    1
)
```

---

## Expiry Alert Logic

Applied at the serializer layer so it is computed on every read:

```python
class MedicineSerializer(serializers.ModelSerializer):
    expiry_alert = serializers.SerializerMethodField()

    def get_expiry_alert(self, obj):
        today = date.today()
        return (obj.expiry_date - today).days <= 30
```

---

## Role-Based Permission Classes

```python
class IsFarmer(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == 'Farmer'
        )

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == 'Admin'
        )

class IsFarmerOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role in ('Farmer', 'Admin')
        )
```

---

## Error Handling

### Validation Errors (400)

DRF's default exception handler is extended to guarantee the `errors` key format:

```json
{
  "errors": {
    "symptom_ids": ["This field is required."],
    "expiry_date": ["Expiry date must be in the future."]
  }
}
```

### Unhandled Server Errors (500)

A custom exception handler logs the full traceback via Python's `logging` module and returns:

```json
{
  "message": "An unexpected error occurred."
}
```

### Frontend Error Display

Axios interceptors normalise error responses. Components receive a structured `{ fieldErrors, globalError }` object and render field-level messages inline and global messages in a toast/banner. Raw stack traces are never forwarded to the UI.

---

## Django Admin Registration

All domain models are registered with `ModelAdmin` classes:

| Model               | Key Admin Features                                             |
|---------------------|----------------------------------------------------------------|
| Disease             | Inline `DiseaseSymptomInline`; clean validates ≥1 symptom with weight > 0 |
| Symptom             | List display: name; search by name                             |
| Medicine            | List filter: category, expiry_date; search by name            |
| KnowledgeBaseArticle| List filter: category; search by title                        |
| Order               | List filter: farmer; ordering: -submitted_at; read-only line items |
| DiagnosisSession    | Read-only; filter by farmer                                    |

---

## Mobile-Responsive Design

Tailwind breakpoints used:

| Breakpoint | Min Width | Usage                                    |
|------------|-----------|------------------------------------------|
| (default)  | 0px       | Single-column layouts, full-width cards  |
| `sm`       | 640px     | Two-column grid for cards/tables         |
| `md`       | 768px     | Three-column grid; full horizontal nav   |
| `lg`       | 1024px    | Four-column product grid                 |

- Navigation: hamburger menu rendered below `md` using React state toggle; full horizontal menu at `md` and above.
- Tables: horizontally scrollable wrapper (`overflow-x-auto`) on small screens, standard table on `sm` and above.
- Cards: `grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3` pattern used across inventory and catalog pages.

---

## Backend Project Structure

```
backend/
├── config/
│   ├── settings.py
│   ├── urls.py           # includes api/v1/ router
│   └── wsgi.py
├── apps/
│   ├── accounts/         # User model, register/login views, JWT config
│   ├── diagnosis/        # Symptom, Disease, DiseaseSymptom, DiagnosisSession
│   ├── inventory/        # Medicine model, views, dosage calculator
│   ├── knowledge_base/   # KnowledgeBaseArticle model and views
│   └── orders/           # Order, OrderItem models, checkout and history views
└── manage.py
```

---

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system — essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Invalid credentials always denied

*For any* login attempt using credentials that do not match a registered user's username and password, the Backend SHALL return a 401 response.

**Validates: Requirements 1.3**

---

### Property 2: Protected endpoints reject unauthenticated requests

*For any* protected API endpoint, a request made without a valid Access Token SHALL receive a 401 response.

**Validates: Requirements 1.4, 1.5**

---

### Property 3: Role field accepts only valid values

*For any* registration request where the role field is not exactly "Farmer" or "Admin", the Backend SHALL return a 400 validation error and SHALL NOT create a User record.

**Validates: Requirements 2.1**

---

### Property 4: Farmer access to Admin-only endpoints is always forbidden

*For any* Farmer-authenticated request to any Admin-only endpoint, the Backend SHALL return a 403 response.

**Validates: Requirements 2.2**

---

### Property 5: Diagnosis match score formula correctness

*For any* Disease with a non-empty set of weighted Symptoms, and *for any* non-empty subset of those Symptoms submitted to the Diagnosis Engine, the computed Match Score SHALL equal `round(sum(weights of matched symptoms) / sum(all weights for that disease) * 100, 1)`.

**Validates: Requirements 3.3**

---

### Property 6: Diagnosis results are ranked by match score descending

*For any* non-empty symptom submission to the diagnosis endpoint, the returned list of results SHALL be sorted such that for every adjacent pair of results, the first result's match_score is greater than or equal to the second result's match_score.

**Validates: Requirements 3.4**

---

### Property 7: Empty symptom submission is always rejected

*For any* request to the diagnosis endpoint with an empty symptom_ids list, the Backend SHALL return a 400 response with a validation error message.

**Validates: Requirements 3.5**

---

### Property 8: Diagnosis session persistence round-trip

*For any* successfully submitted diagnosis session, querying the authenticated Farmer's diagnosis history SHALL include a record containing the submitted symptoms and the top-ranked result from that session.

**Validates: Requirements 3.7**

---

### Property 9: Medicine validation rejects invalid data

*For any* attempt to create or update a Medicine record with a stock_quantity less than zero or with an expiry_date that is not in the future, the Backend SHALL return a 400 response and SHALL NOT persist the record.

**Validates: Requirements 4.3, 4.7**

---

### Property 10: Expiry alert flag correctness

*For any* Medicine record retrieved from the API, the `expiry_alert` field SHALL be `true` if and only if the number of days between the current server date and the Medicine's `expiry_date` is less than or equal to 30.

**Validates: Requirements 4.4**

---

### Property 11: Dosage calculation correctness

*For any* valid Medicine identifier and any positive integer bird count, the `total_dosage` returned by the dosage calculator endpoint SHALL equal `dosage_per_bird × bird_count`, and the `unit` SHALL match the Medicine's `dosage_unit`.

**Validates: Requirements 4.6**

---

### Property 12: Knowledge base category filter invariant

*For any* GET request to the Knowledge Base endpoint with a `?category=` filter, every article in the returned list SHALL have a `category` field equal to the requested filter value.

**Validates: Requirements 5.2**

---

### Property 13: Knowledge base admin update round-trip

*For any* Knowledge Base article created or updated via Django Admin, the next call to the Knowledge Base API endpoint SHALL return a record that reflects the most recently saved title, category, and body text.

**Validates: Requirements 5.4**

---

### Property 14: Cart add-to-cart increment invariant

*For any* cart state and any product, adding a product already present in the cart SHALL increment that product's quantity by exactly one, and adding a product not yet in the cart SHALL add it with quantity one. In both cases the total number of distinct line items changes only by zero or one respectively.

**Validates: Requirements 6.3**

---

### Property 15: Cart grand total arithmetic invariant

*For any* cart state containing one or more line items, the grand total SHALL equal the sum of `quantity × unit_price` for every line item in the cart.

**Validates: Requirements 6.4**

---

### Property 16: Zero-quantity removal invariant

*For any* cart state where a line item's quantity is set to zero, that line item SHALL be absent from the resulting cart state, and all other line items SHALL be unchanged.

**Validates: Requirements 6.5**

---

### Property 17: Order creation round-trip

*For any* non-empty cart submitted to the checkout endpoint by an authenticated Farmer, the Backend SHALL return a 201 response with an Order ID, and a subsequent GET to the order history endpoint SHALL include an Order record with that ID, the correct Farmer, and line items matching the submitted cart contents.

**Validates: Requirements 7.1**

---

### Property 18: Empty cart checkout is always rejected

*For any* checkout request submitted with an empty items list, the Backend SHALL return a 400 response with a validation error message.

**Validates: Requirements 7.2**

---

### Property 19: Order history ordering invariant

*For any* Farmer with two or more recorded orders, the order history endpoint SHALL return the orders such that for every adjacent pair, the first order's `submitted_at` timestamp is greater than or equal to the second order's `submitted_at` timestamp.

**Validates: Requirements 7.5**

---

### Property 20: Disease requires at least one weighted symptom

*For any* attempt to save a Disease record via Django Admin with no associated Symptoms or with all associated Symptom weights equal to zero or below, the Backend SHALL raise a validation error and SHALL NOT persist the Disease record.

**Validates: Requirements 8.2**

---

### Property 21: All API responses carry JSON Content-Type

*For any* request to any `/api/v1/` endpoint, the response SHALL have a `Content-Type` header of `application/json`.

**Validates: Requirements 10.1**

---

### Property 22: Validation errors always produce field-level error objects

*For any* request to any endpoint that fails input validation, the Backend SHALL return a 400 response whose JSON body contains an `errors` key mapping each invalid field name to a non-empty list of error message strings.

**Validates: Requirements 10.2**
