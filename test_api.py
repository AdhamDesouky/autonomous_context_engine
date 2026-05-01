import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# Load the .env file
load_dotenv()

def test_connection():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY not found in .env file.")
        return

    try:
        # Initialize a basic Gemini model
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
        
        # Send a test ping
        response = llm.invoke("Respond with the word 'Connected' if you receive this.")
        print(f"Status: {response.content}")
        
    except Exception as e:
        print(f"Connection Failed: {e}")

if __name__ == "__main__":
    test_connection()