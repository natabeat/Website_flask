from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from . import db
from .models import Recipe, Category, CuisineType, Tag, User, Like, Save, Comment, Chat

views = Blueprint('views', __name__)

# HOMEPAGE

@views.route('/')
def home():
    recipes = Recipe.query.order_by(Recipe.id.desc()).all()
    return render_template("home.html", recipes=recipes, user=current_user)

# SEARCH A RECIPE

@views.route('/search_recipes', methods=['GET'])
def search_recipes():
    query = request.args.get('query', '')
    user=current_user
    recipes = Recipe.query.filter(Recipe.ingredients.ilike(f"%{query}%")).all()

    return render_template('search_results.html', user=current_user, recipes=recipes, query=query)

# FILTER RECIPE

@views.route('/filter_recipes', methods=['GET'])
def filter_recipes():
    user=current_user
    tag_id = request.args.get('tag')
    cuisine_type_id = request.args.get('cuisine_type')
    category_id = request.args.get('category')

    filtered_recipes = Recipe.query

    if tag_id:
        filtered_recipes = filtered_recipes.filter(Recipe.tag.has(id=tag_id))

    if cuisine_type_id:
        filtered_recipes = filtered_recipes.filter_by(cuisine_type_id=cuisine_type_id)

    if category_id:
        filtered_recipes = filtered_recipes.filter_by(category_id=category_id)

    filtered_recipes = filtered_recipes.all()

    tags = Tag.query.all()
    cuisine_types = CuisineType.query.all()
    categories = Category.query.all()

    return render_template('filtered_browse.html', user=current_user, recipes=filtered_recipes, tags=tags, cuisine_types=cuisine_types, categories=categories)

# POST A RECIPE

@views.route('/post_recipe', methods=['GET', 'POST'])
@login_required
def post_recipe():
    if request.method == 'POST':
        title = request.form.get('title')
        ingredients = request.form.get('ingredients')
        preparation_steps = request.form.get('preparation_steps')
        cooking_time = request.form.get('cooking_time')
        category_id = request.form.get('category_id')
        cuisine_type_id = request.form.get('cuisine_type_id')
        tag_id = request.form.get('tag_id')
        images = request.form.get('images')
        videos = request.form.get('videos')

        new_recipe = Recipe(
            title=title,
            ingredients=ingredients,
            preparation_steps=preparation_steps,
            cooking_time=cooking_time,
            category_id=category_id,
            cuisine_type_id=cuisine_type_id,
            tag_id=tag_id,
            images=images,
            videos=videos,
            user_id=current_user.id
        )

        db.session.add(new_recipe)
        db.session.commit()

        flash('Recipe posted successfully', category='success')
        return redirect(url_for('views.home'))
    
    predefined_categories = Category.query.filter(Category.name.in_(['None', 'Breakfast', 'Lunch', 'Dinner', 'Appetizer', 'Salad', 'Side-dish', 'Baked-goods'])).all()
    predefined_cuisine_types = CuisineType.query.filter(CuisineType.name.in_(['None', 'French', 'Chinese', 'Japanese', 'Italian', 'Greek', 'Spanish', 'Croatian', 'Turkey', 'Thai', 'Indian', 'Mexican', 'American'])).all()
    predefined_tags = Tag.query.filter(Tag.name.in_(['None', 'Vegetarian', 'Gluten-free'])).all()
    
    return render_template("post_recipe.html", user=current_user, predefined_categories=predefined_categories, predefined_cuisine_types=predefined_cuisine_types, predefined_tags=predefined_tags)

# DELETE A RECIPE

@views.route('/delete_recipe/<int:recipe_id>', methods=['POST'])
@login_required
def delete_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)

    if current_user.id != recipe.user_id:
        abort(403)

    db.session.delete(recipe)
    db.session.commit()

    flash('Recipe deleted successfully', category='success')

    return redirect(url_for('views.home'))

# DISPLAY FULL RECIPE

@views.route('/recipe_detail/<int:recipe_id>', methods=['GET', 'POST'])
def recipe_detail(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)

    if request.method == 'POST':
        content = request.form.get('content')
        if content:
            new_comment = Comment(user_id=current_user.id, recipe_id=recipe_id, content=content, timestamp=datetime.utcnow())
            db.session.add(new_comment)
            db.session.commit()
            flash('Comment added', category='success')
        else:
            flash('Comment cannot be empty', category='warning')

        return redirect(url_for('views.recipe_detail', recipe_id=recipe_id))

    comments = Comment.query.filter_by(recipe_id=recipe.id).all()

    return render_template("recipe_detail.html", recipe=recipe, user=current_user, comments=comments)

# DISPLAY RECIPE AUTHOR PROFILE

@views.route('/recipe_author/<int:author_id>')
def recipe_author(author_id):
    author = User.query.get_or_404(author_id)
    followers = author.get_followers()
    following = author.get_follows()
    
    if author.profile_visibility == 'private' and current_user != author:
        flash("This user's profile is private.", 'warning')
        return redirect(url_for('views.home'))

    return render_template("recipe_author.html", author=author, user=current_user, followers=followers, following=following)

# DISPLAY FOLLOWER PROFILE

@views.route('/follower_profile/<int:follower_id>')
@login_required
def follower_profile(follower_id):
    follower = User.query.get_or_404(follower_id)

    return redirect(url_for('views.recipe_author', author_id=follower.id))

# DISPLAY FOLLOWING PROFILE

@views.route('/following_profile/<int:following_id>')
@login_required
def following_profile(following_id):
    following_user = User.query.get_or_404(following_id)
    
    return redirect(url_for('views.recipe_author', author_id=following_user.id))

# LIKE A RECIPE

@views.route('/like/<int:recipe_id>', methods=['POST'])
@login_required
def like_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    like = Like.query.filter_by(user_id=current_user.id, recipe_id=recipe_id).first()

    if like:
        db.session.delete(like)
        db.session.commit()
        flash('Like removed', category='success')
    else:
        new_like = Like(user_id=current_user.id, recipe_id=recipe_id)
        db.session.add(new_like)
        db.session.commit()
        flash('Recipe liked', category='success')

    return redirect(url_for('views.recipe_detail', recipe_id=recipe_id))

# SAVE A RECIPE

@views.route('/save/<int:recipe_id>', methods=['POST'])
@login_required
def save_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    save = Save.query.filter_by(user_id=current_user.id, recipe_id=recipe_id).first()

    if save:
        db.session.delete(save)
        db.session.commit()
        flash('Recipe removed from saved recipes', category='success')
    else:
        new_save = Save(user_id=current_user.id, recipe_id=recipe_id)
        db.session.add(new_save)
        db.session.commit()
        flash('Recipe saved', category='success')

    return redirect(url_for('views.recipe_detail', recipe_id=recipe_id))

# COMMENT ON RECIPE 

@views.route('/comment/<int:recipe_id>', methods=['POST'])
@login_required
def comment_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    content = request.form.get('content')

    if content:
        new_comment = Comment(user_id=current_user.id, recipe_id=recipe_id, content=content, timestamp=datetime.utcnow())
        db.session.add(new_comment)
        db.session.commit()
        flash('Comment added', category='success')
    else:
        flash('Comment cannot be empty', category='warning')

    return redirect(url_for('views.recipe_detail', recipe_id=recipe_id))

# DELETE A COMMENT

@views.route('/delete_comment/<int:comment_id>', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)

    if comment.user_id == current_user.id:
        recipe_id = comment.recipe_id
        db.session.delete(comment)
        db.session.commit()
        flash('Comment deleted', category='success')
        return redirect(url_for('views.recipe_detail', recipe_id=recipe_id))
    else:
        flash('You are not authorized to delete this comment', category='warning')
        return redirect(url_for('views.home'))
    
# PREFERENCES PAGE
    
@views.route('/preferences', methods=['GET', 'POST'])
@login_required
def preferences():
    if request.method == 'POST':
        current_user.show_comments = not current_user.show_comments
        db.session.commit()

    return render_template("preferences.html", user=current_user)

# TOGGLE COMMENTS ON/OFF

@views.route('/toggle_comments/<int:recipe_id>', methods=['POST'])
@login_required
def toggle_comments(recipe_id):
    recipe = Recipe.query.get(recipe_id)

    if recipe:
        if current_user == recipe.author:
            recipe.show_comments = not recipe.show_comments
            db.session.commit()

    return redirect(url_for('views.preferences'))

# FOR YOU PAGE

@views.route('/for_you')
@login_required
def for_you():

    liked_recipes = Like.query.filter_by(user_id=current_user.id).all()
    saved_recipes = Save.query.filter_by(user_id=current_user.id).all()
    comments = Comment.query.filter_by(user_id=current_user.id).all()

    liked_recipes = [like.recipe for like in liked_recipes]
    saved_recipes = [save.recipe for save in saved_recipes]

    return render_template('for_you.html', liked_recipes=liked_recipes, saved_recipes=saved_recipes, comments=comments, user=current_user)

# PROFILE

# DISPLAY PROFILE

@views.route('/user_profile')
@login_required
def user_profile():
    user = current_user
    followers = user.get_followers()
    following = user.get_follows()

    return render_template("user_profile.html", user=user, current_user=current_user, followers=followers, following=following)

# EDIT PROFILE

@views.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        user = current_user
        user.bio = request.form.get('bio')
        user.profile_image = request.form.get('profile_image')
        user.profile_visibility = request.form.get('profile_visibility')
        db.session.commit()
        flash('Profile updated successfully', category='success')
        return redirect(url_for('views.user_profile'))

    return render_template("edit_profile.html", user=current_user)

# COMMUNICATION FEATURES

# CHAT PAGE

@views.route('/conversation')
@login_required
def conversation():

    conversations = Chat.query.filter(
        ((Chat.sender_id == current_user.id) | (Chat.receiver_id == current_user.id))
        & (Chat.sender_id != Chat.receiver_id)
    ).distinct(Chat.sender_id, Chat.receiver_id).all()

    return render_template('conversation.html', user=current_user, conversations=conversations)

# DISPLAY A MESSAGE 

@views.route('/chat/<int:other_user_id>')
@login_required
def chat(other_user_id):

    other_user = User.query.get_or_404(other_user_id)

    messages = Chat.query.filter(
        ((Chat.sender_id == current_user.id) & (Chat.receiver_id == other_user_id)) |
        ((Chat.sender_id == other_user_id) & (Chat.receiver_id == current_user.id))
    ).order_by(Chat.timestamp).all()

    return render_template('chat.html', user=current_user, other_user=other_user, other_user_id=other_user_id, messages=messages)

# SEND A MESSAGE

@views.route('/send_message/<int:receiver_id>', methods=['POST'])
@login_required
def send_message(receiver_id):
    receiver = User.query.get_or_404(receiver_id)
    content = request.form.get('content')

    if content:
        message = Chat(sender_id=current_user.id, receiver_id=receiver_id, content=content, timestamp=datetime.utcnow())
        db.session.add(message)
        db.session.commit()
    else:
        flash('Message content cannot be empty.', category='warning')

    return redirect(url_for('views.chat', other_user_id=receiver_id))