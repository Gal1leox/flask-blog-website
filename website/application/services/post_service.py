from typing import List, Optional, Tuple
from werkzeug.datastructures import FileStorage

import cloudinary.uploader
from website import db
from website.domain.models.post import Post
from website.domain.models.image import Image
from website.domain.models import SavedPost
from website.infrastructure.repositories.post_repository import (
    PostRepository,
    ImageRepository,
    SavedPostRepository,
)


class PostService:
    MAX_IMAGES = 5

    def list_posts(self) -> List[Post]:
        """Return all posts, newest first."""
        return PostRepository.list_all()

    def get_post(self, post_id: int) -> Optional[Post]:
        """Fetch a single post by its ID (or None)."""
        return PostRepository.get_by_id(post_id)

    def create_post(
        self, content: str, images: List[FileStorage], author_id: int
    ) -> Tuple[bool, str]:
        if not images:
            return False, "At least one image is required."

        post = Post(content=content, author_id=author_id)

        for img in images:
            res = cloudinary.uploader.upload(img, folder="posts", resource_type="image")
            url = res.get("secure_url")
            if not url:
                continue

            # model field is `url`
            new_img = Image(author_id=author_id, url=url)
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
        # remove any to‐delete images
        for img in list(post.images):
            if img.id in delete_ids:
                post.images.remove(img)
                ImageRepository.delete_image(img)

        # require ≥1 image
        if not post.images and not new_files:
            return False, "At least one image is required."

        # enforce maximum
        if len(post.images) + len(new_files) > self.MAX_IMAGES:
            return False, f"Max {self.MAX_IMAGES} images allowed."

        # update content if changed
        if content != post.content:
            post.content = content

        # upload & attach new
        for img in new_files:
            res = cloudinary.uploader.upload(img, folder="posts", resource_type="image")
            url = res.get("secure_url")
            if not url:
                continue

            new_img = Image(author_id=author_id, url=url)
            post.images.append(new_img)
            ImageRepository.add_image(new_img)

        PostRepository.save_post(post)
        return True, "Post updated successfully!"

    def toggle_save(self, post_id: int, user_id: int) -> bool:
        """Return True if newly saved, False if unsaved."""
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

            PostRepository.delete_post(post)
            return True, f"Post {post.id} deleted."
        except Exception as e:
            db.session.rollback()
            return False, str(e)
