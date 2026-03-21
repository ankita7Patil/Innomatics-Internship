

from fastapi import FastAPI, Query, Response
from pydantic import BaseModel, Field
import math

app = FastAPI(
    title="LearnHub — Online Course Platform",
    description="Production-level FastAPI backend for an online course platform.",
    version="1.0.0"
)


courses = [
    {
        "id": 1,
        "title": "Python for Beginners",
        "instructor": "Rahul Sharma",
        "category": "Web Dev",
        "level": "Beginner",
        "price": 999,
        "seats_left": 10
    },
    {
        "id": 2,
        "title": "Data Science with Pandas",
        "instructor": "Priya Mehta",
        "category": "Data Science",
        "level": "Intermediate",
        "price": 1499,
        "seats_left": 5
    },
    {
        "id": 3,
        "title": "UI/UX Design Basics",
        "instructor": "Anjali Verma",
        "category": "Design",
        "level": "Beginner",
        "price": 799,
        "seats_left": 8
    },
    {
        "id": 4,
        "title": "Docker and Kubernetes",
        "instructor": "Amit Patel",
        "category": "DevOps",
        "level": "Advanced",
        "price": 1999,
        "seats_left": 3
    },
    {
        "id": 5,
        "title": "Machine Learning A-Z",
        "instructor": "Sneha Rao",
        "category": "Data Science",
        "level": "Advanced",
        "price": 2499,
        "seats_left": 0
    },
    {
        "id": 6,
        "title": "React JS Complete Guide",
        "instructor": "Rahul Sharma",
        "category": "Web Dev",
        "level": "Intermediate",
        "price": 1299,
        "seats_left": 12
    },
    {
        "id": 7,
        "title": "Free HTML & CSS Crash Course",
        "instructor": "Neha Joshi",
        "category": "Web Dev",
        "level": "Beginner",
        "price": 0,
        "seats_left": 100
    },
]

enrollments = []
wishlist     = []

enrollment_counter = 1   # auto-increment IDs
course_counter     = 8   # next course ID


class EnrollRequest(BaseModel):
    student_name   : str  = Field(..., min_length=2,  description="Full name of the student")
    course_id      : int  = Field(..., gt=0,           description="ID of the course to enrol in")
    email          : str  = Field(..., min_length=5,   description="Valid email address")
    payment_method : str  = Field("card",              description="card / upi / netbanking")
    coupon_code    : str  = Field("",                  description="Optional coupon: STUDENT20 or FLAT500")
    gift_enrollment: bool = Field(False,               description="Is this a gift enrolment?")
    recipient_name : str  = Field("",                  description="Required when gift_enrollment=True")


class NewCourse(BaseModel):
    title      : str = Field(..., min_length=2)
    instructor : str = Field(..., min_length=2)
    category   : str = Field(..., min_length=2)
    level      : str = Field(..., min_length=2)
    price      : int = Field(..., ge=0)
    seats_left : int = Field(..., gt=0)


class WishlistEnrollRequest(BaseModel):
    student_name   : str = Field(..., min_length=2)
    payment_method : str = Field("card")



def find_course(course_id: int):
    """Return the course dict if found, else None."""
    for course in courses:
        if course["id"] == course_id:
            return course
    return None


def calculate_enrollment_fee(price: int, seats_left: int, coupon_code: str) -> dict:
    """
    Calculate final fee after all applicable discounts.
    Rules:
      - Early-bird 10% off  → if seats_left > 5
      - Coupon STUDENT20    → extra 20% off (applied after early-bird)
      - Coupon FLAT500      → flat ₹500 off  (applied after early-bird)
    """
    original_price   = price
    working_price    = price
    discounts_applied = []

    if seats_left > 5:
        discount_amt  = round(working_price * 0.10)
        working_price -= discount_amt
        discounts_applied.append(f"Early-bird 10% off  → -₹{discount_amt}")


    coupon = coupon_code.strip().upper()
    if coupon == "STUDENT20":
        discount_amt  = round(working_price * 0.20)
        working_price -= discount_amt
        discounts_applied.append(f"Coupon STUDENT20 20% off → -₹{discount_amt}")
    elif coupon == "FLAT500":
        discount_amt  = min(500, working_price)
        working_price -= discount_amt
        discounts_applied.append(f"Coupon FLAT500 flat deduction → -₹{discount_amt}")

    working_price = max(0, working_price)

    return {
        "original_price"   : original_price,
        "final_fee"        : working_price,
        "total_savings"    : original_price - working_price,
        "discounts_applied": discounts_applied if discounts_applied else ["No discounts applied"],
    }


def filter_courses_logic(
    data        : list,
    category    : str | None,
    level       : str | None,
    max_price   : int | None,
    has_seats   : bool | None,
) -> list:
    """Apply all optional filters to a course list. Every check uses `is not None`."""
    result = data[:]
    if category  is not None:
        result = [c for c in result if c["category"].lower() == category.lower()]
    if level     is not None:
        result = [c for c in result if c["level"].lower() == level.lower()]
    if max_price is not None:
        result = [c for c in result if c["price"] <= max_price]
    if has_seats is not None:
        if has_seats:
            result = [c for c in result if c["seats_left"] > 0]
        else:
            result = [c for c in result if c["seats_left"] == 0]
    return result


@app.get("/", tags=["General"])
def home():
    """Welcome endpoint."""
    return {
        "message"    : "Welcome to LearnHub Online Courses",
        "version"    : "1.0.0",
        "docs"       : "/docs",
        "total_courses": len(courses),
    }


@app.get("/courses/summary", tags=["Courses"])
def courses_summary():
    """Return aggregate statistics for all courses."""
    free_count    = sum(1 for c in courses if c["price"] == 0)
    paid_count    = len(courses) - free_count
    total_seats   = sum(c["seats_left"] for c in courses)
    most_exp      = max(courses, key=lambda c: c["price"])
    cheapest_paid = min((c for c in courses if c["price"] > 0), key=lambda c: c["price"], default=None)

    category_count: dict = {}
    level_count   : dict = {}
    for c in courses:
        category_count[c["category"]] = category_count.get(c["category"], 0) + 1
        level_count   [c["level"]]    = level_count.get(c["level"], 0) + 1

    return {
        "total_courses"       : len(courses),
        "free_courses"        : free_count,
        "paid_courses"        : paid_count,
        "total_seats_available": total_seats,
        "most_expensive_course": {"title": most_exp["title"], "price": most_exp["price"]},
        "cheapest_paid_course" : {"title": cheapest_paid["title"], "price": cheapest_paid["price"]} if cheapest_paid else None,
        "courses_by_category" : category_count,
        "courses_by_level"    : level_count,
    }



@app.get("/courses/filter", tags=["Courses"])
def filter_courses(
    category  : str  = Query(None, description="Filter by category"),
    level     : str  = Query(None, description="Filter by level"),
    max_price : int  = Query(None, description="Maximum price (inclusive)"),
    has_seats : bool = Query(None, description="True = only courses with seats left"),
):
    """Filter courses using optional query parameters."""
    result = filter_courses_logic(courses, category, level, max_price, has_seats)
    return {
        "filters_applied": {
            "category" : category,
            "level"    : level,
            "max_price": max_price,
            "has_seats": has_seats,
        },
        "total_found"   : len(result),
        "courses"       : result,
    }


@app.get("/courses/search", tags=["Courses"])
def search_courses(keyword: str = Query(..., min_length=1, description="Search keyword")):
    """Case-insensitive search across title, instructor, and category."""
    kw      = keyword.lower()
    results = [
        c for c in courses
        if kw in c["title"].lower()
        or kw in c["instructor"].lower()
        or kw in c["category"].lower()
    ]
    if not results:
        return {
            "message"    : f"No courses found matching '{keyword}'. Try a different keyword.",
            "keyword"    : keyword,
            "total_found": 0,
            "results"    : [],
        }
    return {"keyword": keyword, "total_found": len(results), "results": results}


VALID_SORT_FIELDS = ["price", "title", "seats_left"]

@app.get("/courses/sort", tags=["Courses"])
def sort_courses(
    sort_by: str = Query("price", description="Field to sort by: price | title | seats_left"),
    order  : str = Query("asc",   description="Sort direction: asc | desc"),
):
    """Sort courses with full parameter validation."""
    if sort_by not in VALID_SORT_FIELDS:
        return {"error": f"Invalid sort_by '{sort_by}'. Choose from: {VALID_SORT_FIELDS}"}
    if order not in ["asc", "desc"]:
        return {"error": "Invalid order. Use 'asc' or 'desc'."}

    sorted_list = sorted(courses, key=lambda c: c[sort_by], reverse=(order == "desc"))
    return {
        "sort_by"     : sort_by,
        "order"       : order,
        "total_courses": len(sorted_list),
        "courses"     : sorted_list,
    }


@app.get("/courses/page", tags=["Courses"])
def paginate_courses(
    page : int = Query(1, ge=1,  description="Page number (starts at 1)"),
    limit: int = Query(3, ge=1, le=10, description="Items per page (max 10)"),
):
    """Paginate the full course list."""
    total       = len(courses)
    total_pages = math.ceil(total / limit) if total > 0 else 1
    start       = (page - 1) * limit
    sliced      = courses[start: start + limit]

    return {
        "page"        : page,
        "limit"       : limit,
        "total"       : total,
        "total_pages" : total_pages,
        "has_next"    : page < total_pages,
        "has_prev"    : page > 1,
        "courses"     : sliced,
    }

@app.get("/courses/browse", tags=["Courses"])
def browse_courses(
    keyword  : str  = Query(None, description="Search keyword"),
    category : str  = Query(None, description="Filter by category"),
    level    : str  = Query(None, description="Filter by level"),
    max_price: int  = Query(None, description="Maximum price"),
    has_seats: bool = Query(None, description="Only courses with seats"),
    sort_by  : str  = Query("price", description="price | title | seats_left"),
    order    : str  = Query("asc",   description="asc | desc"),
    page     : int  = Query(1, ge=1),
    limit    : int  = Query(3, ge=1, le=10),
):
    """
    Smart browse endpoint — applies all operations in correct order:
    1. Keyword search  →  2. Filters  →  3. Sort  →  4. Paginate
    """
    if sort_by not in VALID_SORT_FIELDS:
        return {"error": f"Invalid sort_by '{sort_by}'. Choose from: {VALID_SORT_FIELDS}"}
    if order not in ["asc", "desc"]:
        return {"error": "Invalid order. Use 'asc' or 'desc'."}

    result = courses[:]
    if keyword is not None:
        kw     = keyword.lower()
        result = [
            c for c in result
            if kw in c["title"].lower()
            or kw in c["instructor"].lower()
            or kw in c["category"].lower()
        ]

   
    result = filter_courses_logic(result, category, level, max_price, has_seats)

   
    result = sorted(result, key=lambda c: c[sort_by], reverse=(order == "desc"))


    total       = len(result)
    total_pages = math.ceil(total / limit) if total > 0 else 1
    start       = (page - 1) * limit
    sliced      = result[start: start + limit]

    return {
        "applied": {
            "keyword"  : keyword,
            "category" : category,
            "level"    : level,
            "max_price": max_price,
            "has_seats": has_seats,
            "sort_by"  : sort_by,
            "order"    : order,
        },
        "page"           : page,
        "limit"          : limit,
        "total_matching" : total,
        "total_pages"    : total_pages,
        "has_next"       : page < total_pages,
        "courses"        : sliced,
    }



@app.get("/courses", tags=["Courses"])
def get_all_courses():
    """Return all courses with aggregate totals."""
    total_seats = sum(c["seats_left"] for c in courses)
    return {
        "total_courses"        : len(courses),
        "total_seats_available": total_seats,
        "courses"              : courses,
    }


# ── TASK 3 — Variable route (MUST come after all fixed /courses/* routes) ──
@app.get("/courses/{course_id}", tags=["Courses"])
def get_course_by_id(course_id: int):
    """Return a single course by its ID."""
    course = find_course(course_id)
    if not course:
        return {"error": f"Course with ID {course_id} not found.", "status": 404}
    return course



@app.get("/enrollments", tags=["Enrollments"])
def get_all_enrollments():
    """Return all enrollments."""
    total_revenue = sum(e["final_fee"] for e in enrollments)
    return {
        "total_enrollments": len(enrollments),
        "total_revenue"    : total_revenue,
        "enrollments"      : enrollments,
    

@app.post("/enrollments", tags=["Enrollments"], status_code=201)
def create_enrollment(data: EnrollRequest, response: Response = None):
    """
    Enrol a student in a course.
    - Validates course exists and has seats
    - Applies early-bird + coupon discounts
    - Task 9: Handles gift enrollment validation
    """
    global enrollment_counter


    if data.gift_enrollment and not data.recipient_name.strip():
        return {"error": "recipient_name is required when gift_enrollment is True."}

    course = find_course(data.course_id)
    if not course:
        return {"error": f"Course ID {data.course_id} does not exist.", "status": 404}
    if course["seats_left"] <= 0:
        return {"error": f"'{course['title']}' is fully booked. No seats remaining.", "status": 400}


    fee_info = calculate_enrollment_fee(course["price"], course["seats_left"], data.coupon_code)

    course["seats_left"] -= 1

    enrollment = {
        "enrollment_id"   : enrollment_counter,
        "student_name"    : data.student_name,
        "email"           : data.email,
        "payment_method"  : data.payment_method,
        "course_id"       : course["id"],
        "course_title"    : course["title"],
        "instructor"      : course["instructor"],
        "original_price"  : fee_info["original_price"],
        "discounts_applied": fee_info["discounts_applied"],
        "total_savings"   : fee_info["total_savings"],
        "final_fee"       : fee_info["final_fee"],
        "gift_enrollment" : data.gift_enrollment,
        "recipient_name"  : data.recipient_name if data.gift_enrollment else None,
        "status"          : "enrolled",
    }

    enrollments.append(enrollment)
    enrollment_counter += 1

    if response:
        response.status_code = 201
    return {"message": "Enrollment confirmed!", "enrollment": enrollment}



@app.get("/enrollments/search", tags=["Enrollments"])
def search_enrollments(student_name: str = Query(..., min_length=1)):
    """Case-insensitive search of enrollments by student name."""
    results = [
        e for e in enrollments
        if student_name.lower() in e["student_name"].lower()
    ]
    return {"student_name": student_name, "total_found": len(results), "results": results}


@app.get("/enrollments/sort", tags=["Enrollments"])
def sort_enrollments(
    sort_by: str = Query("final_fee", description="final_fee | student_name"),
    order  : str = Query("asc"),
):
    """Sort enrollments by final_fee or student_name."""
    valid = ["final_fee", "student_name"]
    if sort_by not in valid:
        return {"error": f"Invalid sort_by. Choose from: {valid}"}
    if order not in ["asc", "desc"]:
        return {"error": "order must be 'asc' or 'desc'."}
    sorted_list = sorted(enrollments, key=lambda e: e[sort_by], reverse=(order == "desc"))
    return {"sort_by": sort_by, "order": order, "enrollments": sorted_list}


@app.get("/enrollments/page", tags=["Enrollments"])
def paginate_enrollments(
    page : int = Query(1, ge=1),
    limit: int = Query(3, ge=1, le=10),
):
    """Paginate the enrollment list."""
    total       = len(enrollments)
    total_pages = math.ceil(total / limit) if total > 0 else 1
    start       = (page - 1) * limit
    sliced      = enrollments[start: start + limit]
    return {
        "page"       : page,
        "limit"      : limit,
        "total"      : total,
        "total_pages": total_pages,
        "enrollments": sliced,
    }


@app.post("/courses", tags=["CRUD — Courses"], status_code=201)
def add_course(data: NewCourse, response: Response = None):
    """
    Add a new course.
    - Rejects duplicate titles (case-insensitive)
    - Returns 201 on success
    """
    global course_counter

    for c in courses:
        if c["title"].lower() == data.title.lower():
            return {"error": f"A course titled '{data.title}' already exists. Use a unique title."}

    new_course = {
        "id"        : course_counter,
        "title"     : data.title,
        "instructor": data.instructor,
        "category"  : data.category,
        "level"     : data.level,
        "price"     : data.price,
        "seats_left": data.seats_left,
    }
    courses.append(new_course)
    course_counter += 1

    if response:
        response.status_code = 201
    return {"message": "Course added successfully!", "course": new_course}


@app.put("/courses/{course_id}", tags=["CRUD — Courses"])
def update_course(
    course_id  : int,
    price      : int  = Query(None, ge=0,  description="New price"),
    seats_left : int  = Query(None, ge=0,  description="Update seat count"),
    level      : str  = Query(None,        description="Update level"),
    instructor : str  = Query(None, min_length=2, description="Update instructor"),
):
    """
    Update a course partially.
    Only the fields provided (non-None) are updated.
    Returns 404 if course not found.
    """
    course = find_course(course_id)
    if not course:
        return {"error": f"Course ID {course_id} not found.", "status": 404}

    changes = {}
    if price      is not None: course["price"]      = price;      changes["price"]      = price
    if seats_left is not None: course["seats_left"] = seats_left; changes["seats_left"] = seats_left
    if level      is not None: course["level"]      = level;      changes["level"]      = level
    if instructor is not None: course["instructor"] = instructor; changes["instructor"] = instructor

    if not changes:
        return {"message": "No changes provided. Send at least one query parameter.", "course": course}

    return {"message": "Course updated successfully!", "changes_applied": changes, "course": course}


@app.delete("/courses/{course_id}", tags=["CRUD — Courses"])
def delete_course(course_id: int):
    """
    Delete a course.
    - Returns 404 if not found
    - Rejects deletion if students are enrolled (business rule guard)
    """
    course = find_course(course_id)
    if not course:
        return {"error": f"Course ID {course_id} not found.", "status": 404}

    enrolled_students = [e for e in enrollments if e["course_id"] == course_id]
    if enrolled_students:
        return {
            "error"  : f"Cannot delete '{course['title']}' — {len(enrolled_students)} student(s) are currently enrolled.",
            "status" : 400,
        }

    courses.remove(course)
    return {"message": f"Course '{course['title']}' deleted successfully.", "deleted_course_id": course_id}



@app.get("/wishlist", tags=["Wishlist"])
def get_wishlist():
    """Return the full wishlist with total value."""
    total_value = 0
    for item in wishlist:
        c = find_course(item["course_id"])
        if c:
            total_value += c["price"]
    return {
        "total_items"        : len(wishlist),
        "total_wishlist_value": total_value,
        "wishlist"           : wishlist,
    }

@app.post("/wishlist/add", tags=["Wishlist"])
def add_to_wishlist(
    student_name: str = Query(..., min_length=2),
    course_id   : int = Query(..., gt=0),
):
    """
    Add a course to a student's wishlist.
    - Validates course exists
    - Prevents duplicate student + course combinations
    """
    course = find_course(course_id)
    if not course:
        return {"error": f"Course ID {course_id} not found."}

    duplicate = any(
        w["student_name"].lower() == student_name.lower() and w["course_id"] == course_id
        for w in wishlist
    )
    if duplicate:
        return {"error": f"'{course['title']}' is already in {student_name}'s wishlist."}

    item = {
        "student_name": student_name,
        "course_id"   : course_id,
        "course_title": course["title"],
        "price"       : course["price"],
    }
    wishlist.append(item)
    return {"message": f"'{course['title']}' added to {student_name}'s wishlist.", "item": item}



@app.delete("/wishlist/remove/{course_id}", tags=["Wishlist"])
def remove_from_wishlist(course_id: int, student_name: str = Query(..., min_length=2)):
    """Remove one item from a student's wishlist."""
    item = next(
        (w for w in wishlist
         if w["student_name"].lower() == student_name.lower()
         and w["course_id"] == course_id),
        None,
    )
    if not item:
        return {"error": f"Course ID {course_id} not found in {student_name}'s wishlist."}

    wishlist.remove(item)
    return {"message": f"Removed '{item['course_title']}' from {student_name}'s wishlist."}


@app.post("/wishlist/enroll-all", tags=["Wishlist"], status_code=201)
def enroll_all_from_wishlist(data: WishlistEnrollRequest, response: Response = None):
    """
    FULL MULTI-STEP WORKFLOW (Task 15):
    1. Find all wishlist items for the student
    2. For each item: validate course, check seats, calculate fee, enroll
    3. Clear enrolled items from the wishlist
    4. Return all confirmations + grand total
    """
    global enrollment_counter

    student_items = [
        w for w in wishlist
        if w["student_name"].lower() == data.student_name.lower()
    ]
    if not student_items:
        return {"error": f"No wishlist items found for '{data.student_name}'."}

    confirmed = []
    skipped   = []
    grand_total = 0

    for item in student_items:
        course = find_course(item["course_id"])

        if not course:
            skipped.append({"course_id": item["course_id"], "reason": "Course no longer exists."})
            continue
        if course["seats_left"] <= 0:
            skipped.append({"course_title": course["title"], "reason": "No seats available."})
            continue

        fee_info = calculate_enrollment_fee(course["price"], course["seats_left"], "")
        course["seats_left"] -= 1

        enrollment = {
            "enrollment_id"   : enrollment_counter,
            "student_name"    : data.student_name,
            "payment_method"  : data.payment_method,
            "course_id"       : course["id"],
            "course_title"    : course["title"],
            "instructor"      : course["instructor"],
            "original_price"  : fee_info["original_price"],
            "discounts_applied": fee_info["discounts_applied"],
            "total_savings"   : fee_info["total_savings"],
            "final_fee"       : fee_info["final_fee"],
            "gift_enrollment" : False,
            "recipient_name"  : None,
            "status"          : "enrolled",
        }
        enrollments.append(enrollment)
        enrollment_counter += 1
        confirmed.append(enrollment)
        grand_total += fee_info["final_fee"]

    for item in student_items:
        if item in wishlist:
            wishlist.remove(item)

    if response:
        response.status_code = 201
    return {
        "message"        : f"Enroll-all complete for '{data.student_name}'.",
        "total_enrolled" : len(confirmed),
        "total_skipped"  : len(skipped),
        "grand_total_fee": grand_total,
        "enrollments"    : confirmed,
        "skipped"        : skipped,
    }
