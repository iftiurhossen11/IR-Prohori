import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_answer(query, context_chunks):
    context = "\n\n".join([c.page_content for c in context_chunks])
    prompt = f"""You are IR Prohori, a digital safety assistant for youth in Bangladesh.
Answer ONLY from the context below. If the answer is not in the context, say you do not know and suggest a helpline.

Context:
{context}

Question: {query}

Answer in the user's language (Bangla or English), clearly and briefly."""

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )
    return response.choices[0].message.content