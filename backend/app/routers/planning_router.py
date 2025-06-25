from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

router = APIRouter()

# Initialize OpenAI client with OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

class CourseQuery(BaseModel):
    query: str
    course_info: dict
    reddit_comments: Optional[List[dict]] = None

class CourseInsight(BaseModel):
    summary: str
    prerequisites_analysis: str
    difficulty_assessment: str
    recommendations: List[str]

@router.post("/analyze", response_model=CourseInsight)
async def analyze_course(query: CourseQuery):
    try:
        # Prepare context for the LLM
        context = f"""
        Course Information:
        - Code: {query.course_info['course_code']}
        - Title: {query.course_info['title']}
        - Description: {query.course_info['description']}
        - Prerequisites: {query.course_info.get('prerequisites', 'None specified')}
        
        Student Comments:
        {format_reddit_comments(query.reddit_comments) if query.reddit_comments else 'No student comments available'}
        
        Query: {query.query}
        """

        # Generate insights using OpenRouter with Llama
        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout:free",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful course advisor. Analyze the course information and student comments to provide insights about the course."
                },
                {
                    "role": "user",
                    "content": f"""Please analyze this course information and provide insights about:
1. A summary of what students need to know
2. Analysis of prerequisites
3. Assessment of difficulty
4. Specific recommendations

Context:
{context}"""
                }
            ],
            temperature=0.7,
            max_tokens=1000
        )

        # Parse the response into structured format
        insight_text = response.choices[0].message.content
        
        # Split the response into sections
        sections = insight_text.split('\n\n')
        
        return CourseInsight(
            summary=sections[0] if len(sections) > 0 else "No summary available",
            prerequisites_analysis=sections[1] if len(sections) > 1 else "No prerequisites analysis available",
            difficulty_assessment=sections[2] if len(sections) > 2 else "No difficulty assessment available",
            recommendations=sections[3].split('\n') if len(sections) > 3 else ["No specific recommendations available"]
        )

    except Exception as e:
        print("error")
        print(e)
        raise HTTPException(status_code=500, detail=f"Error generating insights: {str(e)}")

def format_reddit_comments(comments: List[dict]) -> str:
    if not comments:
        return "No comments available"
    
    formatted = []
    for comment in comments:
        formatted.append(f"Comment by {comment['author']} (Score: {comment['score']}):\n{comment['body']}\n")
    
    return "\n".join(formatted) 