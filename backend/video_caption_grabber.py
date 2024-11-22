import instaloader
import os
import glob
import re
import time
import shutil

class ProductPostFinder:
    def __init__(self):
        self.L = instaloader.Instaloader()
        self.L.download_video_thumbnails = False
        self.L.download_geotags = False
        self.L.download_comments = False
        self.L.save_metadata = False
        self.L.download_pictures = True
        
    def login(self, username, password):
        try:
            self.L.login(username, password)
            return True
        except Exception as e:
            print(f"Login failed: {e}")
            return False

    def search_product_posts(self, product_name, max_posts=10):
        found_posts = []
        search_urls = self._generate_search_tags(product_name)
        
        try:
            for url in search_urls:
                time.sleep(2)
                try:
                    # Use Instagram's GraphQL API endpoint instead
                    response = self.L.context.get_json(url)
                    
                    if not response or 'data' not in response:
                        continue
                    
                    posts = response.get('data', {}).get('hashtag', {}).get('edge_hashtag_to_media', {}).get('edges', [])
                    
                    for post_data in posts:
                        if len(found_posts) >= max_posts:
                            break
                            
                        post = post_data.get('node')
                        if not post:
                            continue
                            
                        shortcode = post.get('shortcode')
                        if not shortcode:
                            continue
                            
                        try:
                            full_post = instaloader.Post.from_shortcode(self.L.context, shortcode)
                            if self._is_relevant_sponsored_post(full_post, product_name):
                                found_posts.append(full_post)
                        except Exception as e:
                            print(f"Error fetching post {shortcode}: {e}")
                            continue
                            
                except Exception as e:
                    print(f"Error processing URL {url}: {e}")
                    continue
                    
            return found_posts
                        
        except Exception as e:
            print(f"Error searching posts: {e}")
            return []

    def _generate_search_tags(self, product_name):
        base_tag = re.sub(r'[^a-zA-Z0-9]', '', product_name.lower())
        
        # Updated search URL format
        search_url_template = "https://www.instagram.com/explore/search/keyword/?q=%23{}"
        
        tags = [
            base_tag,
            f"{base_tag}review",
            f"{base_tag}product",
            f"sponsored{base_tag}",
            "productreview",
            "sponsoredpost",
            "ad",
            "sponsored"
        ]
        
        # Convert tags to proper URL format
        search_urls = [search_url_template.format(tag) for tag in tags]
        return search_urls


    def _is_relevant_sponsored_post(self, post, product_name):
        if not post.caption:
            return False
        caption_lower = post.caption.lower()
        product_lower = product_name.lower()
        sponsored_indicators = [
            '#ad', '#sponsored', '#sponsoredpost', '#advertisement',
            'paid partnership', 'sponsored by', 'partner'
        ]
        is_sponsored = any(indicator in caption_lower for indicator in sponsored_indicators)
        contains_product = product_lower in caption_lower
        return is_sponsored and contains_product

    def grab_post(shortcode, posts_dir):
        print(f"Starting to grab post with shortcode: {shortcode}")
        L = instaloader.Instaloader()
        L.download_video_thumbnails = False
        L.download_geotags = False
        L.download_comments = False
        L.save_metadata = False
        L.download_pictures = True  # Enable picture download

        try:
            post = instaloader.Post.from_shortcode(L.context, shortcode)
            target_dir = f"posts/post_{shortcode}"
            L.dirname_pattern = f"posts/post_{shortcode}"
            L.download_post(post, target=shortcode)
            print(f"Post downloaded successfully: {target_dir}")

            # Create relevant directory
            relevant_dir = f"posts/output_frames_{shortcode}/relevant"
            os.makedirs(relevant_dir, exist_ok=True)

            # Create post info dictionary
            post_info = {
                'is_video': post.is_video,
                'is_sidecar': post.typename == 'GraphSidecar',
                'media_count': post.mediacount if hasattr(post, 'mediacount') else 1,
                'target_dir': target_dir,
                'relevant_dir': relevant_dir,
                'shortcode': shortcode
            }

            # Rename and organize files
            video_files = glob.glob(os.path.join(target_dir, "*.mp4"))
            if video_files:
                os.rename(video_files[0], os.path.join(target_dir, "video.mp4"))
                print("Video file renamed")

            caption_files = glob.glob(os.path.join(target_dir, "*.txt"))
            if caption_files:
                os.rename(caption_files[0], os.path.join(target_dir, "caption.txt"))
                print("Caption file renamed")

            # Handle images
            image_files = glob.glob(os.path.join(target_dir, "*.jpg"))
            for i, img_file in enumerate(image_files):
                new_name = f"image_{i+1}.jpg"
                new_path = os.path.join(target_dir, new_name)
                os.rename(img_file, new_path)
                # Copy to relevant directory
                shutil.copy2(new_path, os.path.join(relevant_dir, new_name))
                print(f"Image {i+1} processed and copied to relevant directory")

            print(f"Post info: {post_info}")  # Debug print
            return post_info

        except Exception as e:
            print(f"An error occurred in grabbing post: {e}")
            raise e

    def _rename_files(self, target_dir):
        video_files = glob.glob(os.path.join(target_dir, "*.mp4"))
        if video_files:
            os.rename(video_files[0], os.path.join(target_dir, "video.mp4"))

        caption_files = glob.glob(os.path.join(target_dir, "*.txt"))
        if caption_files:
            os.rename(caption_files[0], os.path.join(target_dir, "caption.txt"))

        image_files = glob.glob(os.path.join(target_dir, "*.jpg"))
        for i, img_file in enumerate(image_files):
            os.rename(img_file, os.path.join(target_dir, f"image_{i+1}.jpg"))
def grab_post(shortcode, posts_dir):
    print(f"Starting to grab post with shortcode: {shortcode}")
    L = instaloader.Instaloader(
        download_pictures=True,    # Enable image download
        download_videos=True,      # Enable video download
        download_video_thumbnails=False,
        download_geotags=False,
        download_comments=False,
        save_metadata=False,
        post_metadata_txt_pattern="caption"  # Save caption as caption.txt
    )

    try:
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        target_dir = f"posts/post_{shortcode}"
        L.dirname_pattern = target_dir
        
        # Create directories
        os.makedirs(target_dir, exist_ok=True)
        relevant_dir = f"posts/output_frames_{shortcode}/relevant"
        os.makedirs(relevant_dir, exist_ok=True)

        print(f"Downloading post {shortcode}...")
        print(f"Is video: {post.is_video}")
        print(f"Media type: {post.typename}")
        print(f"Media count: {post.mediacount if hasattr(post, 'mediacount') else 1}")

        # Download the post
        L.download_post(post, target=shortcode)
        print(f"Post downloaded successfully: {target_dir}")

        # Create post info dictionary
        post_info = {
            'is_video': post.is_video,
            'is_sidecar': post.typename == 'GraphSidecar',
            'media_count': post.mediacount if hasattr(post, 'mediacount') else 1,
            'target_dir': target_dir,
            'relevant_dir': relevant_dir,
            'shortcode': shortcode
        }

        # Rename and organize files
        if post.is_video:
            video_files = glob.glob(os.path.join(target_dir, "*.mp4"))
            if video_files:
                os.rename(video_files[0], os.path.join(target_dir, "video.mp4"))
                print("Video file renamed")

        # Handle images
        image_files = glob.glob(os.path.join(target_dir, "*.jpg"))
        print(f"Found {len(image_files)} image files")
        
        for i, img_file in enumerate(image_files):
            new_name = f"image_{i+1}.jpg"
            new_path = os.path.join(target_dir, new_name)
            os.rename(img_file, new_path)
            # Copy to relevant directory
            shutil.copy2(new_path, os.path.join(relevant_dir, new_name))
            print(f"Image {i+1} processed and copied to relevant directory")

        # Handle caption
        caption_files = glob.glob(os.path.join(target_dir, "*.txt"))
        if caption_files:
            os.rename(caption_files[0], os.path.join(target_dir, "caption.txt"))
            print("Caption file renamed")

        print(f"Post info: {post_info}")  # Debug print
        return post_info

    except Exception as e:
        print(f"An error occurred in grabbing post: {e}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        raise e

def process_product_request(product_name, username, password):
    finder = ProductPostFinder()
    
    if username and password:
        if not finder.login(username, password):
            return {"error": "Failed to login to Instagram"}
    
    try:
        posts = finder.search_product_posts(product_name)
        
        if not posts:
            return {"error": "No relevant sponsored posts found"}
            
        best_post = max(posts, key=lambda p: p.likes)
        posts_dir = "posts"
        os.makedirs(posts_dir, exist_ok=True)
        post_data = finder.grab_post(best_post, posts_dir)
        
        return {
            "success": True,
            "post_data": post_data
        }
        
    except Exception as e:
        return {"error": f"Error processing request: {e}"}

def process_product_background(product_name, request_id, progress_store, progress_lock):
    try:
        with progress_lock:
            progress_store[request_id] = {
                "progress": 0,
                "current_step": "Initializing product search...",
                "error": None
            }

        finder = ProductPostFinder()
        
        with progress_lock:
            progress_store[request_id]["progress"] = 20
            progress_store[request_id]["current_step"] = "Searching for product posts..."

        result = process_product_request(product_name, None, None)
        
        with progress_lock:
            if result.get("error"):
                progress_store[request_id]["error"] = result["error"]
            else:
                progress_store[request_id]["progress"] = 100
                progress_store[request_id]["current_step"] = "Processing complete!"
                progress_store[request_id]["result_ready"] = True
                progress_store[request_id]["result"] = result

    except Exception as e:
        with progress_lock:
            progress_store[request_id]["error"] = str(e)
            progress_store[request_id]["progress"] = 0