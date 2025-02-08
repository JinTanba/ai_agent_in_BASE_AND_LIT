import asyncio

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from tools.codes import code1, code2
from browser_use import Agent,Browser,Controller, ActionResult
from browser_use.browser.browser import BrowserConfig
from browser_use.browser.context import BrowserContext
load_dotenv()
controller = Controller()
browser = Browser(config=BrowserConfig(headless=True))
llm = ChatOpenAI(model="gpt-4o")

@controller.registry.action('Execute js code')
async def execute_script(js_code: str, browser: BrowserContext):
	print(f"✅Executing script: {js_code[:100]}")
	await browser.execute_javascript(js_code)


async def run(link: str):
    task1 = f"""
    Your task is to go to below link and execute two specific js code
    link: {link}
    tasks:
        1. execute below js code
        	\n\n{code1}\n\n
        2.execute below js code
	        \n\n{code2}\n\n
		3. Teach me what message is displayed in the console after executing the code.
    """
    agent = Agent(
        browser=browser,
        task=task1,
        controller=controller,
        llm=llm,
    )
    # Run the agent
    history = await agent.run()
    await browser.close()
    res = False
    if history.final_result():
        print(f"Final result: {history.final_result()}")
        res = True
    else:
        print("No final result found.")
        res = False
    return res


if __name__ == '__main__':
    asyncio.run(run("https://cdn.midjourney.com/1773acc6-b2a7-40e7-b67c-6ab6fc506505/0_0.png"))
