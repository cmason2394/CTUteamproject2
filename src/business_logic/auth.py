from flask import Flask, request, session, redirect, url_for, render_template_string

app = Flask(__name__)
app.secret_key = "yoursecretkey" # change this in production!

# Demo user store (replace with database later)
users = {
"admin": "password123",
"teacher": "teach2025"
}

# Login page
@app.route("/login", methods=["GET", "POST"])
def login():
if request.method == "POST":
username = request.form["username"]
password = request.form["password"]

if username in users and users[username] == password:
session["user"] = username
return redirect(url_for("dashboard"))
return "Invalid credentials. Try again."

return render_template_string("""
<form method="post">
<input type="text" name="username" placeholder="Username" required><br>
<input type="password" name="password" placeholder="Password" required><br>
<button type="submit">Login</button>
</form>
""")

# Protected dashboard
@app.route("/dashboard")
def dashboard():
if "user" not in session:
return redirect(url_for("login"))
return f"Welcome, {session['user']}! This is the School Management System."

# Logout
@app.route("/logout")
def logout():
session.pop("user", None)
return redirect(url_for("login"))

if __name__ == "__main__":
app.run(debug=True)
