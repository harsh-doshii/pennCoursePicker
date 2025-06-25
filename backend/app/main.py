from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import course_router, planning_router

app = FastAPI(
    title="PennCoursePicker API",
    description="API for course planning and insights",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(course_router.router, prefix="/api/courses", tags=["courses"])
app.include_router(planning_router.router, prefix="/api/planning", tags=["planning"])

@app.get("/")
async def root():
    return {"message": "Welcome to PennCoursePicker API"} 