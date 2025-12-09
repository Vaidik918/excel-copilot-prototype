import google.generativeai as genai

# Set API key
api_key = "AIzaSyD5BOeMyAVoFtWFtKBaZR2U9s1Qzuaw_Xw"  # Paste your key
genai.configure(api_key=api_key)

# Test connection
model = genai.GenerativeModel('gemini-2.5-flash')
response = model.generate_content("Say 'Gemini is working!'")
print("✅ SUCCESS:", response.text)
