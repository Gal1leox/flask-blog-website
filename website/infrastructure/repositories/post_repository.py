from typing import List, Optional

from website import db
from website.domain.models import Post, Image, SavedPost


class PostRepository:
    @staticmethod
    def list_all() -> List[Post]:
        return Post.query.order_by(Post.created_at.desc()).all()

    @staticmethod
    def get_posts_by_tags(tags: List[str]) -> List[Post]:
        query = Post.query
        for tag in tags:
            query = query.filter(Post.content.ilike(f"%#{tag}%"))
        return query.order_by(Post.created_at.desc()).all()

    @staticmethod
    def get_by_id(post_id: int) -> Optional[Post]:
        return Post.query.get(post_id)

    @staticmethod
    def save_post(post: Post) -> None:
        db.session.add(post)
        db.session.commit()

    @staticmethod
    def delete_post(post: Post) -> None:
        db.session.delete(post)
        db.session.commit()


class ImageRepository:
    @staticmethod
    def add_image(image: Image) -> None:
        db.session.add(image)
        db.session.commit()

    @staticmethod
    def delete_image(image: Image) -> None:
        db.session.delete(image)
        db.session.commit()


class SavedPostRepository:
    @staticmethod
    def find(user_id: int, post_id: int) -> Optional[SavedPost]:
        return SavedPost.query.filter_by(user_id=user_id, post_id=post_id).first()

    @staticmethod
    def add(saved: SavedPost) -> None:
        db.session.add(saved)
        db.session.commit()

    @staticmethod
    def remove(saved: SavedPost) -> None:
        db.session.delete(saved)
        db.session.commit()

    @staticmethod
    def remove_by_post(post_id: int) -> None:
        SavedPost.query.filter_by(post_id=post_id).delete()
        db.session.commit()

    @staticmethod
    def list_by_user(user_id: int) -> List[Post]:
        items = (
            SavedPost.query.filter_by(user_id=user_id)
            .join(Post)
            .order_by(SavedPost.saved_at.desc())
            .all()
        )
        return [s.post for s in items]
