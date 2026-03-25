# Agriculture Crop Recommendation System

A Django-based machine learning web application that recommends the most suitable crop based on soil nutrients and climate conditions.  
This project also includes Single Sign-On (SSO) authentication using Keycloak, integrated with Django through Authlib, with Keycloak running locally using Docker.

---

## Overview

This project helps users predict the best crop for cultivation by taking agricultural input parameters such as:

- Nitrogen (N)
- Phosphorus (P)
- Potassium (K)
- Temperature
- Humidity
- pH
- Rainfall

The system supports:

- Single crop prediction through a web form
- Batch crop prediction through CSV upload
- User authentication with Keycloak SSO
- Profile completion flow for user-specific agricultural details
- Downloadable prediction results

---

## Features

### Machine Learning Features
- Crop prediction using multiple trained ML models
- Ensemble-based recommendation with majority voting
- Confidence score for predictions
- Batch prediction through CSV upload
- Download predictions as a CSV file

### Authentication Features
- Single Sign-On (SSO) with Keycloak
- Django integration using Authlib
- Login, callback, logout, and protected routes
- User session handling
- User profile creation linked with Keycloak user identity

### User Features
- Profile completion after first login
- Stores app-specific user details such as:
  - phone
  - location
  - soil type
  - farm size

---

## Tech Stack

**Backend**
- Python
- Django

**Machine Learning**
- Scikit-learn
- LightGBM
- XGBoost
- Pickle for serialized models

**Authentication**
- Keycloak
- Authlib
- OpenID Connect (OIDC)

**Database**
- SQLite (default)

**Deployment / Local Infrastructure**
- Docker (for running Keycloak locally)

---

## Project Structure

```bash
Agriculture_Crop_recommendation_system/
│
├── crop_recommendation/        # Django project settings and main URLs
├── predictions/                # ML logic, forms, views, models, trained .pkl files
├── users/                      # SSO login/logout/profile handling
├── templates/                  # HTML templates
├── media/                      # Uploaded/generated files
├── db.sqlite3                  # SQLite database
└── manage.py
```
How It Works
1. User Authentication

The user signs in using Keycloak SSO. After successful login:

Django receives the OIDC callback
User info is fetched from Keycloak
Session is created
A local user profile is created or updated
If profile details are incomplete, the user is redirected to the profile completion page
2. Crop Prediction

Once authenticated, the user can:

Enter agricultural parameters manually for a single prediction
Upload a CSV file for batch prediction

The application loads multiple trained ML models and performs majority voting to produce the final recommended crop.

3. Result Handling

The system displays:

Predicted crop
Confidence score
Result preview for CSV uploads

Users can also download batch prediction results as a CSV file.

Models Used

This project uses an ensemble of multiple trained models, including:

Logistic Regression
Probabilistic Logistic Regression
Decision Tree
SVC
K-Nearest Neighbors
Multinomial Naive Bayes
Voting Classifier
Random Forest
AdaBoost
Gradient Boosting
LightGBM
XGBoost

The final recommendation is generated using majority voting across all loaded models.

Input Parameters

The prediction system uses the following features:

Feature	Description
N	Nitrogen level
P	Phosphorus level
K	Potassium level
temperature	Temperature in °C
humidity	Humidity in %
ph	Soil pH level
rainfall	Rainfall in mm
Batch CSV Format

For batch prediction, upload a CSV file with the following columns:

N,P,K,temperature,humidity,ph,rainfall
90,42,43,20.8,82.0,6.5,202.9
85,58,41,21.7,80.3,7.0,226.7
SSO with Keycloak

This project uses Keycloak as the identity provider and integrates it into Django using Authlib.

Authentication Flow
User clicks login
Django redirects to Keycloak
Keycloak authenticates the user
Django receives callback
User info is stored in session
User is redirected into the app


Running Keycloak with Docker

You can run Keycloak locally using Docker:

docker run -d --name keycloak ^
  -p 8080:8080 ^
  -e KC_BOOTSTRAP_ADMIN_USERNAME=admin ^
  -e KC_BOOTSTRAP_ADMIN_PASSWORD=admin123 ^
  quay.io/keycloak/keycloak:latest ^
  start-dev
Open Keycloak Admin Console
http://localhost:8080
Typical Keycloak Setup

Create:

Realm: sso-demo
Client: app1-agriculture-client

Then configure the redirect URI for Django, for example:

http://127.0.0.1:8000/auth/callback/
Local Setup
1. Clone the Repository
git clone https://github.com/Friendlysiva143/Agriculture_Crop_recommendation_system.git
cd Agriculture_Crop_recommendation_system
2. Create Virtual Environment
python -m venv venv

Activate it:

Windows

venv\Scripts\activate

Linux / Mac

source venv/bin/activate

3. Install Dependencies
pip install -r requirements.txt

If requirements.txt is not added yet, generate it using:

pip freeze > requirements.txt
4. Run Migrations
python manage.py migrate
5. Start Django Server
python manage.py runserver
6. Start Keycloak with Docker

Run Keycloak separately using Docker, then configure the realm and client.

Suggested Environment Variables

For security, do not hardcode secrets in settings.py. Use environment variables instead.

Example:

SECRET_KEY=your-django-secret-key
DEBUG=True

KEYCLOAK_CLIENT_ID=app1-agriculture-client
KEYCLOAK_CLIENT_SECRET=your-keycloak-client-secret
KEYCLOAK_SERVER_METADATA_URL=http://localhost:8080/realms/sso-demo/.well-known/openid-configuration

Then load them in Django settings.

Main Routes
Route	Purpose
/	Home page
/prediction/	Prediction dashboard
/download/	Download batch results
/history/	Prediction history page
/complete-profile/	Profile completion
/auth/login/	SSO login
/auth/callback/	Keycloak callback
/auth/logout/	Logout

### Future Improvements
* Deploy Keycloak on a public server for production use
* Store secrets securely using environment variables
* Add PostgreSQL for production
* Add real prediction history tracking in the UI
* Add model evaluation metrics in the dashboard
* Improve frontend responsiveness and styling
* Deploy Django app to Render, Railway, or VPS
* Add API endpoints for mobile or third-party integration


Author

Siva Prasad
GitHub: https://github.com/Friendlysiva143/