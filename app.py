from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Mock data storage
users = {}  # {username: password}
posts = []  # [{"id": 1, "title": "Post Title", "content": "Post Content", "tags": ["tag1"], "likes": 0, "shares": 0, "comments": [], "username": "user1"}]
tags = []   # ["tag1", "tag2", ...]

# Routes

@app.route("/")
def get_started():
    # The Get Started page is shown first
    return render_template("get_started.html")  # Points to the updated get_started.html
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        # Check if passwords match
        if password != confirm_password:
            flash("Passwords do not match!", "danger")
            return redirect(url_for("signup"))

        # Check if username already exists
        if username in users:
            flash("Username already exists!", "danger")
        else:
            users[username] = password
            flash("Signup successful! Please log in.", "success")
            return redirect(url_for("login"))  # Redirect to login after successful signup
    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username in users and users[username] == password:
            session["user"] = username  # Store username in session for future reference
            flash("Login successful!", "success")
            return redirect(url_for("home"))
        else:
            flash("Invalid username or password!", "danger")
    return render_template("login.html")  # Create a login.html page

@app.route("/home")
def home():
    if "user" not in session:
        flash("You need to log in first.", "danger")
        return redirect(url_for("login"))
    return render_template("home.html")  
@app.route("/create_post", methods=["GET", "POST"])
def create_post():
    if "user" not in session:
        flash("You need to log in to create a post.", "danger")
        return redirect(url_for("login"))

    current_user = session["user"]
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        selected_tags = request.form.getlist("tags")
        post_id = len(posts) + 1
        posts.append({
            "id": post_id,
            "title": title,
            "content": content,
            "tags": selected_tags,
            "likes": 0,
            "shares": 0,
            "comments": [],
            "username": current_user
        })
        flash("Post created successfully!", "success")
        return redirect(url_for("view_posts"))
    return render_template("create_post.html", tags=tags)

@app.route("/view_posts", methods=["GET", "POST"])
def view_posts():
    
    # Get the selected tag from the URL query parameters
    selected_tag = request.args.get("tag", "")
    
    # Filter posts based on the selected tag
    if selected_tag:
        filtered_posts = [post for post in posts if selected_tag in post["tags"]]
    else:
        filtered_posts = posts
    
    # Get all tags to display in the filter dropdown
    all_tags = set(tag for post in posts for tag in post["tags"])
    
    return render_template("view_posts.html", posts=filtered_posts, all_tags=all_tags, selected_tag=selected_tag)
    

@app.route("/like_post/<int:post_id>")
def like_post(post_id):
    for post in posts:
        if post["id"] == post_id:
            post["likes"] += 1
            flash(f"Post '{post['title']}' liked!", "success")
            break
    return redirect(url_for("view_posts"))

@app.route("/share_post/<int:post_id>")
def share_post(post_id):
    for post in posts:
        if post["id"] == post_id:
            post["shares"] += 1
            flash(f"Post '{post['title']}' shared successfully!", "success")
            break
    return redirect(url_for("view_posts"))

@app.route("/comment_post/<int:post_id>", methods=["POST"])
def comment_post(post_id):
    comment = request.form["comment"]
    for post in posts:
        if post["id"] == post_id:
            post["comments"].append(comment)
            flash("Comment added successfully!", "success")
            break
    return redirect(url_for("view_posts"))
@app.route('/manage_tags', methods=['GET', 'POST'])
def manage_tags():
    search_query = request.args.get('search', '').lower()
    filtered_tags = [tag for tag in tags if search_query in tag.lower()]
    return render_template('manage_tags.html', tags=filtered_tags)

@app.route('/add_tag', methods=['POST'])
def add_tag():
    new_tag = request.form['tag']
    if new_tag not in tags:
        tags.append(new_tag)
        flash('Tag added successfully!', 'success')
    else:
        flash('Tag already exists!', 'danger')
    return redirect(url_for('manage_tags'))
@app.route('/edit_tag', methods=['POST'])
def edit_tag():
    old_tag = request.form['old_tag']
    new_tag = request.form['new_tag']
    if old_tag in tags and new_tag not in tags:
        tags[tags.index(old_tag)] = new_tag
        flash('Tag updated successfully!', 'success')
    else:
        flash('Invalid operation. Make sure the new tag does not already exist.', 'danger')
    return redirect(url_for('manage_tags'))
@app.route('/delete_tag/<tag>', methods=['POST'])
def delete_tag(tag):
    if tag in tags:
        tags.remove(tag)
        flash('Tag deleted successfully!', 'success')
    else:
        flash('Tag not found!', 'danger')
    return redirect(url_for('manage_tags'))




@app.route("/settings")
def settings():
    return render_template("settings.html")
@app.route("/change_username", methods=["POST"])
def change_username():
    if "user" not in session:
        flash("You need to log in first.", "danger")
        return redirect(url_for("login"))

    new_username = request.form["newUsername"]
    current_username = session["user"]

    if new_username in users:
        flash("Username already exists!", "danger")
    else:
        users[new_username] = users.pop(current_username)
        session["user"] = new_username
        flash("Username updated successfully!", "success")

    return redirect(url_for("settings"))


@app.route("/change_password", methods=["POST"])
def change_password():
    if "user" not in session:
        flash("You need to log in first.", "danger")
        return redirect(url_for("login"))

    current_password = request.form["currentPassword"]
    new_password = request.form["newPassword"]
    confirm_password = request.form["confirmPassword"]
    current_username = session["user"]

    if users.get(current_username) != current_password:
        flash("Current password is incorrect.", "danger")
        return redirect(url_for("settings"))

    if new_password != confirm_password:
        flash("New password and confirmation do not match.", "danger")
        return redirect(url_for("settings"))

    users[current_username] = new_password
    flash("Password updated successfully!", "success")
    return redirect(url_for("settings"))


@app.route("/update_email", methods=["POST"])
def update_email():
    if "user" not in session:
        flash("You need to log in first.", "danger")
        return redirect(url_for("login"))

    new_email = request.form["newEmail"]
    current_username = session["user"]

    # Mock email update logic
    # You may store and validate the email in your data structure
    flash(f"Email updated successfully to {new_email}!", "success")
    return redirect(url_for("settings"))



    

@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("You have been logged out.", "success")
    return redirect(url_for("get_started"))

if __name__ == "__main__":
    app.run(debug=True)