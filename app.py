from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
import os
import uuid
import pypdf
from docx import Document
import google.generativeai as genai

app = Flask(__name__)
app.config.from_object('config.Config')
app.secret_key = app.config.get('SECRET_KEY', 'supersecretkey')

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def extract_text_from_file(file_path, filename):
    ext = filename.rsplit('.', 1)[1].lower()
    if ext == 'pdf':
        reader = pypdf.PdfReader(file_path)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text
    elif ext in ['doc', 'docx']:
        try:
            doc = Document(file_path)
            return "\n".join([para.text for para in doc.paragraphs])
        except Exception as e:
            print(f"Error extracting DOCX: {e}")
            return ""
    elif ext == 'txt':
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

def process_document_with_ai(file_path, filename, user_query=None):
    document_content = extract_text_from_file(file_path, filename)
    if not document_content:
        return None, "Could not extract text from the document. Please check the file format or content."
    genai.configure(api_key=app.config['GOOGLE_API_KEY'])
    model = genai.GenerativeModel(app.config['AI_MODEL_NAME'])
    if user_query:
        prompt = (
            "You are a helpful legal assistant. Based only on the following document, "
            "answer the user's question clearly and concisely. If the information is not present, "
            "state 'I cannot find that information in the provided document.'\n\n"
            f"--- Document ---\n{document_content}\n\n"
            f"--- User Question ---\n{user_query}\n\n"
            "--- AI Answer ---"
        )
    else:
        prompt = (
            "You are a helpful legal assistant. Summarize the key points and important clauses "
            "of the following legal document. Use clear, simple language and avoid jargon. "
            "Present the summary as bullet points or numbered lists for readability. "
            "Highlight potential areas of concern or common pitfalls if they are evident.\n\n"
            f"--- Document ---\n{document_content}\n\n"
            "--- Summary ---"
        )
    try:
        response = model.generate_content(prompt)
        return response.text, None
    except Exception as e:
        print(f"AI error: {e}")
        return None, f"Sorry, there was an error processing your request: {e}"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'document' not in request.files:
            return render_template('index.html', error="No file part in the request.")
        file = request.files['document']
        if file.filename == '':
            return render_template('index.html', error="No file selected.")
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(filepath)
            session['current_document_path'] = filepath
            session['document_original_name'] = filename
            summary, error = process_document_with_ai(filepath, filename)
            session['last_summary'] = summary
            return render_template('result.html', summary=summary, filename=filename, error=error)
        else:
            return render_template('index.html', error="Unsupported file type.")
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_query = request.form.get('user_query')
    document_path = session.get('current_document_path')
    filename = session.get('document_original_name', 'your document')
    last_summary = session.get('last_summary', '')
    if not document_path or not os.path.exists(document_path):
        error = "No document uploaded or document not found. Please upload a document first."
        return render_template('result.html', error=error, summary=None, filename=None)
    chat_response, error = process_document_with_ai(document_path, filename, user_query)
    return render_template(
        'result.html',
        chat_response=chat_response,
        summary=last_summary,
        filename=filename,
        user_query=user_query,
        error=error
    )

@app.route('/chat_page', methods=['GET', 'POST'])
def chat_page():
    chat_response = None
    error = None
    if request.method == 'POST':
        user_query = request.form.get('user_query')
        document_path = session.get('current_document_path')
        filename = session.get('document_original_name', 'your document')
        if not document_path or not os.path.exists(document_path):
            error = "No document uploaded or document not found. Please upload a document first."
        else:
            chat_response, error = process_document_with_ai(document_path, filename, user_query)
    return render_template('chat.html', chat_response=chat_response, error=error)

if __name__ == '__main__':
    app.run(debug=True)