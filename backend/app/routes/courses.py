from fastapi import APIRouter, HTTPException
from typing import Dict, Optional
import json
import os
from datetime import datetime, timedelta

router = APIRouter()

# Constants
DATA_DIR = "data"
COURSES_FILE = os.path.join(DATA_DIR, "courses.json")
METADATA_FILE = os.path.join(DATA_DIR, "metadata.json")
UPDATE_INTERVAL = timedelta(days=1)  # Update data daily

def load_courses() -> Dict:
    """Load courses from JSON file."""
    try:
        with open(COURSES_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Course data not found. Please run the scraper first.")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid course data format.")

def check_data_freshness() -> bool:
    """Check if the data needs to be updated."""
    try:
        with open(METADATA_FILE, 'r') as f:
            metadata = json.load(f)
            last_updated = datetime.fromisoformat(metadata['last_updated'])
            return datetime.now() - last_updated < UPDATE_INTERVAL
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        return False

@router.get("/courses/{course_code}")
async def get_course(course_code: str) -> Dict:
    """
    Get course information by course code.
    """
    # Normalize course code
    course_code = course_code.upper().replace(" ", "")
    
    # Load courses
    courses = load_courses()
    
    # Find the course
    course = next(
        (c for c in courses if c["course_code"].replace(" ", "") == course_code),
        None
    )
    
    if not course:
        raise HTTPException(
            status_code=404,
            detail=f"Course {course_code} not found"
        )
    
    # Add data freshness information
    course["data_freshness"] = {
        "last_updated": datetime.fromisoformat(course["last_updated"]).isoformat(),
        "needs_update": not check_data_freshness()
    }
    
    return course

@router.get("/courses")
async def list_courses() -> Dict:
    """
    List all available courses.
    """
    courses = load_courses()
    
    return {
        "courses": courses,
        "total": len(courses),
        "last_updated": datetime.fromisoformat(courses[0]["last_updated"]).isoformat() if courses else None,
        "needs_update": not check_data_freshness()
    } 