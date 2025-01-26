from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.classifier import TopicsClassifier

app = FastAPI(title="Topics Classification API")

class DomainRequest(BaseModel):
    domain: str

classifier = TopicsClassifier()

@app.get("/topics")
async def get_topics():
    """Get all available topics from the taxonomy."""
    try:
        topics = classifier.get_all_topics()
        return {"topics": topics}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/classify")
async def classify_domain(request: DomainRequest):
    try:
        topics = classifier.classify_domain(request.domain)
        return {"domain": request.domain, "topics": topics}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 