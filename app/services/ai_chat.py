import openai
from app.config import settings
 
client=openai.OpenAI(api_key=settings.client.api_key,
                     base_url="https://api.anthropic.com/v1/" ) 

def generate_answer(question, context):
    response = client.chat.completions.create(
        model="claude-3-7-sonnet-20250219",
        messages=[
            {"role": "system", "content": "Answer only using the provided context. If the answer is not in the context, say 'I don't know.' Do not add extra information."},
            {"role": "user", "content": f"Context: {context}\n\nQuestion: {question}"}
        ]
    )
    return response.choices[0].message.content 


