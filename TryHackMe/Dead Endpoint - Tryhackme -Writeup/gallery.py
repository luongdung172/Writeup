"""Meridian internal image library."""
from datetime import datetime, timezone
from functools import wraps
from pathlib import Path
import hashlib
import io
import json
import logging
import os
import secrets
import sqlite3
import subprocess
import threading
import uuid

from flask import Flask, Request, abort, jsonify, redirect, render_template, request, send_file, session, url_for
from PIL import Image

BASE = Path("/srv/gallery")
ORIGINALS = BASE / "media" / "originals"
EXPORTS = BASE / "exports"
DATABASE = BASE / "data" / "gallery.sqlite3"
ALLOWED = {
    "yard_0147.jpg", "yard_0148.jpg", "yard_0152.jpg",
}

class ImageRequest(Request):
    def _get_file_stream(self, total_content_length, content_type, filename=None, content_length=None):
        return io.BytesIO()

app = Flask(__name__)
app.request_class = ImageRequest
app.secret_key = os.environ["GALLERY_SESSION_KEY"]
app.config.update(MAX_CONTENT_LENGTH=10 * 1024 * 1024, SESSION_COOKIE_HTTPONLY=True,
                  SESSION_COOKIE_SAMESITE="Lax")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
LOG = logging.getLogger("gallery")

def utcnow():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")

def connect():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

def initialize():
    for directory in (ORIGINALS, EXPORTS, DATABASE.parent):
        directory.mkdir(parents=True, exist_ok=True)
    with connect() as db:
        db.executescript("""
          PRAGMA journal_mode=WAL;
          CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY, username TEXT UNIQUE NOT NULL,
            salt TEXT NOT NULL, password_hash TEXT NOT NULL, display_name TEXT NOT NULL);
          CREATE TABLE IF NOT EXISTS albums (
            id INTEGER PRIMARY KEY, title TEXT NOT NULL, description TEXT NOT NULL);
          CREATE TABLE IF NOT EXISTS photos (
            filename TEXT PRIMARY KEY, album_id INTEGER NOT NULL, caption TEXT NOT NULL,
            uploaded_by INTEGER NOT NULL, uploaded_at TEXT NOT NULL, bytes INTEGER NOT NULL);
          CREATE TABLE IF NOT EXISTS exports (
            id TEXT PRIMARY KEY, album_id INTEGER NOT NULL, requested_by INTEGER NOT NULL,
            requested_at TEXT NOT NULL, completed_at TEXT, state TEXT NOT NULL,
            selection TEXT NOT NULL, filename TEXT);
          CREATE TABLE IF NOT EXISTS activity (
            id INTEGER PRIMARY KEY, time TEXT NOT NULL, user_id INTEGER,
            action TEXT NOT NULL, detail TEXT NOT NULL);
        """)
        db.execute("INSERT OR IGNORE INTO albums VALUES (1, ?, ?)",
                   ("North yard inspection", "Loading bays, boundary access and delivery records."))

def add_user(username, password, display_name):
    salt = secrets.token_hex(16)
    digest = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt), n=16384, r=8, p=1).hex()
    with connect() as db:
        db.execute("INSERT OR IGNORE INTO users(username,salt,password_hash,display_name) VALUES(?,?,?,?)",
                   (username, salt, digest, display_name))

def authenticated(function):
    @wraps(function)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("login"))
        return function(*args, **kwargs)
    return wrapped

def event(action, detail):
    with connect() as db:
        db.execute("INSERT INTO activity(time,user_id,action,detail) VALUES(?,?,?,?)",
                   (utcnow(), session.get("user_id"), action, detail))

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        with connect() as db:
            user = db.execute("SELECT * FROM users WHERE username=?", (request.form.get("username", ""),)).fetchone()
        password = request.form.get("password", "")
        if user:
            digest = hashlib.scrypt(password.encode(), salt=bytes.fromhex(user["salt"]), n=16384, r=8, p=1).hex()
            if secrets.compare_digest(digest, user["password_hash"]):
                session.clear()
                session.update(user_id=user["id"], display_name=user["display_name"])
                event("sign_in", request.remote_addr or "")
                return redirect(url_for("index"))
        error = "The username or password was not recognized."
    return render_template("login.html", error=error)

@app.get("/")
@authenticated
def index():
    with connect() as db:
        photos = db.execute("SELECT * FROM photos ORDER BY uploaded_at").fetchall()
        exports = db.execute("SELECT * FROM exports ORDER BY requested_at DESC LIMIT 8").fetchall()
    return render_template("index.html", photos=photos, exports=exports)

@app.get("/media/<name>")
@authenticated
def media(name):
    if name not in ALLOWED:
        abort(404)
    path = ORIGINALS / name
    if not path.is_file():
        abort(404)
    return send_file(path, mimetype="image/jpeg", conditional=True, max_age=0)

@app.post("/api/photos")
@authenticated
def upload():
    file = request.files.get("photo")
    if not file or file.filename not in ALLOWED:
        abort(400)
    path = ORIGINALS / file.filename
    if path.exists() or path.with_name(path.name + ".locked").exists():
        abort(409)
    data = file.read()
    if len(data) > 8 * 1024 * 1024:
        abort(413)
    with Image.open(io.BytesIO(data)) as image:
        if image.format != "JPEG":
            abort(400)
        image.verify()
    with path.open("xb") as out:
        out.write(data)
        out.flush()
        os.fsync(out.fileno())
    with connect() as db:
        db.execute("INSERT INTO photos VALUES(?,?,?,?,?,?)", (file.filename, 1,
                   request.form.get("caption", "")[:200], session["user_id"], utcnow(), len(data)))
    event("photo_uploaded", file.filename)
    LOG.info("photo accepted name=%s bytes=%d", file.filename, len(data))
    return jsonify(filename=file.filename), 201

def export_job(job_id, selection):
    filename = job_id + ".tar"
    destination = EXPORTS / filename
    LOG.info("export started job=%s", job_id)
    # The legacy name selector is interpolated by this application's export worker.
    command = f"/bin/tar -cf '{destination}' -C '{ORIGINALS}' {selection}"
    try:
        process = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=45)
        if process.stdout:
            LOG.info("export worker job=%s %s", job_id, process.stdout.strip()[:500])
        if process.stderr:
            LOG.warning("export worker job=%s %s", job_id, process.stderr.strip()[:500])
        state = "ready" if process.returncode == 0 and destination.exists() else "failed"
    except subprocess.TimeoutExpired:
        state = "failed"
    with connect() as db:
        db.execute("UPDATE exports SET completed_at=?,state=?,filename=? WHERE id=?",
                   (utcnow(), state, filename if state == "ready" else None, job_id))
    LOG.info("export finished job=%s state=%s", job_id, state)

@app.post("/api/albums/<int:album_id>/export")
@authenticated
def export(album_id):
    if album_id != 1:
        abort(404)
    body = request.get_json(silent=True) or {}
    selection = body.get("selection", ".")
    if not isinstance(selection, str) or len(selection) > 1000:
        abort(400)
    job_id = uuid.uuid4().hex[:16]
    with connect() as db:
        db.execute("INSERT INTO exports VALUES(?,?,?,?,?,?,?,?)",
                   (job_id, album_id, session["user_id"], utcnow(), None, "queued", selection, None))
    event("export_requested", job_id)
    threading.Thread(target=export_job, args=(job_id, selection), daemon=True).start()
    return jsonify(id=job_id, state="queued"), 202

@app.get("/api/exports/<job_id>")
@authenticated
def export_status(job_id):
    with connect() as db:
        record = db.execute("SELECT id,state,completed_at FROM exports WHERE id=?", (job_id,)).fetchone()
    if not record:
        abort(404)
    return jsonify(dict(record))

@app.get("/exports/<job_id>")
@authenticated
def download(job_id):
    with connect() as db:
        record = db.execute("SELECT * FROM exports WHERE id=?", (job_id,)).fetchone()
    if not record or record["state"] != "ready":
        abort(404)
    return send_file(EXPORTS / record["filename"], as_attachment=True, download_name="north-yard.tar")

@app.get("/health")
def health():
    return jsonify(status="ok")

initialize()