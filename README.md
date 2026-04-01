# 🔐 Secure File Transfer System

A full-stack **secure file transfer web application** built with **Python (Flask)** that lets users:

- Register & log in
- Upload files that are **encrypted before being stored**
- Download their files (automatically **decrypted on download**)
- Securely **share files with other registered users** by username

> ✅ Live Demo:  
> https://secure-file-transfer-system-1.onrender.com/login

---

## ✨ Features

- 🔑 **User Authentication**
  - Register, login, logout using Flask-Login
  - Passwords are stored as **secure hashes**, not plain text

- 🧾 **Encrypted File Storage**
  - Files are encrypted using **Fernet (symmetric encryption)** from `cryptography`
  - Each file gets its **own random key**
  - File key is encrypted with a **master key** before being stored in the database

- 📤 **Secure Upload & Download**
  - On **upload**:
    - File is read as bytes
    - Encrypted using a per-file key
    - Ciphertext is stored on disk (e.g. `instance/uploads/*.enc`)
  - On **download**:
    - Encrypted bytes are read from disk
    - Decrypted server-side
    - Sent back to the user as the original file

- 🤝 **File Sharing**
  - Owner can share a file with another user using their username
  - Only:
    - the **owner**, or  
    - a **user it’s shared with**  
    can download the file

- 🎨 **Modern UI / UX**
  - Dark, **security-themed** design
  - **Poppins** font from Google Fonts
  - Smooth hover effects & transitions
  - Responsive layout for desktop & mobile



---

## 🏗 Tech Stack

**Backend**

- Python 3.x
- Flask
- Flask-Login
- Flask-SQLAlchemy
- cryptography (Fernet)
- SQLite (via SQLAlchemy)

**Frontend**

- HTML + Jinja2 templates
- CSS (custom, dark security theme)
- Google Font: Poppins

**Deployment**

- Render (Web Service)
- `gunicorn` / Flask (depending on setup)

---

## 📂 Project Structure

```text
Secure_File_Transfer_System/
│
├─ app.py               # Flask app, routes, auth, upload/download logic
├─ config.py            # Config (DB URI, upload folder, keys)
├─ models.py            # SQLAlchemy models (User, File, SharedFile, etc.)
├─ requirements.txt     # Python dependencies
├─ data.db              # SQLite database (created at runtime)
│
├─ instance/
│   └─ uploads/         # Encrypted file storage (.enc files)
│
├─ utils/
│   ├─ __init__.py
│   └─ crypto_utils.py  # Encryption / decryption helpers
│
├─ templates/
│   ├─ index.html       # Landing page
│   ├─ login.html       # Login page
│   ├─ register.html    # Registration page
│   └─ dashboard.html   # Dashboard (upload, list, share, download)
│
└─ static/
    └─ css/
        └─ style.css    # Modern dark UI with transitions
