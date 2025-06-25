import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import os
from typing import Dict, List, Optional
import logging
import re

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CourseScraper:
    def __init__(self):
        self.base_url = "https://catalog.upenn.edu/courses/cis/"
        self.data_dir = "data"
        self.courses_file = os.path.join(self.data_dir, "courses.json")
        self.metadata_file = os.path.join(self.data_dir, "metadata.json")
        
        # Create data directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)

    def clean_text(self, text: str) -> str:
        """Clean text by removing special characters and normalizing spaces."""
        # Replace non-breaking space with regular space
        text = text.replace('\u00a0', ' ')
        # Replace multiple spaces with a single space
        text = re.sub(r'\s+', ' ', text)
        # Remove leading/trailing spaces
        return text.strip()

    def fetch_catalog_page(self) -> Optional[str]:
        """Fetch the catalog page content."""
        try:
            response = requests.get(self.base_url)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"Error fetching catalog page: {e}")
            return None

    def parse_courses(self, html_content: str) -> List[Dict]:
        """Parse course information from HTML content."""
        soup = BeautifulSoup(html_content, 'html.parser')
        courses = []

        # Find all course entries
        course_entries = soup.find_all('div', class_='courseblock')
        
        for entry in course_entries:
            try:
                # Extract course code and title
                title_block = entry.find('p', class_='courseblocktitle')
                if not title_block:
                    continue

                # Extract course code and title from the strong tag
                strong_tag = title_block.find('strong')
                if not strong_tag:
                    continue

                code_title = self.clean_text(strong_tag.get_text())
                
                # Use regex to extract course code and title
                match = re.match(r'([A-Z]+\s+\d{4})\s+(.+)', code_title)
                if not match:
                    continue

                course_code = self.clean_text(match.group(1))
                title = self.clean_text(match.group(2))

                # Extract description and prerequisites from courseblockextra
                extra_blocks = entry.find_all('p', class_='courseblockextra')
                description = ""
                prerequisites = None
                terms = None
                units = None

                for block in extra_blocks:
                    text = self.clean_text(block.get_text(strip=True))
                    
                    # Skip empty blocks
                    if not text:
                        continue

                    # Check if this block contains prerequisites
                    if "Prerequisite" in text or "Prerequisites" in text:
                        prerequisites = text
                    # Check if this block contains terms
                    elif text in ["Fall", "Spring", "Summer", "Fall or Spring"]:
                        terms = text
                    # Check if this block contains course units
                    elif "Course Unit" in text:
                        units = text
                    # Otherwise, it's part of the description
                    else:
                        if description:
                            description += " "
                        description += text

                course_data = {
                    "course_code": course_code,
                    "title": title,
                    "description": description,
                    "prerequisites": prerequisites,
                    "terms": terms,
                    "units": units,
                    "last_updated": datetime.now().isoformat()
                }

                courses.append(course_data)
                logger.info(f"Parsed course: {course_code}")

            except Exception as e:
                logger.error(f"Error parsing course entry: {e}")
                continue

        return courses

    def save_courses(self, courses: List[Dict]):
        """Save courses to JSON file."""
        try:
            with open(self.courses_file, 'w', encoding='utf-8') as f:
                json.dump(courses, f, indent=2, ensure_ascii=False)
            
            # Save metadata
            metadata = {
                "last_updated": datetime.now().isoformat(),
                "total_courses": len(courses),
                "source_url": self.base_url
            }
            
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
                
            logger.info(f"Saved {len(courses)} courses to {self.courses_file}")
        except Exception as e:
            logger.error(f"Error saving courses: {e}")

    def load_existing_courses(self) -> List[Dict]:
        """Load existing courses from JSON file."""
        try:
            if os.path.exists(self.courses_file):
                with open(self.courses_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading existing courses: {e}")
        return []

    def run(self):
        """Main execution method."""
        logger.info("Starting course scraping process...")
        
        # Fetch and parse courses
        html_content = self.fetch_catalog_page()
        if not html_content:
            logger.error("Failed to fetch catalog page")
            return

        new_courses = self.parse_courses(html_content)
        if not new_courses:
            logger.error("No courses found")
            return

        # Save courses
        self.save_courses(new_courses)
        logger.info("Course scraping completed successfully")

if __name__ == "__main__":
    scraper = CourseScraper()
    scraper.run() 