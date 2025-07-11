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
        self,
        title: str,
        content: str,
        images: List[FileStorage],
        author_id: int,
        overall_rating: int,
        story_rating: int,
        gameplay_rating: int,
        graphics_rating: int,
        sound_design_rating: int,
        replay_value_rating: int,
        difficulty_rating: int,
        bug_free_rating: int,
        pc_requirements_rating: int,
        game_length_blocks: int,
        game_name: str,           # Added
        game_developer: str,      # Added
        category: str,            # Added
    ) -> Tuple[bool, str]:
        if not images:
            return False, "At least one image is required."

        post = Post(
            title=title,
            content=content,
            author_id=author_id,
            overall_rating=overall_rating,
            story_rating=story_rating,
            gameplay_rating=gameplay_rating,
            graphics_rating=graphics_rating,
            sound_design_rating=sound_design_rating,
            replay_value_rating=replay_value_rating,
            difficulty_rating=difficulty_rating,
            bug_free_rating=bug_free_rating,
            pc_requirements_rating=pc_requirements_rating,
            game_length_blocks=game_length_blocks,
            game_name=game_name,               # Added
            game_developer=game_developer,     # Added
            category=category,                 # Added
        )

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
        title: str,
        content: str,
        delete_ids: List[int],
        new_files: List[FileStorage],
        author_id: int,
        overall_rating: int,
        story_rating: int,
        gameplay_rating: int,
        graphics_rating: int,
        sound_design_rating: int,
        replay_value_rating: int,
        difficulty_rating: int,
        bug_free_rating: int,
        pc_requirements_rating: int,
        game_length_blocks: int,
        game_name: str,           # Added
        game_developer: str,      # Added
        category: str,            # Added
    ) -> Tuple[bool, str]:
        for img in list(post.images):
            if img.id in delete_ids:
                try:
                    cloudinary.uploader.destroy(img.public_id, invalidate=True)
                except Exception:
                    pass
                post.images.remove(img)
                db.session.delete(img)

        if not post.images and not new_files:
            return False, "At least one image is required."

        if len(post.images) + len(new_files) > self.MAX_IMAGES:
            return False, f"At most {self.MAX_IMAGES} images are allowed."

        if title != post.title:
            post.title = title

        if content != post.content:
            post.content = content

        if overall_rating != post.overall_rating:
            post.overall_rating = overall_rating
        
        if story_rating != post.story_rating:
            post.story_rating = story_rating
        
        if gameplay_rating != post.gameplay_rating:
            post.gameplay_rating = gameplay_rating

        if graphics_rating != post.graphics_rating:  
            post.graphics_rating = graphics_rating

        if sound_design_rating != post.sound_design_rating:
            post.sound_design_rating = sound_design_rating

        if replay_value_rating != post.replay_value_rating:    
            post.replay_value_rating = replay_value_rating

        if difficulty_rating != post.difficulty_rating:   
            post.difficulty_rating = difficulty_rating

        if bug_free_rating != post.bug_free_rating:    
            post.bug_free_rating = bug_free_rating

        if pc_requirements_rating != post.pc_requirements_rating:    
            post.pc_requirements_rating = pc_requirements_rating

        if game_length_blocks != post.game_length_blocks:    
            post.game_length_blocks = game_length_blocks
        
        # Added new fields
        if game_name != post.game_name:
            post.game_name = game_name

        if game_developer != post.game_developer:
            post.game_developer = game_developer

        if category != post.category:
            post.category = category

        for file in new_files:
            response = cloudinary.uploader.upload(
                file, folder="posts", resource_type="image"
            )
            url = response.get("secure_url")
            public_id = response.get("public_id")
            if not url or not public_id:
                continue

            new_img = Image(author_id=author_id, url=url, public_id=public_id)
            post.images.append(new_img)
            db.session.add(new_img)

        try:
            db.session.commit()
            return True, "Post edited successfully!"
        except Exception as e:
            db.session.rollback()
            return False, f"Error saving changes: {e}"


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
