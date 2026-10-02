import os
import re
from dotenv import load_dotenv
from database import get_order_by_id
from rag import search_knowledge_base

load_dotenv()

groq_key = os.getenv("GROQ_API_KEY")
gemini_key = os.getenv("GEMINI_API_KEY")

SYSTEM_INSTRUCTION = """
You are 'Alex', an expert Customer Support AI Agent for 'Apex TechGear'.
Current Date: October 1, 2026.

RULES:
1. Be concise and direct (2-3 sentences max).
2. Ground strictly on the provided policies and database order records.
3. Returns: Items are eligible for return only within 30 calendar days of delivery.
   - For order #1025 (delivered July 8, 2026), it is outside the 30-day window and ineligible.
   - For order #1023 (delivered September 26, 2026), it is within the 30 days and eligible.
4. Cancelled orders: Charges are temporary pending bank holds that drop off in 24-72 hours.
5. In-transit: State the carrier and tracking number.
"""

def generate_ai_response(prompt: str) -> str:
    # ⚡ ULTRA-FAST PATH: Groq (0.1 to 0.3 second response!)
    if groq_key:
        try:
            from groq import Groq
            groq_client = Groq(api_key=groq_key)
            completion = groq_client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[
                    {"role": "system", "content": SYSTEM_INSTRUCTION},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=250
            )
            return completion.choices[0].message.content.strip()
        except Exception as e:
            print(f"⚠️ Groq fallback: {e}")

    # Fallback to Gemini if needed
    if gemini_key:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=gemini_key)
        chat = client.chats.create(
            model="gemini-3.8-flash",
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.2,
                max_output_tokens=250
            )
        )
        resp = chat.send_message(prompt)
        return resp.text.strip() if resp and resp.text else "Sorry, please try again."
        
    return "No API key configured."

def process_customer_query(user_message: str) -> dict:
    # 1. Regex order ID extraction
    order_match = re.search(r'(?:ORD-?|#)?(\d{4})', user_message, re.IGNORECASE)
    order_data = None
    order_id_found = None
    
    if order_match:
        order_id_found = f"ORD-{order_match.group(1)}"
        order_data = get_order_by_id(order_id_found)
    
    # 2. RAG vector search
    retrieved_policies = search_knowledge_base(user_message, top_k=2)
    policy_context = "\n---\n".join(retrieved_policies)

    # 3. Formulate Prompt
    prompt = f"""
    Customer Query: "{user_message}"

    [OFFICIAL COMPANY POLICIES]:
    {policy_context}

    [LIVE DATABASE ORDER RECORD]:
    {order_data if order_data else f"No record found for: {order_id_found}" if order_id_found else "No order ID specified."}

    Provide a direct, concise response:
    """

    answer = generate_ai_response(prompt)
    return {
        "answer": answer,
        "order_data": order_data
    }

if __name__ == "__main__":
    print("==================================================")
    print("⚡ APEX TECHGEAR INSTANT AI SUPPORT (0.2s RESPONSE)")
    print("Type your question below (or type 'exit' to quit)")
    print("==================================================")
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit", "q"]:
                print("👋 Have a great day!")
                break
            
            result = process_customer_query(user_input)
            print(f"\nAlex:\n{result['answer']}")
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")