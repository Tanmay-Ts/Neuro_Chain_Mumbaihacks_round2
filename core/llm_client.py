import openai
import json
import config

# Initialize client using cleaned config values
client = openai.OpenAI(
    api_key=config.OPENAI_API_KEY,
    organization=config.OPENAI_ORG_ID,
    project=config.OPENAI_PROJECT_ID,
    base_url="https://api.openai.com/v1" 
)

def call_chat(messages, model="gpt-3.5-turbo", temperature=0.0):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature
        )
        return response.choices[0].message.content.strip()

    except openai.AuthenticationError as e:
        print(f"!!! AUTH ERROR: {e}") 
        return f"AUTH_ERROR: {str(e)}"
        
    except Exception as e:
        print(f"!!! GENERAL ERROR: {e}")
        return f"Error calling LLM: {str(e)}"

def parse_json_response(response_text):
    if not response_text:
        return None
        
    clean_text = response_text.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(clean_text)
    except json.JSONDecodeError:
        return None