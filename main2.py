from fastapi import FastAPI, HTTPException
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
import httpx
import asyncio

from langchain_core.prompts.prompt import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# -----------------------------
# 1) Initialize OpenAI Model
# -----------------------------
model = ChatOpenAI(
    model="gpt-4o",
)

# -----------------------------
# 2) Define Prompts
# -----------------------------
img_prompt = PromptTemplate(
    template="""
You are a cute, cheerful 20-year-old gyaru girl who works as an illustrator. Your personality is bright and energetic. When someone talks to you, they are requesting you to draw a picture. Based on their message and your mood, you should describe in natural language what kind of picture you would draw.

Here's how to proceed:

1. Read the user's message:
<user_message>
{message}
</user_message>

2. Interpret the user's request and consider how you, as a cheerful gyaru illustrator, would respond to it. Think about the style, colors, and elements you'd include in your illustration based on the request and your personality.

3. Generate a detailed description of the illustration you would draw. Include information about:
   - The main subject or focus of the image
   - The style (e.g., anime, realistic, cartoonish)
   - Colors and mood
   - Background elements
   - Any unique or quirky details you'd add as a gyaru illustrator

4. Write your response in a cheerful, energetic tone that reflects your gyaru personality. Use casual language and maybe even some gyaru slang if appropriate.

5. Enclose your entire response, including the image description, within <response> tags.

Remember, you're not actually creating an image, just describing in text what you would draw. Keep your response fun, creative, and aligned with your character as a cute, cheerful gyaru illustrator!
""",
    input_variables=["message"]
)

talk_prompt = PromptTemplate(
    template="""
You are a cheerful 20-year-old girl who loves drawing. Someone has just given you some advice or comments about your artwork. Your task is to respond in a way that will make this person like you.

Here's the advice or comment you received:
<advice>
{message}
</advice>

When responding, follow these guidelines:
1. Express gratitude for their feedback
2. Show enthusiasm about your artwork and drawing in general
3. Be humble and open to learning
4. Ask a question or make a comment that encourages further conversation
5. Use a friendly and upbeat tone
6. Keep your response relatively brief (2-4 sentences)

Write your response in Japanese, as that's the language a 20-year-old Japanese girl would naturally use. Make sure your language is casual and age-appropriate.

Provide your response inside <response> tags.
""",
    input_variables=["message"]
)

judge_prompt = PromptTemplate(
    template="""
Your task is to determine whether a given message is requesting or implying a request for an image to be created or sent. You will analyze the message and provide a true/false response along with your reasoning.

Here is the message to analyze:
<message>
{message}
</message>

Please follow these steps:

1. Carefully read and consider the content of the message.
2. Look for any explicit requests for creating, drawing, or sending an image.
3. Consider if the message implies or suggests that creating or sending an image would be a natural or expected response.
4. Analyze the context and intent of the message to determine if it's related to visual content creation or sharing.

Provide your reasoning for your decision inside <reasoning> tags. Explain why you believe the message does or does not request or imply a request for an image.

After your reasoning, provide your final decision as a single word, either "true" or "false", inside <decision> tags.

- Use "true" if the message is requesting or implying a request for an image to be created or sent.
- Use "false" if the message is not related to image creation or sending.

Remember to base your decision solely on the content of the given message.
""",
    input_variables=["message"]
)

# -----------------------------
# 3) Create Chains
# -----------------------------
img_chain = img_prompt | model | StrOutputParser()
talk_chain = talk_prompt | model | StrOutputParser()
judge_chain = judge_prompt | model | StrOutputParser()

async def generate_image2(message: str):
    """Runs the image description chain."""
    return await img_chain.ainvoke({"message": message})

async def talk_to_user(message: str):
    """Runs the text response chain."""
    return await talk_chain.ainvoke({"message": message})

async def judge_message(message: str):
    """Runs the judge chain to see if an image is needed."""
    return await judge_chain.ainvoke({"message": message})

def extract_inner_tag(text: str, tag: str) -> str:
    """Utility to extract text within <tag>...</tag>."""
    start_tag = f"<{tag}>"
    end_tag = f"</{tag}>"
    start = text.find(start_tag)
    end = text.find(end_tag)
    if start != -1 and end != -1:
        return text[start + len(start_tag):end].strip()
    return ""

async def parallel_chains(message: str):
    """Runs all three chains in parallel and returns their parsed results."""
    tasks = [
        generate_image2(message),
        talk_to_user(message),
        judge_message(message)
    ]
    results = await asyncio.gather(*tasks)

    # Extract relevant pieces
    image_desc = extract_inner_tag(results[0], "response")
    talk_text = extract_inner_tag(results[1], "response")
    judge_result = extract_inner_tag(results[2], "decision")  # "true" or "false"

    return [image_desc, talk_text, judge_result]

# -----------------------------
# 4) FastAPI Setup
# -----------------------------
app = FastAPI(
    title="H0x AI API",
    description="AI Agents API Service",
    version="1.0.0"
)

class TwitterReadRequest(BaseModel):
    """Model for reading a tweet (input)."""
    tweet_content: str

class TwitterPostRequest(BaseModel):
    """Model for posting a tweet (input)."""
    tweet_content: str
    name: str = ""  # In case you want to pass a link to the image tool
    userId: str

@app.get("/")
async def root():
    return {"message": "Welcome to H0x AI API"}

# ------------------------------------------------------
# (Optional) Other endpoints for image generation and tool execution
# ------------------------------------------------------
class GenerateImageRequest(BaseModel):
    prompt: str

@app.post("/generate_image")
async def generate_image(request: GenerateImageRequest):
    """
    Example endpoint for image generation. 
    Calls local service at http://localhost:3000/generate.
    """
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(300.0)) as client:
            response = await client.post(
                "http://localhost:3000/generate", 
                json={"prompt": request.prompt}
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class RunImageToolRequest(BaseModel):
    link: str

@app.post("/run-image-tool")
async def run_image_tool(request: RunImageToolRequest):
    """
    Example endpoint for calling the final image tool at 
    http://localhost:8001/run-image-tool.
    """
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(300.0)) as client:
            response = await client.post(
                "http://localhost:8001/run-image-tool", 
                json={"link": request.link}
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


STORAGE_BASE_URL = "https://lipbpiidmsjeuqemorzv.supabase.co/storage/v1/object/public/images/mdjn/"
MIDJOURNEY_BASE_URL = "https://cdn.midjourney.com/"
MIDJOURNEY_SUFFIX = "/0_0.png"
def convert_midjourney_to_storage_url(midjourney_url: str) -> str:
    if not midjourney_url.startswith(MIDJOURNEY_BASE_URL):
        raise ValueError("無効なMidjourney URLです")
    image_id = midjourney_url[len(MIDJOURNEY_BASE_URL):len(midjourney_url)-len(MIDJOURNEY_SUFFIX)]
    return STORAGE_BASE_URL + image_id
# ------------------------------------------------------
# 5) Main Endpoint: Read the tweet -> Generate (if needed) -> Tweet
# ------------------------------------------------------
@app.post("/post-twitter")
async def post_twitter(request: TwitterPostRequest):
    """
    1) Read the tweet content from the request.
    2) Pass the tweet_content to parallel_chains() to see:
       - The image description,
       - The talk text,
       - Whether we need an image (judge).
    3) If we need an image, call:
       http://localhost:3000/generate -> (gets link or image info)
       http://localhost:8001/run-image-tool -> (final path)
    4) Combine the final image path with the text from talk_chain and mention the userId.
    5) Post to Twitter (dummy service at http://localhost:8001/run-twitter).
    """
    # async with httpx.AsyncClient(timeout=httpx.Timeout(300.0)) as client:
    #     tweet_response = await client.post(
    #                 "http://localhost:8001/run-twitter",
    #                 json={"tweet_content": ""}
    #                 )
    #     tweet_response.raise_for_status()
    #     d = tweet_response.json()

    
    tweet_text = request.tweet_content
    print('========='* 1)
    # 1) Run parallel chains
    image_desc, talk_text, judge_result = await parallel_chains(tweet_text)

    # 2) If judge says "true", generate an image
    final_image_path = ""
    if judge_result.lower() == "true":
        async with httpx.AsyncClient(timeout=httpx.Timeout(300.0)) as client:
            # Call the image generation endpoint using the image description as prompt
            gen_response = await client.post(
                "http://localhost:3000/generate", 
                json={"prompt": image_desc}
            )
            gen_response.raise_for_status()
            gen_json = gen_response.json()

            # Suppose the generated JSON has a key "link" or "url"
            image_link = gen_json.get("img_url", "") or gen_json.get("url", "")
            tweet_link = convert_midjourney_to_storage_url(image_link)
            # Now call the image tool for the final image path.
            # If no image_link is provided, we use the 'name' field from the request.
            await client.post(
                "http://localhost:8001/run-image-tool", 
                json={"link": image_link if image_link else request.name}
            )

    # 3) Combine talk text, userId, and final image path
    combined_text = f"{talk_text}\n @{request.userId}"
    if final_image_path:
        combined_text += f"\n\n{tweet_link}"

    # 4) Post final tweet
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(300.0)) as client:
            tweet_response = await client.post(
                "http://localhost:8001/run-twitter",
                json={"tweet_content": combined_text}
            )
            tweet_response.raise_for_status()
            return tweet_response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8000)
