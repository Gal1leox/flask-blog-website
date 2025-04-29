from typing import List, Optional, Tuple
from werkzeug.datastructures import FileStorage

import cloudinary.uploader

from website import db
from website.domain.models import Post, Image, SavedPost
from website.infrastructure.repositories import (
    PostRepository,
    ImageRepository,
    SavedPostRepository,
)


class PostService:
    MAX_IMAGES = 5

    def list_posts(self) -> List[Post]:
        return PostRepository.list_all()

    def get_post(self, post_id: int) -> Tuple[Optional[Post], str]:
        post = PostRepository.get_by_id(post_id)

        if post is None:
            return None, "Post not found."

        return post, ""

    def create_post(
        self, content: str, images: List[FileStorage], author_id: int
    ) -> Tuple[bool, str]:
        if not images:
            return False, "At least one image is required."

        post = Post(content=content, author_id=author_id)

        for img in images:
            response = cloudinary.uploader.upload(
                img, folder="posts", resource_type="image"
            )
            url = response.get("secure_url")
            public_id = response.get("public_id")
            if not url:
                continue

            new_img = Image(author_id=author_id, url=url, public_id=public_id)
            post.images.append(new_img)
            ImageRepository.add_image(new_img)

        PostRepository.save_post(post)
        return True, "Post created successfully!"

    def edit_post(
        self,
        post: Post,
        content: str,
        delete_ids: List[int],
        new_files: List[FileStorage],
        author_id: int,
    ) -> Tuple[bool, str]:
        for img in list(post.images):
            if img.id in delete_ids:
                try:
                    cloudinary.uploader.destroy(img.public_id, invalidate=True)
                except Exception:
                    pass
                post.images.remove(img)
                ImageRepository.delete_image(img)

        if not post.images and not new_files:
            return False, "At least one image is required."

        if len(post.images) + len(new_files) > self.MAX_IMAGES:
            return False, f"At most {self.MAX_IMAGES} images are allowed."

        if content != post.content:
            post.content = content

        for img in new_files:
            response = cloudinary.uploader.upload(
                img, folder="posts", resource_type="image"
            )
            url = response.get("secure_url")
            public_id = response.get("public_id")
            if not url:
                continue

            new_img = Image(author_id=author_id, url=url, public_id=public_id)
            post.images.append(new_img)
            ImageRepository.add_image(new_img)

        PostRepository.save_post(post)
        return True, "Post edited successfully!"

    def toggle_save(self, post_id: int, user_id: int) -> bool:
        saved = SavedPostRepository.find(user_id, post_id)
        if saved:
            SavedPostRepository.remove(saved)
            return False
        SavedPostRepository.add(SavedPost(user_id=user_id, post_id=post_id))
        return True

    def list_saved(self, user_id: int) -> List[Post]:
        return SavedPostRepository.list_by_user(user_id)

    def delete_post(self, post: Post) -> Tuple[bool, str]:
        try:
            SavedPostRepository.remove_by_post(post.id)

            for img in list(post.images):
                cloudinary.uploader.destroy(img.public_id, invalidate=True)
                ImageRepository.delete_image(img)

            PostRepository.delete_post(post)
            return True, f"Post {post.id} deleted successfully."
        except Exception as e:
            db.session.rollback()
            return False, str(e)
