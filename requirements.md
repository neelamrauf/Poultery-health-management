# Requirements Document

## Introduction

The Poultry Health & Medicine Management System is a web application that helps poultry farmers and small-scale flock keepers monitor flock health, diagnose common poultry diseases using a rule-based symptom checker, manage medicine inventory, and purchase supplies through a mock e-commerce interface. The system provides an advisory knowledge base covering best practices, vaccination schedules, and nutrition guidance. It is built on a Django REST Framework backend with a React (Vite + Tailwind CSS) frontend and targets both Farmer and Admin user roles.

## Glossary

- **System**: The Poultry Health & Medicine Management System web application as a whole.
- **Backend**: The Django + Django REST Framework API server backed by PostgreSQL.
- **Frontend**: The React (Vite + Tailwind CSS) single-page application served to the browser.
- **Farmer**: An authenticated user who manages flocks, runs diagnoses, manages their medicine inventory, and places orders.
- **Admin**: An authenticated user with elevated privileges who manages the knowledge base, disease/symptom data, medicine catalog, and all user orders via Django Admin.
- **Diagnosis Engine**: The rule-based component that scores diseases against a submitted set of symptoms and returns ranked results.
- **Knowledge Base**: Static advisory content (best practices, vaccination schedules, nutrition advice) managed via Django Admin.
- **Medicine**: A product record containing name, description, stock quantity, expiry date, dosage information, and unit price.
- **Order**: A record of a Farmer's mock checkout transaction including line items and total cost; no real payment is processed.
- **Symptom**: A named clinical observation that can be associated with one or more Diseases with a weight value.
- **Disease**: A named poultry disease record containing a symptom profile, severity level, and treatment recommendations.
- **Cart**: Frontend React state holding selected Medicine line items before checkout; not persisted server-side.
- **Match Score**: A percentage value calculated by the Diagnosis Engine representing how closely a submitted symptom set matches a Disease's symptom profile.
- **SimpleJWT**: The Django SimpleJWT library used to issue short-lived JWT access tokens for API authentication.
- **Access Token**: A short-lived JWT issued by the Backend upon successful login, used to authenticate subsequent API requests.

---

## Requirements

### Requirement 1 — User Authentication

**User Story:** As a user, I want to register, log in, and receive an access token, so that I can securely access role-appropriate features of the system.

#### Acceptance Criteria

1. THE Backend SHALL expose a registration endpoint that accepts a username, email, password, and role (Farmer or Admin), creates a User record, and returns a 201 response.
2. WHEN a user submits valid credentials to the login endpoint, THE Backend SHALL return a JWT access token and the user's role in the response body.
3. IF a user submits invalid credentials to the login endpoint, THEN THE Backend SHALL return a 401 response with an error message.
4. WHILE a user holds a valid Access Token, THE Backend SHALL authenticate all protected API requests bearing that token via the Authorization header.
5. IF a request to a protected endpoint is made without a valid Access Token, THEN THE Backend SHALL return a 401 response.
6. THE Frontend SHALL store the Access Token in memory or browser local storage and attach it as a Bearer token to every authenticated API request via Axios.
7. THE Frontend SHALL display a login form and a registration form, and redirect the user to the appropriate dashboard after successful authentication based on role.

---

### Requirement 2 — Role-Based Access Control

**User Story:** As a system operator, I want Farmer and Admin roles enforced on every endpoint, so that users can only access features appropriate to their role.

#### Acceptance Criteria

1. THE Backend SHALL store a role field on the User model with exactly two permitted values: Farmer and Admin.
2. WHEN a Farmer attempts to access an Admin-only endpoint, THE Backend SHALL return a 403 response.
3. WHEN an Admin authenticates, THE Backend SHALL permit access to all Farmer endpoints and all Admin-only management endpoints.
4. THE Frontend SHALL render navigation and UI elements conditionally based on the authenticated user's role, hiding Admin-only sections from Farmer users.

---

### Requirement 3 — Symptom Checker and Disease Diagnosis

**User Story:** As a Farmer, I want to select symptoms my flock is showing and receive a ranked list of probable diseases with treatment advice, so that I can make informed decisions about flock care.

#### Acceptance Criteria

1. THE Backend SHALL maintain a Symptom table and a Disease table linked by a many-to-many relationship with a numeric weight per symptom–disease pair.
2. THE Frontend SHALL display a symptom selection form listing all available Symptoms retrieved from the Backend, allowing the Farmer to select one or more Symptoms.
3. WHEN a Farmer submits a non-empty set of selected Symptoms, THE Diagnosis Engine SHALL calculate a Match Score for each Disease by dividing the sum of weights of matched symptoms by the sum of total weights for all symptoms associated with that Disease, expressed as a percentage rounded to one decimal place.
4. WHEN the Diagnosis Engine completes scoring, THE Backend SHALL return a ranked list of Diseases ordered by Match Score descending, each entry including the Disease name, Match Score, severity level, and treatment recommendations.
5. IF a Farmer submits an empty symptom set to the diagnosis endpoint, THEN THE Backend SHALL return a 400 response with a validation error message.
6. THE Frontend SHALL display the ranked diagnosis results in a clear list, showing each Disease's name, Match Score, severity level, and treatment recommendations.
7. THE Backend SHALL persist each diagnosis session as a record associated with the authenticated Farmer, including the submitted symptoms and the top-ranked result.

---

### Requirement 4 — Medicine Inventory Management

**User Story:** As a Farmer, I want to track my on-hand medicine stock, dosage information, and expiry dates, so that I can ensure medicines are available and safe to use.

#### Acceptance Criteria

1. THE Backend SHALL maintain a Medicine table with fields for name, description, category, unit price, stock quantity, dosage information, and expiry date.
2. THE Frontend SHALL display a medicine inventory dashboard listing all Medicine records accessible to the authenticated Farmer, showing name, stock quantity, dosage information, and expiry date.
3. WHEN a Farmer adds a new Medicine record via the Frontend form, THE Backend SHALL validate that stock quantity is a non-negative integer and expiry date is a future date, then persist the record and return a 201 response.
4. IF a Medicine record's expiry date is within 30 days of the current server date, THEN THE Backend SHALL include an expiry_alert flag set to true in the Medicine record's API response.
5. THE Frontend SHALL display a visual alert indicator on any Medicine card where expiry_alert is true.
6. THE Backend SHALL expose an endpoint that accepts a bird count and a Medicine identifier, and returns the calculated total dosage as dosage_per_bird multiplied by bird_count with the unit of measurement.
7. WHEN a Farmer updates the stock quantity of a Medicine record, THE Backend SHALL validate the new quantity is a non-negative integer and persist the updated value.
8. THE Frontend SHALL display a stock tracking dashboard summarising total Medicine types, medicines with low stock (quantity below 10), and medicines with active expiry alerts.

---

### Requirement 5 — Poultry Care Knowledge Base

**User Story:** As a Farmer, I want to browse advisory articles on best practices, vaccination schedules, and nutrition, so that I can improve flock management.

#### Acceptance Criteria

1. THE Backend SHALL maintain Knowledge Base content as structured records (title, category, body text, last updated date) with category values of: Best Practices, Vaccination Schedule, and Nutrition.
2. THE Backend SHALL expose a public read-only endpoint that returns all Knowledge Base records, filterable by category.
3. THE Frontend SHALL display a Knowledge Base section with tabs or filter controls for each category, rendering the title and body text of each record.
4. WHEN an Admin updates or creates a Knowledge Base record via Django Admin, THE Backend SHALL immediately reflect the change in the Knowledge Base API endpoint response.
5. IF no Knowledge Base records exist for a requested category filter, THEN THE Backend SHALL return an empty list with a 200 response.

---

### Requirement 6 — E-Commerce Product Catalog

**User Story:** As a Farmer, I want to browse available medicines and supplies in a product catalog and add items to a cart, so that I can select products for purchase.

#### Acceptance Criteria

1. THE Backend SHALL expose a product catalog endpoint that returns all Medicine records with name, description, category, unit price, and available stock quantity.
2. THE Frontend SHALL display a product catalog page rendering each product's name, description, unit price, and an "Add to Cart" control.
3. WHEN a Farmer clicks "Add to Cart" for a product, THE Frontend SHALL add the product and a default quantity of one to the Cart state, incrementing quantity if the product is already present in the Cart.
4. THE Frontend SHALL display a cart view listing all Cart line items with product name, quantity, unit price, and line total, and a cart grand total calculated as the sum of all line totals.
5. WHEN a Farmer updates the quantity of a Cart line item to zero, THE Frontend SHALL remove that line item from the Cart state.
6. THE Frontend SHALL allow a Farmer to clear all items from the Cart in a single action.

---

### Requirement 7 — Mock Checkout and Order Recording

**User Story:** As a Farmer, I want to place an order from my cart and receive confirmation, so that I have a record of my intended purchase.

#### Acceptance Criteria

1. WHEN a Farmer submits a non-empty Cart to the checkout endpoint, THE Backend SHALL create an Order record containing the Farmer's user ID, submission timestamp, line items (product ID, quantity, unit price at time of order), and total amount, then return a 201 response with the Order ID and a success message.
2. IF a Farmer submits an empty Cart to the checkout endpoint, THEN THE Backend SHALL return a 400 response with a validation error message.
3. THE Backend SHALL NOT process any real payment transactions; the checkout endpoint SHALL simulate success by persisting the Order record and returning a success response.
4. THE Frontend SHALL display a checkout confirmation page showing the Order ID, line items, total amount, and a success message upon receiving a 201 response from the checkout endpoint.
5. WHEN a Farmer views their order history, THE Backend SHALL return all Order records associated with the authenticated Farmer ordered by submission timestamp descending.
6. THE Frontend SHALL display an order history page listing past orders with Order ID, submission date, and total amount.

---

### Requirement 8 — Admin Management via Django Admin

**User Story:** As an Admin, I want to manage diseases, symptoms, medicines, knowledge base content, and orders through Django Admin, so that I can maintain accurate system data without custom UI development.

#### Acceptance Criteria

1. THE Backend SHALL register Disease, Symptom, Medicine, Knowledge Base, and Order models with the Django Admin interface.
2. WHEN an Admin creates or updates a Disease record in Django Admin, THE Backend SHALL enforce that the Disease record contains at least one associated Symptom with a positive numeric weight.
3. WHEN an Admin creates or updates a Symptom record in Django Admin, THE Backend SHALL permit the symptom to be associated with zero or more Disease records.
4. THE Backend SHALL expose all Order records in Django Admin with filtering by Farmer and ordering by submission timestamp.

---

### Requirement 9 — Mobile-Responsive Frontend

**User Story:** As a Farmer, I want to access the system from a mobile device or desktop browser, so that I can manage flock health in the field as well as at a desk.

#### Acceptance Criteria

1. THE Frontend SHALL apply Tailwind CSS responsive utility classes so that all pages render usably at viewport widths from 320px to 1920px without horizontal scrolling.
2. THE Frontend SHALL render a collapsible or hamburger navigation menu on viewport widths below 768px.
3. THE Frontend SHALL display data tables and card-based layouts in a single-column layout on viewport widths below 640px and in multi-column layouts on viewport widths of 640px and above.

---

### Requirement 10 — API Design and Error Handling

**User Story:** As a developer, I want consistent, well-structured API responses and error handling, so that the Frontend can reliably parse results and display meaningful feedback to users.

#### Acceptance Criteria

1. THE Backend SHALL return all API responses as JSON with a Content-Type header of application/json.
2. WHEN a validation error occurs on any endpoint, THE Backend SHALL return a 400 response containing a JSON object with a field-level errors key mapping each invalid field name to a list of error message strings.
3. WHEN an unhandled server error occurs, THE Backend SHALL return a 500 response containing a JSON object with a message key set to "An unexpected error occurred." and SHALL log the full exception traceback to the server log.
4. THE Backend SHALL version all API routes under the /api/v1/ path prefix.
5. THE Frontend SHALL display user-facing error messages derived from Backend error responses, and SHALL NOT expose raw stack traces or internal error details to the user.
