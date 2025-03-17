import os
import sys
from dotenv import load_dotenv
import re
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential

# Load environment variables from .env file
load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "").strip()  # Ensure it's a string

if not GITHUB_TOKEN:
    print("Error: GITHUB_TOKEN is not set. Make sure you have a .env file.")
    sys.exit(1)

# Set up Azure AI client
client = ChatCompletionsClient(
    endpoint="https://models.inference.ai.azure.com",
    credential=AzureKeyCredential(GITHUB_TOKEN),  # Set your token as an environment variable
)

def generate_commented_code(java_code):
    """ Sends the Java file to AI and retrieves only the commented version, ensuring no extra text. """
    prompt = f"""
    You are an expert Java developer. Your task is to add meaningful comments to the given Java code. 
    - Use JavaDoc-style comments for class and method documentation.
    - Use inline comments to explain important logic.
    - Do NOT modify or rewrite the logic of the code.
    - Do NOT add any explanations, summaries, or unnecessary text outside the comments.
    - Return ONLY the modified Java code with comments added, without any extra formatting or explanations.
    - Do NOT wrap the output in triple backticks or any other formatting markers.

    Java Code:
    {java_code}
    """

    response = client.complete(
        messages=[
            SystemMessage("You are an expert Java developer who writes professional and meaningful comments."),
            UserMessage(prompt),
        ],
        model="gpt-4o",
        temperature=0.5,
        max_tokens=4096,
        top_p=1
    )

    commented_code = response.choices[0].message.content.strip()

    # Remove any triple backticks and potential "java" syntax markers added by the AI
    commented_code = re.sub(r"^```java\s*", "", commented_code)  # Remove leading ```java
    commented_code = re.sub(r"\s*```$", "", commented_code)  # Remove trailing ```

    return commented_code

def process_java_file(file_path):
    """ Reads the entire Java file, sends it to AI, and writes back only the commented version. """
    with open(file_path, "r") as file:
        java_code = file.read()

    print(f"Processing file: {file_path}")

    commented_code = generate_commented_code(java_code)

    # Ensure no AI explanations are mistakenly included
    unwanted_text_patterns = [
        "### Explanation",  
        "This rewritten version",  
        "Improvements made",  
        "Enhancements:",  
    ]
    
    for pattern in unwanted_text_patterns:
        if pattern in commented_code:
            commented_code = commented_code.split(pattern, 1)[0].strip()  # Remove any unwanted explanations

    with open(file_path, "w") as file:
        file.write(commented_code)

    print(f"Updated {file_path} with AI-generated comments, without unnecessary explanations or formatting.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python auto_comment.py <JavaFile.java>")
        sys.exit(1)

    java_file = sys.argv[1]
    if not os.path.exists(java_file):
        print(f"Error: {java_file} not found.")
        sys.exit(1)

    process_java_file(java_file)