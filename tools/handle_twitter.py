import asyncio
import os
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from browser_use import Agent,Browser,Controller, ActionResult
from langchain.output_parsers import StructuredOutputParser,ResponseSchema
from langchain_core.output_parsers import JsonOutputParser
from langchain.prompts import PromptTemplate
from browser_use.browser.browser import BrowserConfig
from browser_use.browser.context import BrowserContext
from pathlib import Path
from tools.utils import extract_links
import json
load_dotenv()
claude = ChatAnthropic(model="claude-3-5-sonnet-20241022")
openai = ChatOpenAI(model="gpt-4o") 
llm = openai
twitter_id = os.getenv("TWITTER_ID")
twitter_pass = os.getenv("TWITTER_PASS")


create_login_task = lambda id, password: f"""
Navigate to Twitter and login to using below credentials.

Here are the specific steps:

1. Navigate to https://x.com/i/flow/login.
2. input below user_id in the input field.
    - user_id: {id}
3. input below password in the input field.
    - password: {password}
3. and click on login button.

Important:
- If a page appears that asks you to confirm whether you are a bot such as "recapture", please reload the page and try the task again.
- Your job is to log in to Twitter using the password and username you are given.
"""

create_tweet_task = lambda content: f"""
Your task is create a tweet in twitter page.

Here are the specific steps:
1. See the text input field at the top of the page that says "What's happening?"
2. Input below text in the text input field.
    - text: {content}
"""

check_mention_task = lambda: f"""
Your task is to check the mention to me and store tweet link.

Here are the specific steps:
1. Go to the https://x.com/notifications/mentions
2. collect 10~5 latest mention tweet link to me.
"""

async def run(tweet_content: str="", retry_count: int = 0):
    """
    Run the agent to login to twitter and post/read tweet
    if tweet_content is empty, then it will read the mention to me
    """
    if retry_count >= 3:
        print("Maximum retry attempts reached")
        return False

    browser = Browser()
    res = False
    async with await browser.new_context() as context:

        agent = Agent(
            task=create_login_task(twitter_id, twitter_pass),
            llm=llm,
            browser_context=context,
        )
        history = await agent.run()
        result = history.final_result()
        if not result:
            res = False


        async def post():
            # Create tweet after successful login
            post_agent = Agent(
                task=create_tweet_task(tweet_content),
                llm=llm,
                browser_context=context,
            )
            
            tweet_history = await post_agent.run()
            if tweet_history.is_done():
                print("Tweet posted successfully")
                return True
            else:
                return False
            
        
        async def get_mention_to_me():
            # Check mention to me
            mention_agent = Agent(
                task=check_mention_task(),
                llm=llm,
                browser_context=context
            )
            mention_history = await mention_agent.run()
            if mention_history.is_done():
                print("Mention checked successfully")
                extracted = mention_history.extracted_content()
                print(extracted)
                linksjson = extract_links(json.dumps(extracted))
                print(linksjson)
                
                return True
            else:
                return False

        if result:
            if tweet_content:
                res = await post()
            else:
                res = await get_mention_to_me()
        
    print('=============', res)
    await browser.close()

    return res
    
    



if __name__ == '__main__':
    source_code = Path(__file__).read_text(encoding='utf-8')
    asyncio.run(run(tweet_content=""))

