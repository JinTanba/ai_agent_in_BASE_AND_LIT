from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio
from tools.get_image_tool import run as run_image_tool
from tools.handle_twitter import run as run_twitter
from typing import Optional

app = FastAPI()

class TwitterRequest(BaseModel):
    tweet_content: Optional[str] = ""

class ImageRequest(BaseModel):
    link: str

@app.post("/run-image-tool")
async def run_image(request: ImageRequest):
    try:
        result = await run_image_tool(request.link)
        return {"success": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/run-twitter")
async def run_twitter_tool(request: TwitterRequest):
    try:
        result = await run_twitter(tweet_content=request.tweet_content)
        return {"success": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8001)