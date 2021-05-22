"""Blogly application."""

from flask import Flask, request, redirect, render_template, flash
from models import db, connect_db, User, Post, Tag

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)
db.create_all()

from flask_debugtoolbar import DebugToolbarExtension
app.config['SECRET_KEY'] = "fhgfjgfjhgf"
debug = DebugToolbarExtension(app)

@app.route("/")
def root():
    posts = Post.query.order_by(Post.created_at.desc()).limit(5).all()
    return render_template("post_home.html", posts=posts)

@app.errorhandler(404)
def page_not_found(e):
    """Show 404 NOT FOUND page."""

    return render_template('404.html'), 404

@app.route("/users")
def list_users():
    """List users."""

    blogs = User.query.all()

    return render_template("list.html", blogs = blogs)

@app.route("/users/new", methods=["GET"])
def add_user_page():
    return render_template("add.html")

@app.route("/users/new", methods = ["POST"])
def add_user():
    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    image_url = request.form["image_url"]

    user = User(first_name = first_name, last_name = last_name, image_url = image_url or None)
    db.session.add(user)
    db.session.commit()

    return redirect("/users")

@app.route("/users/<int:user_id>")
def show_user(user_id):
    user = User.query.get_or_404(user_id)
    return render_template("show.html", user = user)

@app.route("/users/<int:user_id>/edit")
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    return render_template("edit.html", user = user)

@app.route("/users/<int:user_id>/edit", methods = ["POST"])
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    user.first_name = request.form['first_name']
    user.last_name = request.form['last_name']
    user.image_url = request.form['image_url']

    db.session.add(user)
    db.session.commit()

    return redirect("/users")

@app.route("/users/<int:user_id>/delete", methods=["POST"])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()

    return redirect("/users")


@app.route('/users/<int:user_id>/posts/new')
def posts_new_form(user_id):
    """Show a form to create a new post for a specific user"""

    user = User.query.get_or_404(user_id)
    tags = Tag.query.all()
    return render_template('post_new.html', user=user, tags = tags)


@app.route('/users/<int:user_id>/posts/new', methods=["POST"])
def posts_new(user_id):
    """Handle form submission for creating a new post for a specific user"""

    user = User.query.get_or_404(user_id)
    tag_ids = [int(n) for n in request.form.getlist("tags")]
    tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()

    new_post = Post(title=request.form['title'],
                    content=request.form['content'],
                    user=user,
                    tags = tags)

    db.session.add(new_post)
    db.session.commit()
    flash(f"Post '{new_post.title}' added.")

    return redirect(f"/users/{user_id}")


# POSTS

@app.route('/posts/<int:post_id>')
def posts_show(post_id):
    """Show a page with info on a specific post"""

    post = Post.query.get_or_404(post_id)
    return render_template('post_show.html', post=post)


@app.route('/posts/<int:post_id>/edit')
def posts_edit(post_id):
    """Show a form to edit an existing post"""

    post = Post.query.get_or_404(post_id)
    tags = Tag.query.all()
    return render_template('post_edit.html', post=post, tags=tags)


@app.route('/posts/<int:post_id>/edit', methods=["POST"])
def posts_update(post_id):
    """Handle form submission for updating an existing post"""

    post = Post.query.get_or_404(post_id)
    post.title = request.form['title']
    post.content = request.form['content']

    tag_ids = [int(num) for num in request.form.getlist("tags")]
    post.tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()

    db.session.add(post)
    db.session.commit()
    flash(f"Post '{post.title}' edited.")

    return redirect(f"/users/{post.user_id}")


@app.route('/posts/<int:post_id>/delete', methods=["POST"])
def posts_destroy(post_id):
    """Handle form submission for deleting an existing post"""

    post = Post.query.get_or_404(post_id)

    db.session.delete(post)
    db.session.commit()
    flash(f"Post '{post.title} deleted.")

    return redirect(f"/users/{post.user_id}")


@app.route("/tags")
def tags_list():
    tags = Tag.query.all()
    return render_template("tags_index.html", tags = tags)

@app.route("/tags/new")
def tags_new_form():
    posts = Post.query.all()
    return render_template("tags_new.html", posts = posts)

@app.route("/tags/new", methods=["POST"])
def tags_new():
    post_id = [int(n) for n in request.form.getlist("posts")]
    posts = Post.query.filter(Post.id.in_(post_id)).all()

    new_tag = Tag(name = request.form["name"], posts = posts)

    db.session.add(new_tag)
    db.session.commit()
    flash(f"Tag '{new_tag.name}' added.")

    return redirect("/tags")

@app.route("/tags/<int:tag_id>")
def tag_details(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    return render_template("tag_details.html", tag = tag)

@app.route("/tags/<int:tag_id>/edit")
def tags_edit_form(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    posts = Post.query.all()

    return render_template("tags_edit.html", tag = tag, posts = posts)

@app.route("/tags/<int:tag_id>/edit", methods=["POST"])
def tags_edit(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    tag.name = request.form["name"]
    post_ids = [int(n) for n in request.form.getlist("posts")]
    tag.post = Post.query.filter(Post.id.in_(post_ids)).all()

    db.session.add(tag)
    db.session.commit()
    flash(f"Tag '{tag.name}' edited.")

    return redirect("/tags")

@app.route("/tags/<int:tag_id>/delete", methods=["POST"])
def tags_delete(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    db.session.delete(tag)
    db.session.commit()
    flash(f"Tag '{tag.name}' deleted.")

    return redirect("/tags")

