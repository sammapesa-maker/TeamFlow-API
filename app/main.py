from fastapi import FastAPI
from app.api.v1.router import v1_router

app = FastAPI(
    title="TeamFlow API",
    version="1.0.0"
)

# Root/Health check endpoint
@app.get(path="/health", tags=["Health"])
def root():
    return {"status": "healthy"}

# Global prefix for all v1 routes
app.include_router(v1_router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app="main:app", host="127.0.0.1", port=8000)