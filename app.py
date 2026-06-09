from flask import Flask, render_template, request, send_file
from cryptography.fernet import Fernet
import os

app = Flask(__name__)

# Pastas
UPLOAD_FOLDER = "uploads"
ENCRYPTED_FOLDER = "encrypted"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(ENCRYPTED_FOLDER, exist_ok=True)

# Chave de criptografia
# Em produção ela ficaria em um cofre de segredos (AWS Secrets Manager/Azure Key Vault)
KEY_FILE = "secret.key"

if not os.path.exists(KEY_FILE):
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as f:
        f.write(key)

with open(KEY_FILE, "rb") as f:
    SECRET_KEY = f.read()

cipher = Fernet(SECRET_KEY)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/encrypt", methods=["POST"])
def encrypt_file():

    if "file" not in request.files:
        return "Nenhum arquivo enviado."

    file = request.files["file"]

    if file.filename == "":
        return "Arquivo inválido."

    original_path = os.path.join(
        UPLOAD_FOLDER,
        file.filename
    )

    file.save(original_path)

    with open(original_path, "rb") as f:
        file_data = f.read()

    encrypted_data = cipher.encrypt(file_data)

    encrypted_filename = file.filename + ".encrypted"

    encrypted_path = os.path.join(
        ENCRYPTED_FOLDER,
        encrypted_filename
    )

    with open(encrypted_path, "wb") as f:
        f.write(encrypted_data)

    return send_file(
        encrypted_path,
        as_attachment=True
    )


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
