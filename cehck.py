import google.generativeai as genai

genai.configure(api_key="AIzaSyDynwuPk0ryM3yTZQPzy5jpH2H6ILpUDno")  # Replace with your actual API key

for m in genai.list_models():
    print(m.name, m.supported_generation_methods)