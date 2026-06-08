# Implementation Plan: Poultry Health & Medicine Management System

## Overview

Incrementally build the full-stack application: start with the Django project scaffold and data models, wire up authentication and permissions, implement each feature domain (diagnosis, inventory, knowledge base, e-commerce/orders) on the backend, then build the React SPA on the frontend, and finish with integration wiring and responsive polish.

---

## Tasks

- [x] 1. Scaffold backend project structure and core configuration
  - Create the `backend/` directory tree (`config/`, `apps/accounts`, `apps/diagnosis`, `apps/inventory`, `apps/knowledge_base`, `apps/orders`)
  - Configure `settings.py`: PostgreSQL database, installed apps, SimpleJWT, CORS, and DRF defaults
  - Set up `config/urls.py` with the `/api/v1/` prefix router
  - _Requirements: 10.4_

- [x] 2. Implement the User model and authentication endpoints
  - [x] 2.1 Create the custom User model extending `AbstractUser` with `role` field (choices: Farmer, Admin)
    - Write migration for the custom User model
    - _Requirements: 1.1, 2.1_
  - [x] 2.2 Implement `IsFarmer`, `IsAdmin`, and `IsFarmerOrAdmin` DRF permission classes
    - Write the three permission classes in `apps/accounts/permissions.py`
    - _Requirements: 2.2, 2.3_
  - [x] 2.3 Implement the registration endpoint (`POST /api/v1/auth/register/`)
    - Write `RegisterSerializer` with role validation (only "Farmer" or "Admin" accepted)
    - Write the register view returning 201 on success
    - _Requirements: 1.1, 2.1_
  - [ ]* 2.4 Write property test for role validation (Property 3)
    - **Property 3: Role field accepts only valid values**
    - **Validates: Requirements 2.1**
  - [x] 2.5 Implement the login endpoint (`POST /api/v1/auth/login/`)
    - Write the login view using SimpleJWT to return `{ "access": "...", "role": "..." }`
    - _Requirements: 1.2, 1.3_
  - [ ]* 2.6 Write property test for invalid credential rejection (Property 1)
    - **Property 1: Invalid credentials always denied**
    - **Validates: Requirements 1.3**
  - [ ]* 2.7 Write property test for unauthenticated endpoint rejection (Property 2)
    - **Property 2: Protected endpoints reject unauthenticated requests**
    - **Validates: Requirements 1.4, 1.5**
  - [ ]* 2.8 Write property test for Farmer access to Admin-only endpoints (Property 4)
    - **Property 4: Farmer access to Admin-only endpoints is always forbidden**
    - **Validates: Requirements 2.2**

- [x] 3. Implement Symptom, Disease, and DiseaseSymptom models with Django Admin
  - [x] 3.1 Create `Symptom`, `Disease`, and `DiseaseSymptom` models in `apps/diagnosis/models.py`
    - Write models per data model spec; include `weight > 0` constraint and unique_together on DiseaseSymptom
    - Write and apply migrations
    - _Requirements: 3.1, 8.1, 8.2_
  - [x] 3.2 Register Symptom and Disease in Django Admin
    - Create `DiseaseSymptomInline`; add `clean()` validating ≥1 symptom with weight > 0 on Disease
    - _Requirements: 8.1, 8.2, 8.3_
  - [ ]* 3.3 Write property test for Disease-requires-symptom validation (Property 20)
    - **Property 20: Disease requires at least one weighted symptom**
    - **Validates: Requirements 8.2**

- [x] 4. Implement the Diagnosis Engine and diagnosis API endpoints
  - [x] 4.1 Implement the `run_diagnosis` function in `apps/diagnosis/engine.py`
    - Pure Python function: compute `match_score = round(matched_weight / total_weight * 100, 1)` per disease; return sorted descending list of dicts
    - _Requirements: 3.3, 3.4_
  - [ ]* 4.2 Write property test for diagnosis match score formula (Property 5)
    - **Property 5: Diagnosis match score formula correctness**
    - **Validates: Requirements 3.3**
  - [ ]* 4.3 Write property test for diagnosis result ordering (Property 6)
    - **Property 6: Diagnosis results are ranked by match score descending**
    - **Validates: Requirements 3.4**
  - [x] 4.4 Implement `GET /api/v1/symptoms/` endpoint
    - Write `SymptomSerializer` and list view (Farmer-only)
    - _Requirements: 3.2_
  - [x] 4.5 Implement `POST /api/v1/diagnosis/` endpoint
    - Write `DiagnosisSerializer` validating non-empty `symptom_ids`; call `run_diagnosis`; persist `DiagnosisSession`; return ranked results
    - _Requirements: 3.3, 3.4, 3.5, 3.7_
  - [ ]* 4.6 Write property test for empty symptom submission rejection (Property 7)
    - **Property 7: Empty symptom submission is always rejected**
    - **Validates: Requirements 3.5**
  - [x] 4.7 Implement `GET /api/v1/diagnosis/history/` endpoint
    - Write list view returning the authenticated Farmer's past `DiagnosisSession` records
    - _Requirements: 3.7_
  - [ ]* 4.8 Write property test for diagnosis session persistence round-trip (Property 8)
    - **Property 8: Diagnosis session persistence round-trip**
    - **Validates: Requirements 3.7**

- [x] 5. Checkpoint — Ensure all diagnosis-related tests pass
  - Ensure all tests pass; ask the user if questions arise.

- [ ] 6. Implement Medicine model, inventory endpoints, and Django Admin
  - [x] 6.1 Create the `Medicine` model in `apps/inventory/models.py`
    - Write model per data model spec; write and apply migration
    - _Requirements: 4.1_
  - [ ] 6.2 Implement `MedicineSerializer` with `expiry_alert` computed field
    - Implement `get_expiry_alert`: return `True` if `(expiry_date - today).days <= 30`
    - _Requirements: 4.4_
  - [ ]* 6.3 Write property test for expiry alert flag correctness (Property 10)
    - **Property 10: Expiry alert flag correctness**
    - **Validates: Requirements 4.4**
  - [ ] 6.4 Implement medicine CRUD endpoints (`GET/POST /api/v1/medicines/`, `GET/PATCH /api/v1/medicines/{id}/`)
    - Write views with `IsFarmer` permission; validate stock_quantity >= 0 and expiry_date is future on create; validate stock_quantity >= 0 on update
    - _Requirements: 4.2, 4.3, 4.7_
  - [ ]* 6.5 Write property test for medicine validation (Property 9)
    - **Property 9: Medicine validation rejects invalid data**
    - **Validates: Requirements 4.3, 4.7**
  - [ ] 6.6 Implement dosage calculator endpoint (`GET /api/v1/medicines/dosage-calculator/`)
    - Accept `?medicine_id=&bird_count=` query params; return `total_dosage = dosage_per_bird × bird_count` and unit
    - _Requirements: 4.6_
  - [ ]* 6.7 Write property test for dosage calculation correctness (Property 11)
    - **Property 11: Dosage calculation correctness**
    - **Validates: Requirements 4.6**
  - [ ] 6.8 Register `Medicine` in Django Admin
    - Add list filter by category and expiry_date; search by name
    - _Requirements: 8.1_

- [ ] 7. Implement Knowledge Base model and public endpoint
  - [x] 7.1 Create `KnowledgeBaseArticle` model in `apps/knowledge_base/models.py`
    - Write model per data model spec with category choices; write and apply migration
    - _Requirements: 5.1_
  - [ ] 7.2 Implement `GET /api/v1/knowledge-base/` public endpoint
    - Write public (no-auth) list view with optional `?category=` filter
    - _Requirements: 5.2, 5.3, 5.5_
  - [ ]* 7.3 Write property test for knowledge base category filter invariant (Property 12)
    - **Property 12: Knowledge base category filter invariant**
    - **Validates: Requirements 5.2**
  - [ ]* 7.4 Write property test for knowledge base admin update round-trip (Property 13)
    - **Property 13: Knowledge base admin update round-trip**
    - **Validates: Requirements 5.4**
  - [ ] 7.5 Register `KnowledgeBaseArticle` in Django Admin
    - Add list filter by category; search by title
    - _Requirements: 8.1_

- [ ] 8. Implement Orders, Checkout, and Django Admin integration
  - [x] 8.1 Create `Order` and `OrderItem` models in `apps/orders/models.py`
    - Write models per data model spec; write and apply migration
    - _Requirements: 7.1_
  - [-] 8.2 Implement `POST /api/v1/orders/` checkout endpoint
    - Validate `items` list is non-empty; capture unit_price at time of order; compute total_amount; persist Order + OrderItems; return 201 with order ID
    - _Requirements: 7.1, 7.2, 7.3_
  - [ ]* 8.3 Write property test for order creation round-trip (Property 17)
    - **Property 17: Order creation round-trip**
    - **Validates: Requirements 7.1**
  - [ ]* 8.4 Write property test for empty cart checkout rejection (Property 18)
    - **Property 18: Empty cart checkout is always rejected**
    - **Validates: Requirements 7.2**
  - [ ] 8.5 Implement `GET /api/v1/orders/` and `GET /api/v1/orders/{id}/` endpoints
    - Return farmer's orders ordered by `submitted_at` descending; include line items on the detail view
    - _Requirements: 7.5_
  - [ ]* 8.6 Write property test for order history ordering invariant (Property 19)
    - **Property 19: Order history ordering invariant**
    - **Validates: Requirements 7.5**
  - [ ] 8.7 Implement `GET /api/v1/catalog/` endpoint
    - Return all Medicine records (name, description, category, unit_price, stock_quantity) with `IsFarmer` permission
    - _Requirements: 6.1_
  - [ ] 8.8 Register `Order` and `OrderItem` in Django Admin
    - Add list filter by farmer; order by `-submitted_at`; read-only line items inline
    - _Requirements: 8.1, 8.4_

- [ ] 9. Implement custom error handling and API response consistency
  - [ ] 9.1 Write custom DRF exception handler in `config/exceptions.py`
    - Wrap all validation errors in `{ "errors": { field: [messages] } }` format
    - Catch unhandled exceptions: log full traceback; return `{ "message": "An unexpected error occurred." }`
    - _Requirements: 10.1, 10.2, 10.3_
  - [ ]* 9.2 Write property test for JSON Content-Type invariant (Property 21)
    - **Property 21: All API responses carry JSON Content-Type**
    - **Validates: Requirements 10.1**
  - [ ]* 9.3 Write property test for validation error format invariant (Property 22)
    - **Property 22: Validation errors always produce field-level error objects**
    - **Validates: Requirements 10.2**

- [ ] 10. Checkpoint — Ensure all backend tests pass
  - Ensure all backend tests pass; ask the user if questions arise.

- [ ] 11. Scaffold React frontend and shared infrastructure
  - [ ] 11.1 Initialise Vite + React project in `frontend/`; install Tailwind CSS, React Router, and Axios
    - Configure Tailwind in `tailwind.config.js` and `index.css`
    - Set up project directory structure per component architecture spec
    - _Requirements: 9.1_
  - [ ] 11.2 Implement `AuthContext` and Axios instance with Bearer token interceptor
    - Create `src/context/AuthContext.jsx` holding `{ user, token, role }`; persist token to `localStorage`
    - Create `src/api/axios.js` Axios instance; attach `Authorization: Bearer <token>` on each request
    - _Requirements: 1.6_
  - [ ] 11.3 Implement `CartContext` for client-side cart state
    - Create `src/context/CartContext.jsx` with `addToCart`, `updateQty`, `clearCart`; `addToCart` increments if product present, else adds with quantity 1; setting quantity to 0 removes the item
    - _Requirements: 6.3, 6.5_
  - [ ]* 11.4 Write property test for cart add-to-cart increment invariant (Property 14)
    - **Property 14: Cart add-to-cart increment invariant**
    - **Validates: Requirements 6.3**
  - [ ]* 11.5 Write property test for cart grand total arithmetic invariant (Property 15)
    - **Property 15: Cart grand total arithmetic invariant**
    - **Validates: Requirements 6.4**
  - [ ]* 11.6 Write property test for zero-quantity removal invariant (Property 16)
    - **Property 16: Zero-quantity removal invariant**
    - **Validates: Requirements 6.5**
  - [ ] 11.7 Implement `ProtectedRoute` component and responsive `Navbar`
    - `ProtectedRoute.jsx`: redirect unauthenticated or wrong-role users
    - `Navbar.jsx`: role-conditional nav links; hamburger menu toggle below 768px; full horizontal nav at md and above
    - _Requirements: 2.4, 9.2_

- [ ] 12. Implement authentication pages
  - [ ] 12.1 Implement `LoginForm` and `LoginPage`
    - Call `POST /api/v1/auth/login/`; store token and role in `AuthContext`; redirect to role-appropriate dashboard
    - Display field-level and global errors from backend response
    - _Requirements: 1.2, 1.3, 1.7, 10.5_
  - [ ] 12.2 Implement `RegisterForm` and `RegisterPage`
    - Call `POST /api/v1/auth/register/`; redirect to login on success; display validation errors inline
    - _Requirements: 1.1, 1.7, 10.5_

- [ ] 13. Implement Diagnosis feature on the frontend
  - [ ] 13.1 Implement `SymptomSelector` component and `DiagnosisPage`
    - Fetch symptoms from `GET /api/v1/symptoms/`; render multi-select checklist; submit selected IDs to `POST /api/v1/diagnosis/`
    - _Requirements: 3.2_
  - [ ] 13.2 Implement `DiagnosisResults` component
    - Render ranked list of disease results showing name, match score, severity, and treatment recommendations
    - _Requirements: 3.6_

- [ ] 14. Implement Medicine Inventory feature on the frontend
  - [ ] 14.1 Implement `MedicineList`, `MedicineCard`, and `InventoryPage`
    - Fetch medicines from `GET /api/v1/medicines/`; display name, stock quantity, dosage info, expiry date; show expiry alert badge when `expiry_alert=true`
    - _Requirements: 4.2, 4.5_
  - [ ] 14.2 Implement `MedicineForm` for adding new medicine records
    - POST to `POST /api/v1/medicines/`; validate and display field-level errors; redirect to inventory list on success
    - _Requirements: 4.3_
  - [ ] 14.3 Implement `StockDashboard` component
    - Display total medicine types count, count of low-stock medicines (quantity < 10), count with active expiry alerts
    - Include inline stock quantity update (PATCH) for each medicine
    - _Requirements: 4.7, 4.8_

- [ ] 15. Implement Knowledge Base feature on the frontend
  - [ ] 15.1 Implement `ArticleList`, `CategoryTabs`, and `KnowledgeBasePage`
    - Fetch from `GET /api/v1/knowledge-base/` (no auth required); render category tabs (Best Practices, Vaccination Schedule, Nutrition); pass `?category=` filter on tab switch; render article title and body
    - _Requirements: 5.2, 5.3_

- [ ] 16. Implement E-Commerce Catalog and Cart on the frontend
  - [ ] 16.1 Implement `ProductCatalog`, `ProductCard`, and `ShopPage`
    - Fetch from `GET /api/v1/catalog/`; render product name, description, unit price, available stock; "Add to Cart" button calls `CartContext.addToCart`
    - _Requirements: 6.1, 6.2, 6.3_
  - [ ] 16.2 Implement `CartView` component
    - Render all line items (product name, quantity, unit price, line total); display grand total (`Σ quantity × unit_price`); allow quantity update to zero to remove item; "Clear Cart" button calls `CartContext.clearCart`
    - _Requirements: 6.4, 6.5, 6.6_

- [ ] 17. Implement Checkout and Order History on the frontend
  - [ ] 17.1 Implement `CheckoutConfirmation` component and `CheckoutPage`
    - POST cart items to `POST /api/v1/orders/`; on 201 display order ID, line items, total amount, and success message; on error display validation errors
    - _Requirements: 7.1, 7.4_
  - [ ] 17.2 Implement `OrderHistory` component and `OrderHistoryPage`
    - Fetch from `GET /api/v1/orders/`; list orders with order ID, submission date, total amount; link to `GET /api/v1/orders/{id}/` for detail view
    - _Requirements: 7.5, 7.6_

- [ ] 18. Implement Farmer Dashboard and wire all frontend routes
  - [ ] 18.1 Implement `FarmerDashboard` page
    - Render summary widgets linking to Diagnosis, Inventory, Shop, Knowledge Base, and Order History sections
    - _Requirements: 1.7_
  - [ ] 18.2 Wire all React Router routes and `ProtectedRoute` guards
    - Register all page routes in `App.jsx`; apply `ProtectedRoute` with correct role checks to all protected pages; confirm public route for Knowledge Base and auth pages
    - _Requirements: 1.7, 2.4_
  - [ ] 18.3 Implement frontend Axios error normalisation
    - In the Axios response interceptor, transform error responses into `{ fieldErrors, globalError }` objects; ensure raw stack traces are never displayed to users
    - _Requirements: 10.5_

- [ ] 19. Apply mobile-responsive Tailwind CSS layouts across all pages
  - [ ] 19.1 Apply responsive grid and table layouts to Inventory, Catalog, and Knowledge Base pages
    - Use `grid-cols-1 sm:grid-cols-2 lg:grid-cols-3` for card grids; wrap tables in `overflow-x-auto` containers
    - Verify single-column layout below 640px and multi-column at 640px and above
    - _Requirements: 9.1, 9.3_
  - [ ] 19.2 Verify hamburger navigation behaviour and viewport coverage
    - Confirm hamburger menu renders below 768px; confirm full horizontal nav renders at 768px and above
    - Confirm all pages render usably from 320px to 1920px without horizontal scroll
    - _Requirements: 9.1, 9.2_

- [ ] 20. Final checkpoint — Ensure all tests pass
  - Ensure all backend and frontend tests pass; ask the user if questions arise.

---

## Notes

- Tasks marked with `*` are optional and can be skipped for a faster MVP delivery.
- The backend uses **Python / Django REST Framework** with **pytest-django** for testing; property-based tests use **Hypothesis**.
- The frontend uses **React (Vite)** with **Vitest** and **fast-check** for property-based tests.
- Each task references specific requirements for traceability.
- Checkpoints ensure incremental validation after each major domain is completed.
- Property tests validate the 22 universal correctness properties defined in the design document.
- Unit tests validate specific examples and edge cases not covered by property tests.
- All 22 correctness properties from the design are mapped to specific sub-tasks above.

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1"] },
    { "id": 1, "tasks": ["2.1", "2.2"] },
    { "id": 2, "tasks": ["2.3", "2.5", "3.1"] },
    { "id": 3, "tasks": ["2.4", "2.6", "2.7", "2.8", "3.2", "4.1"] },
    { "id": 4, "tasks": ["3.3", "4.2", "4.3", "4.4", "4.5"] },
    { "id": 5, "tasks": ["4.6", "4.7", "6.1", "7.1"] },
    { "id": 6, "tasks": ["4.8", "6.2", "7.2", "8.1"] },
    { "id": 7, "tasks": ["6.3", "6.4", "7.3", "7.4", "7.5", "8.2"] },
    { "id": 8, "tasks": ["6.5", "6.6", "8.3", "8.4", "8.5"] },
    { "id": 9, "tasks": ["6.7", "6.8", "8.6", "8.7", "8.8", "9.1"] },
    { "id": 10, "tasks": ["9.2", "9.3", "11.1"] },
    { "id": 11, "tasks": ["11.2", "11.3"] },
    { "id": 12, "tasks": ["11.4", "11.5", "11.6", "11.7"] },
    { "id": 13, "tasks": ["12.1", "12.2"] },
    { "id": 14, "tasks": ["13.1", "14.1", "15.1", "16.1"] },
    { "id": 15, "tasks": ["13.2", "14.2", "16.2"] },
    { "id": 16, "tasks": ["14.3", "17.1"] },
    { "id": 17, "tasks": ["17.2", "18.1"] },
    { "id": 18, "tasks": ["18.2", "18.3"] },
    { "id": 19, "tasks": ["19.1", "19.2"] }
  ]
}
```
