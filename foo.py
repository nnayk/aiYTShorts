from google import genai

client = genai.Client()

response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents="Tell me about brahim diaz afcon controversy",
)

print(response.text)
