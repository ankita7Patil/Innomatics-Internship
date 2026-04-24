# LearnHub — Online Course Platform
### FastAPI Backend | Internship Final Project

A production-level FastAPI backend for an online course platform.
Built using in-memory data, Pydantic validation, helper functions,
CRUD operations, multi-step workflows, and advanced search/sort/pagination.

---

## Tech Stack

| Tool       | Purpose                       |
|------------|-------------------------------|
| FastAPI    | Web framework                 |
| Uvicorn    | ASGI server                   |
| Pydantic   | Request body validation       |
| Python 3.10+ | Runtime                    |

---

## Folder Structure

```
learnhub_project/
├── main.py           ← entire backend (single file)
├── requirements.txt  ← dependencies
└── README.md         ← this file
```

---

## Quick Start

```bash
# 1. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # Mac / Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the server
uvicorn main:app --reload

# 4. Open Swagger UI
http://127.0.0.1:8000/docs
```

---

## All Endpoints

### General
| Method | Route  | Description              |
|--------|--------|--------------------------|
| GET    | /      | Welcome + platform info  |

### Courses — Read
| Method | Route               | Description                          |
|--------|---------------------|--------------------------------------|
| GET    | /courses            | List all courses                     |
| GET    | /courses/summary    | Aggregate stats (Q5)                 |
| GET    | /courses/filter     | Filter by category/level/price/seats |
| GET    | /courses/search     | Multi-field keyword search (Q16)     |
| GET    | /courses/sort       | Sort by price/title/seats (Q17)      |
| GET    | /courses/page       | Paginate courses (Q18)               |
| GET    | /courses/browse     | Search + filter + sort + page (Q20)  |
| GET    | /courses/{id}       | Get single course by ID              |

### Courses — CRUD
| Method | Route          | Description                    |
|--------|----------------|--------------------------------|
| POST   | /courses       | Add new course — 201 (Q11)     |
| PUT    | /courses/{id}  | Update course partially (Q12)  |
| DELETE | /courses/{id}  | Delete course with guard (Q13) |

### Enrollments
| Method | Route                  | Description                       |
|--------|------------------------|-----------------------------------|
| GET    | /enrollments           | All enrollments + revenue (Q4)    |
| POST   | /enrollments           | Enroll with discounts (Q8/Q9)     |
| GET    | /enrollments/search    | Search by student name (Q19)      |
| GET    | /enrollments/sort      | Sort by fee or name (Q19)         |
| GET    | /enrollments/page      | Paginate enrollments (Q19)        |

### Wishlist Workflow
| Method | Route                       | Description                          |
|--------|-----------------------------|--------------------------------------|
| GET    | /wishlist                   | View full wishlist (Q14)             |
| POST   | /wishlist/add               | Add course to wishlist (Q14)         |
| DELETE | /wishlist/remove/{course_id}| Remove item from wishlist (Q15)      |
| POST   | /wishlist/enroll-all        | Enroll in all wishlist items (Q15)   |

---

## Key Features

### Discount Logic (calculate_enrollment_fee)
- Early-bird 10% off — when seats_left > 5
- Coupon STUDENT20 — extra 20% off (stacks after early-bird)
- Coupon FLAT500   — flat ₹500 deduction

### Validation Rules (Pydantic)
- student_name: min 2 characters
- email: min 5 characters
- course_id: must be > 0
- gift_enrollment = True requires recipient_name
- price: ge=0 (free courses allowed)
- seats_left: gt=0

### Business Rule Guards
- Cannot enroll in a fully booked course
- Cannot delete a course with enrolled students
- Cannot add duplicate student+course combo to wishlist

### Route Order Rule
All fixed routes (/courses/summary, /courses/filter, /courses/search,
/courses/sort, /courses/page, /courses/browse) are declared BEFORE
the variable route /courses/{course_id} — as required by FastAPI.

---

## Example API Responses

### GET /
```json
{
  "message": "Welcome to LearnHub Online Courses",
  "version": "1.0.0",
  "docs": "/docs",
  "total_courses": 7
}
```

### POST /enrollments (with coupon STUDENT20)
```json
{
  "message": "Enrollment confirmed!",
  "enrollment": {
    "enrollment_id": 1,
    "student_name": "Arjun Patel",
    "course_title": "React JS Complete Guide",
    "original_price": 1299,
    "discounts_applied": [
      "Early-bird 10% off → -₹130",
      "Coupon STUDENT20 20% off → -₹234"
    ],
    "total_savings": 364,
    "final_fee": 935,
    "status": "enrolled"
  }
}
```

### GET /courses/browse?keyword=python&sort_by=price&order=asc&page=1&limit=3
```json
{
  "applied": {
    "keyword": "python",
    "sort_by": "price",
    "order": "asc"
  },
  "page": 1,
  "total_matching": 1,
  "total_pages": 1,
  "courses": [
    {
      "id": 1,
      "title": "Python for Beginners",
      "price": 999,
      "seats_left": 10
    }
  ]
}
```

---

## Day-wise Concept Coverage

| Day | Concept                  | Where Used                              |
|-----|--------------------------|-----------------------------------------|
| 1   | GET + JSON responses     | /, /courses, /courses/{id}, /summary    |
| 2   | POST + Pydantic          | POST /enrollments, POST /courses        |
| 3   | Helpers + Filter         | find_course(), calculate_enrollment_fee(), filter_courses_logic() |
| 4   | CRUD + status codes      | POST/PUT/DELETE /courses                |
| 5   | Multi-step workflow      | /wishlist/add → /wishlist/enroll-all    |
| 6   | Search + Sort + Pagination | /search, /sort, /page, /browse        |

---

*Built for FastAPI Internship Final Project — Feb 2026 Batch*
