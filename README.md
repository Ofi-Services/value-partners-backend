# OFI Services Process Mining API

This is a Django REST application that provides API endpoints to a front-end dashboard for process mining for the company OFI Services. The API is hosted at [https://ofiservices.pythonanywhere.com/api/](https://ofiservices.pythonanywhere.com/api/).

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Contact](#contact)

## Introduction

OFI Services Process Mining API allows you to interact with the company's process data through a RESTful interface. This API is designed to support the front-end dashboard, enabling users to visualize and analyze business processes.

## Features

- Retrieve process data

## Installation

To get started with the API, follow these steps:

1. Clone the repository:
    ```bash
    git clone https://github.com/Ofi-Services/zurick-backend.git
    cd ofi_dashboard_backend
    ```

2. Create and activate a virtual environment:
    ```bash
    python3 -m venv env
    source env/bin/activate
    ```

3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Apply database migrations:
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

5. Run the development server:
    ```bash
    python manage.py runserver
    ```

## Usage

Access the API at `http://127.0.0.1:8000/api/` (for local development) or [https://ofiservices.pythonanywhere.com/api/](https://ofiservices.pythonanywhere.com/api/).

Use a tool like Postman or cURL to interact with the API endpoints.

### API Endpoints

### API Endpoints
- [`GET /api/cases/`](https://ofiservices.pythonanywhere.com/api/cases/) - Retrieve a list of cases or create a new case.
- [`GET /api/activities/`](https://ofiservices.pythonanywhere.com/api/activities/) - Retrieve a list of activities or create a new activity.
- [`GET /api/activity-list/`](https://ofiservices.pythonanywhere.com/api/activity-list/) - Retrieve a list of activities with optional filtering and pagination.
    - Optional parameters:
        - `case` (list[str]): List of case IDs to filter activities.
        - `name` (list[str]): List of names to filter activities.
        - `case_index` (str): Case index to filter activities.
        - `page_size` (int): Number of activities per page (default: 100000).
        - `type` (str): Case type to filter activities.
        - `branch` (str): Case branch to filter activities.
        - `ramo` (str): Case ramo to filter activities.
        - `brocker` (str): Case brocker to filter activities.
        - `state` (str): Case state to filter activities.
        - `client` (str): Case client to filter activities.
        - `creator` (str): Case creator to filter activities.
        - `var` (list[str]): List of variant IDs to filter activities.
        - `start_date` (str): Start date (YYYY-MM-DD) to filter activities.
        - `end_date` (str): End date (YYYY-MM-DD) to filter activities.
    - Response: A paginated response containing the filtered list of activities or an error message in case of failure.
- [`GET /api/material/`](https://ofiservices.pythonanywhere.com/api/material/) - Retrieve a list of orderItems or create a new orderItem.
    - Optional parameters:
        - `material_code` (list[str]): List of material codes to filter orderItems.
        - `free_text` (str): `"true"` or `"false"` to filter by `is_free_text`.
    - Validation:
        - Any value other than `"true"` or `"false"` for `free_text` returns **400 Bad Request**.
    - Response: A paginated response containing the filtered list of orderItems or an error message in case of failure
- [`GET /api/meta-data/`](https://ofiservices.pythonanywhere.com/api/meta-data/) - Retrieve lists of all distinct activity names and case IDs.
- [`GET /api/variants/`](https://ofiservices.pythonanywhere.com/api/variants/) - Retrieve a list of variants with activities, cases, number of cases, and percentages.
    - Optional parameters:
        - `activities`: Filter variants by activities. You can specify multiple activities.
        - `cases`: Filter variants by case IDs. You can specify multiple case IDs.
- [`GET /api/bills/`](https://ofiservices.pythonanywhere.com/api/bills/) - Retrieve a list of bills.
- [`GET /api/reworks/`](https://ofiservices.pythonanywhere.com/api/reworks/) - Retrieve a list of reworks.
- [`GET /api/KPI/`](https://ofiservices.pythonanywhere.com/api/KPI/) - Retrieve a list of mean times in seconds for each activity.
    - Optional parameters:
        - `start_date` (str): Start date (YYYY-MM-DD) to filter activities.
        - `end_date` (str): End date (YYYY-MM-DD) to filter activities.
- [`GET /ai/alerts/`](https://ofiservices.pythonanywhere.com/ai/alerts/) - Retrieve a list of alerts or create a new alert.
- [`POST /ai/ai_assistant/`](https://ofiservices.pythonanywhere.com/ai/ai_assistant/) - Interact with the AI assistant for process mining insights.

#### Name Choices

The only choices for the `name` parameter are:
- `CREATE`
- `UPDATE`
- `RESOLUTION ADD`
- `SOLUTIONASSOCIATION`
- `RESOLUTION UPDATE`
- `RESOLVED`
- `DELETE`
- `RESTORE`
- `REQ_CONVER`
- `ADD_requesttask`
- `COMPLETED`
- `SLA_VIOLATION`
- `CLOSE`
- `COPY`
- `ADD_requestworklog`
- `FR_SLA_VIOLATION`
- `DELETE_requesttask`
- `ATT_ADD`
- `FCR`
- `ADD_requestResponse`
- `REPLY`
- `UPDATE_requestworklog`

#### Example

To filter activities by case IDs 3 and 10, and by names "CREATE" and "UPDATE":

https://ofiservices.pythonanywhere.com/api/activity-list/?case=3&case=10&name=CREATE&name=UPDATE

## Contact

Stefano Lacorazza  
s.lacorazza@ofiservices.com