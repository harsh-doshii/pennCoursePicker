from fastapi import APIRouter, HTTPException
from typing import Optional
import requests
from bs4 import BeautifulSoup
import praw
import os
from dotenv import load_dotenv
from pydantic import BaseModel
import re

load_dotenv()

router = APIRouter()

# Initialize Reddit client
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            user_agent="PennCoursePicker/1.0"
)

class CourseInfo(BaseModel):
    course_code: str
    title: str
    description: str
    prerequisites: Optional[str] = None
    reddit_comments: Optional[list] = None

def extract_course_info(soup: BeautifulSoup, course_code: str) -> Optional[dict]:
    # Find all course blocks
    course_blocks = soup.find_all('div', class_='courseblock')
    
    for block in course_blocks:
        # Get the course title from the strong tag
        title_elem = block.find('strong')
        if not title_elem:
            continue
            
        title_text = title_elem.text.strip()
        print(f"Looking for course {course_code}")
        print(f"Found title: {title_text}")
        
        # Clean up the title text by replacing multiple spaces with a single space
        clean_title = ' '.join(title_text.split())
        print(f"Checking if {clean_title} starts with 'CIS {course_code}'")
        
        # Check if this is the course we're looking for
        if clean_title.startswith(f"CIS {course_code}"):
            print("Match found!")
            # Split the title into code and name
            parts = clean_title.split(course_code, 1)
            title = parts[1].strip()
            
            # Get all courseblockextra paragraphs
            extra_paras = block.find_all('p', class_='courseblockextra')
            
            # First paragraph is usually the description
            description = extra_paras[0].text.strip() if extra_paras else ""
            
            # Look for prerequisites in the description
            prerequisites = None
            prereq_match = re.search(r'Prerequisite:.*?(?=\.|$)', description, re.IGNORECASE)
            if prereq_match:
                prerequisites = prereq_match.group(0).strip()
            
            return {
                "course_code": course_code,
                "title": title,
                "description": description,
                "prerequisites": prerequisites
            }
    
    return None

@router.get("/{course_code}")
async def get_course_info(course_code: str):
    try:
        # Clean up course code - remove 'CIS' prefix if present and any spaces
        course_code = course_code.upper().replace('CIS', '').strip()
        
        # Fetch course information from UPenn catalog
        url = "https://catalog.upenn.edu/courses/cis/"
        response = requests.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract course information
        course_info = extract_course_info(soup, course_code)
        print("Hi")
        print(course_info)
        if not course_info:
            raise HTTPException(status_code=404, detail=f"Course {course_code} not found")
        
        # Fetch Reddit comments
        subreddit = reddit.subreddit("UPenn")
        search_query = f"{course_code} course"
        comments = []
        
        for submission in subreddit.search(search_query, limit=5):
            submission.comments.replace_more(limit=0)
            for comment in submission.comments.list():
                comments.append({
                    "author": str(comment.author),
                    "body": comment.body,
                    "score": comment.score,
                    "created_utc": comment.created_utc
                })
        print(comments)
        course_info["reddit_comments"] = comments
        
        return course_info
        
    except requests.RequestException as e:
        raise HTTPException(status_code=404, detail=f"Course catalog not accessible: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") 