from . import db
from .models import User, Follow
from flask import Blueprint, flash, redirect, url_for, request
from flask_login import login_required, current_user


follow = Blueprint('follow', __name__)

# FOLLOW

@follow.route('/follow/<int:author_id>', methods=['GET', 'POST'])
@login_required
def follow_user(author_id):
    author_to_follow = User.query.get(author_id)

    if current_user.is_following(author_to_follow):
        flash('You are already following this user.', category='success')
    else:
        follow = Follow(follower_id=current_user.id, following_id=author_to_follow.id)
        db.session.add(follow)
        db.session.commit()
        flash(f'You are now following {author_to_follow.username}.', category='success')

    return redirect(url_for('views.recipe_author', author_id=author_id))

# UNFOLLOW

@follow.route('/unfollow/<int:author_id>', methods=['POST'])
@login_required
def unfollow_user(author_id):
    author_to_unfollow = User.query.get(author_id)
    follow = Follow.query.filter_by(follower_id=current_user.id, following_id=author_to_unfollow.id).first()

    if not follow:
        flash(f'You are not following {author_to_unfollow.username}.', category='warning')
    else:
        db.session.delete(follow)
        db.session.commit()
        flash(f'You have unfollowed {author_to_unfollow.username}.', category='success')

    return redirect(url_for('views.recipe_author', author_id=author_id))