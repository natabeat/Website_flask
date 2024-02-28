from . import db
from datetime import datetime
from flask_login import UserMixin

class Follow(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    following_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # RELATIONSHIS
    follower = db.relationship('User', foreign_keys=[follower_id], backref=db.backref('following_user', lazy='dynamic'), overlaps="following_user,follower_user")
    following = db.relationship('User', foreign_keys=[following_id], backref=db.backref('follower_user', lazy='dynamic'), overlaps="follower_user,following_user")
    # UC BECAUSE OVERLAPING
    __table_args__ = (db.UniqueConstraint('follower_id', 'following_id', name='_follower_following_uc'),)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    profile_visibility = db.Column(db.String(10), default='public')
    profile_image = db.Column(db.String(255), default=None, nullable=True)
    bio = db.Column(db.Text, default=None, nullable=True)
    # RELATIONSHIPS
    recipes = db.relationship('Recipe', backref='author', lazy=True)
    liked_recipes = db.relationship('Like', back_populates='user', lazy=True)
    saved_recipes = db.relationship('Save', back_populates='user', lazy=True)
    comments = db.relationship('Comment', back_populates='user', lazy=True)
    followers = db.relationship('Follow', foreign_keys=[Follow.following_id], backref=db.backref('following_user', lazy='joined'), lazy='dynamic', overlaps="following_user,follower_user")
    following = db.relationship('Follow', foreign_keys=[Follow.follower_id], backref=db.backref('follower_user', lazy='joined'), lazy='dynamic', overlaps="follower_user,following_user")
    def is_following(self, user):
        return Follow.query.filter_by(follower_id=self.id, following_id=user.id).first() is not None
    def get_followers(self):
        return self.followers.all()
    def get_follows(self):
        return self.following.all()
    
class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)
    ingredients = db.Column(db.Text, nullable=False)
    preparation_steps = db.Column(db.Text, nullable=False)
    cooking_time = db.Column(db.Text, nullable=False)
    images = db.Column(db.String(5000), default=None)
    videos = db.Column(db.String(5000), default=None)
    show_comments = db.Column(db.Boolean, default=True)
    # RELATIONSHIPS
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    cuisine_type_id = db.Column(db.Integer, db.ForeignKey('cuisine_type.id'), nullable=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'), nullable=True)
    likes = db.relationship('Like', back_populates='recipe', lazy=True)
    saves = db.relationship('Save', back_populates='recipe', lazy=True)
    comments = db.relationship('Comment', back_populates='recipe', lazy=True)
    
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    # RELATIONSHIP
    recipes = db.relationship('Recipe', backref='category', lazy=True)

class CuisineType(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    # RELATIONSHIP
    recipes = db.relationship('Recipe', backref='cuisine_type', lazy=True)

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    # RELATIONSHIP
    recipes = db.relationship('Recipe', backref='tag', lazy=True)

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # RELATIONSHIPS
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    user = db.relationship('User', back_populates='liked_recipes')
    recipe = db.relationship('Recipe', back_populates='likes')

class Save(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # RELATIONSHIPS
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    user = db.relationship('User', back_populates='saved_recipes')
    recipe = db.relationship('Recipe', back_populates='saves')

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    # RELATIONSHIPS
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    user = db.relationship('User', back_populates='comments')
    recipe = db.relationship('Recipe', back_populates='comments')

class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    # RELATIONSHIPS
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_messages')