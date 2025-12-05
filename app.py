import os
from io import BytesIO

from flask import (
    Flask, render_template, request, redirect,
    url_for, send_file, flash
)
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import (
    LoginManager, login_user, login_required,
    current_user, logout_user
)

from config import Config
from models import db, User, File, SharedFile
from utils.crypto_utils import encrypt_file_bytes, decrypt_file_bytes


# -------------------- APP SETUP --------------------

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

# make sure uploads folder exists
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

login_manager = LoginManager(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# -------------------- ROUTES --------------------


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        email = request.form["email"].strip()
        pw = request.form["password"]

        if User.query.filter_by(username=username).first():
            flash("Username already exists")
            return redirect(url_for("register"))

        if User.query.filter_by(email=email).first():
            flash("Email already registered")
            return redirect(url_for("register"))

        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(pw),
        )
        db.session.add(user)
        db.session.commit()
        flash("Registered successfully. Please login.")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        pw = request.form["password"]

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, pw):
            login_user(user)
            return redirect(url_for("dashboard"))

        flash("Invalid username or password")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out")
    return redirect(url_for("index"))


@app.route("/dashboard")
@login_required
def dashboard():
    # files owned by current user
    my_files = File.query.filter_by(owner_id=current_user.id).all()

    # files shared with current user
    shared_links = SharedFile.query.filter_by(recipient_id=current_user.id).all()
    shared_items = []
    for s in shared_links:
        f = File.query.get(s.file_id)
        sender = User.query.get(s.sender_id)
        if f and sender:
            shared_items.append(
                {
                    "file": f,
                    "sender": sender.username,
                }
            )

    return render_template("dashboard.html", files=my_files, shared=shared_items)


@app.route("/upload", methods=["POST"])
@login_required
def upload():
    file_obj = request.files.get("file")
    if not file_obj or file_obj.filename == "":
        flash("No file selected")
        return redirect(url_for("dashboard"))

    raw_data = file_obj.read()

    ciphertext, encrypted_key = encrypt_file_bytes(raw_data)

    orig_name = secure_filename(file_obj.filename)
    random_prefix = os.urandom(12).hex()
    storage_name = f"{random_prefix}_{orig_name}.enc"
    storage_path = os.path.join(app.config["UPLOAD_FOLDER"], storage_name)

    with open(storage_path, "wb") as fh:
        fh.write(ciphertext)

    rec = File(
        owner_id=current_user.id,
        filename_orig=orig_name,
        storage_path=storage_path,
        encrypted_key=encrypted_key,
        filesize=len(raw_data),
    )
    db.session.add(rec)
    db.session.commit()
    flash("File encrypted & uploaded successfully")
    return redirect(url_for("dashboard"))


@app.route("/download/<int:file_id>")
@login_required
def download(file_id):
    file_rec = File.query.get_or_404(file_id)

    # Access control: owner or shared recipient only
    if file_rec.owner_id != current_user.id:
        shared = SharedFile.query.filter_by(
            file_id=file_id, recipient_id=current_user.id
        ).first()
        if not shared:
            flash("You do not have access to this file")
            return redirect(url_for("dashboard"))

    with open(file_rec.storage_path, "rb") as fh:
        ciphertext = fh.read()

    plaintext = decrypt_file_bytes(ciphertext, file_rec.encrypted_key)

    bio = BytesIO(plaintext)
    bio.seek(0)
    return send_file(bio, as_attachment=True, download_name=file_rec.filename_orig)


@app.route("/share/<int:file_id>", methods=["POST"])
@login_required
def share(file_id):
    file_rec = File.query.get_or_404(file_id)

    if file_rec.owner_id != current_user.id:
        flash("Only the owner can share this file")
        return redirect(url_for("dashboard"))

    recipient_username = request.form.get("recipient", "").strip()
    if not recipient_username:
        flash("Recipient username is required")
        return redirect(url_for("dashboard"))

    recipient = User.query.filter_by(username=recipient_username).first()
    if not recipient:
        flash("Recipient user not found")
        return redirect(url_for("dashboard"))

    existing = SharedFile.query.filter_by(
        file_id=file_id, recipient_id=recipient.id
    ).first()
    if existing:
        flash(f"Already shared with {recipient_username}")
        return redirect(url_for("dashboard"))

    link = SharedFile(
        file_id=file_id,
        sender_id=current_user.id,
        recipient_id=recipient.id,
    )
    db.session.add(link)
    db.session.commit()
    flash(f"File securely shared with {recipient_username}")
    return redirect(url_for("dashboard"))


# -------------------- MAIN --------------------

if __name__ == "__main__":
    from models import db

    # ensure tables exist
    with app.app_context():
        db.create_all()

    # Render provides PORT env var
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)

