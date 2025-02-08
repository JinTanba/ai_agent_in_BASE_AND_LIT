from langchain_anthropic import ChatAnthropic
from langchain.prompts import PromptTemplate
import json
claude = ChatAnthropic(model="claude-3-5-sonnet-20241022")
example_text = """
{
  "links": [
    "https://example.com/page1",
    "https://anothersite.org/article",
    "https://www.somewebsite.net/post/12345"
  ]
}
"""
format_text = """
{
  "links": [
    "URL1",
    "URL2",
    ...
  ]
}
"""
prompt = PromptTemplate(template="""
Your task is to extract all links from the following text:

<input_text>
{input_text}
</input_text>

Please follow these instructions carefully:

1. Analyze the provided text and identify all URLs present.
2. Extract each unique URL you find.
3. Create a JSON object with a single key "links" whose value is an array of the extracted URLs.
4. Ensure that each URL is a complete and valid link.
5. If no links are found, return an empty array.
6. Do not include any explanations or additional text in your output.

Output your result in the following JSON format:

<format>
{format_text}
</format>

Replace "URL1", "URL2", etc., with the actual links you've extracted from the input text. If there are no links, the "links" array should be empty.

Here's an example of how your output should look if links are found:
{example_text}


Remember to include only the JSON object in your response, without any additional text or explanations.
""", input_variables=["input_text"], partial_variables={"example_text": example_text, "format_text": format_text})

output_chain = prompt | claude

def extract_links(text: str):
    print("------------->", text)
    res = output_chain.invoke({"input_text":text})
    print(res.content)
    res = res.content
    if isinstance(res, list):
        res = res[0]
    else:
        res = res
    res = json.loads(res)
    print(res)
    print("<-------------", res)
    return (res)
