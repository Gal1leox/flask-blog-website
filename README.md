# ✍️Personal Blog Website

## I believe a typical social media platform has a number of negative aspects:
- People are distracted by ads.
- People waste time checking random user profiles.
- People check the likes on their posts. If someone doesn’t like a post, it may damage the friendship.
- People measure social status by the number of views, likes and subscriptions.

In addition, people often open social media unintentionally and are immediately flooded with new posts. <br />
It can take hours to scroll down to the very last post.

- - -

### To make a long story short:
Big companies do their best to keep users stuck in the app as long as possible. <br />
They don’t give a damn about users’ mental health or their time.

- - -

### I decided to make the complete opposite:
- No ADS
- No user profiles
- No views, likes and subscriptions

**The main feature:** only the blog owner can manage new posts.

Sounds unfair and boring, isn't it?)

The idea behind this project is to avoid distractions, unhealthy relationships, and to **focus on the owner’s news**. <br />
This is not entertaining place. This is the place where you get familiar with what's going on with the individual.

- - -

### ✨ Features:
- 🔐 **Authentication**
    - **Sign In**
        - Email
        - Google
    - **Sign Up**
        - Email
        - Google
    - **Reset Password**
        - Enter your email address
        - Enter and verify the code sent to your email
        - Set a new password
- 👤 **Profile Management**
    - Set a New Avatar Image
    - Change Username
    - Update Password
    - Toggle Theme (Light / Dark)
    - Delete Account
- 📝 **Posts**
    - **For All Users:**
        - View Posts
        - Save Posts
        - Share Post Link
        - **Manage Comments:**
            - View All Comments
                - Sort by Newest / Oldest
            - Create Comment
            - Edit Comment
            - Delete Comment
            - Reply to Comment
    - **For Admins:**
        - Create / Read / Update / Delete Posts
          Preview All Posts
        - Remove Other Users’ Comments
- 📬 **Contact Me** _(Regular Users only)_
    - First Name & Last Name
    - Inquiry Type:
        - General Inquiry
        - Collaboration Inquiry
        - Hiring Inquiry
    - Phone Number _(optional)_
    - Message
- 🛢 **Database Management** _(Admin Only)_
    - View Table Records
    - Delete Records
    - Backup Database
    - Restore Database from Backup

- - -

### 🛠 Tech Stack
- **Frontend:** HTML, Tailwind CSS, JavaScript (Alpine.js)
- **Backend:** Python, Flask, SQLAlchemy
- **Database:** SQLite
- **Containerization:** Docker
- **Web Server & Reverse Proxy:** Nginx

- - -

### 📂 Project Structure:
```
.
├── database-design
│   ├── assets
│   │   ├── dark-entity-relationship-diagram-highlighted.png
│   │   ├── dark-entity-relationship-diagram.png
│   │   ├── light-entity-relationship-diagram-highlighted.png
│   │   └── light-entity-relationship-diagram.png
│   └── dbdiagram.txt
├── instructions
│   ├── cloudinary
│   │   ├── screenshots
│   │   │   ├── 01_search_cloudinary.png
│   │   │   ├── 02_cloudinary_website.png
│   │   │   ├── 03_cloudinary_signup.png
│   │   │   ├── 04_cloudinary_settings.png
│   │   │   ├── 05_cloudinary_api_keys.png
│   │   │   └── 06_cloudinary_credentials.png
│   │   └── README.md
│   ├── gmail-app-password
│   │   ├── screenshots
│   │   │   ├── 01_search_google_account_security.png
│   │   │   ├── 02_google_account_website.png
│   │   │   ├── 03_google_account_app_passwords.png
│   │   │   ├── 04_google_account_app_passwords_app_name.png
│   │   │   └── 05_google_account_app_passwords_app_password.png
│   │   └── README.md
│   ├── google-authentication
│   │   ├── screenshots
│   │   │   ├── 01_google_developer_console.png
│   │   │   ├── 02_google_developer_console_api_and_services.png
│   │   │   ├── 03_google_developer_console_oauth_consent_screen.png
│   │   │   ├── 04_google_developer_console_app_information.png
│   │   │   ├── 05_google_developer_console_app_create.png
│   │   │   ├── 06_google_developer_console_create_oauth_client.png
│   │   │   ├── 07_google_developer_console_oauth_client_name_authorized_js_origins.png
│   │   │   ├── 08_google_developer_console_oauth_client_name_authorized_redirect_uris.png
│   │   │   └── 09_google_developer_console_oauth_credentials.png
│   │   └── README.md
│   ├── google-console
│   │   ├── screenshots
│   │   │   ├── 01_google_developer_console.png
│   │   │   ├── 02_google_developer_console_website.png
│   │   │   ├── 03_google_developer_console_create_project.png
│   │   │   ├── 04_google_developer_console_project_details.png
│   │   │   └── 05_google_developer_console_select_project.png
│   │   └── README.md
│   └── google-recaptcha
│       ├── screenshots
│       │   ├── 01_search_create_google_recaptcha.png
│       │   ├── 02_create_google_recaptcha_website.png
│       │   ├── 03_go_to_recaptcha_admin_console.png
│       │   ├── 04_set_label_and_recaptcha_type.png
│       │   ├── 05_add_domain_names_and_select_the_project.png
│       │   └── 06_recaptcha_credentials.png
│       └── README.md
├── nginx
│   └── default.conf
├── scripts
│   ├── create_admin.py
│   ├── drop_database.py
│   └── generate_token.py
├── use-case-diagram
│   └── blog-website-diagram.png
├── website
│   ├── __init__.py
│   ├── config.py
│   ├── errors.py
│   ├── extensions.py
│   ├── utils.py
│   ├── application
│   │   └── services
│   │       ├── __init__.py
│   │       ├── admin_service.py
│   │       ├── auth_service.py
│   │       ├── comment_service.py
│   │       ├── post_service.py
│   │       ├── public_service.py
│   │       └── settings_service.py
│   ├── domain
│   │   └── models
│   │       ├── __init__.py
│   │       ├── comment.py
│   │       ├── enums.py
│   │       ├── image.py
│   │       ├── post.py
│   │       ├── user.py
│   │       └── verification_code.py
│   ├── infrastructure
│   │   └── repositories
│   │       ├── __init__.py
│   │       ├── comment_repository.py
│   │       ├── post_repository.py
│   │       ├── table_repository.py
│   │       ├── user_repository.py
│   │       └── verification_code_repository.py
│   └── presentation
│       ├── forms
│       │   ├── __init__.py
│       │   ├── auth_forms.py
│       │   ├── base.py
│       │   ├── contact_forms.py
│       │   ├── fields.py
│       │   ├── post_forms.py
│       │   ├── settings_forms.py
│       │   └── validators.py
│       ├── middlewares
│       │   ├── __init__.py
│       │   └── auth_middleware.py
│       ├── routes
│       │   ├── __init__.py
│       │   ├── admin_routes.py
│       │   ├── auth_routes.py
│       │   ├── blueprints.py
│       │   ├── comment_routes.py
│       │   ├── post_routes.py
│       │   ├── public_routes.py
│       │   └── settings_routes.py
│       ├── static
│       │   ├── css
│       │   │   ├── globals.css
│       │   │   ├── shake-hand.css
│       │   │   └── swiper.css
│       │   ├── images
│       │   │   ├── covers
│       │   │   │   └── blog_author.jpg
│       │   │   ├── icons
│       │   │   │   └── spinner.svg
│       │   │   ├── favicon.ico
│       │   │   ├── no-avatar.jpg
│       │   │   └── post-loading.svg
│       │   └── js
│       │       ├── alpine.min.js
│       │       ├── pin-code.js
│       │       ├── swiper.js
│       │       └── tailwind-browser.js
│       └── templates
│           ├── components
│           │   ├── layout
│           │   │   └── navbar.html
│           │   └── ui
│           │       ├── navbar
│           │       │   ├── burger_button.html
│           │       │   ├── desktop_menu.html
│           │       │   ├── mobile_menu.html
│           │       │   └── user_dropdown.html
│           │       ├── post
│           │       │   ├── post.html
│           │       │   └── preview_post.html
│           │       ├── alert.html
│           │       ├── comment.html
│           │       ├── field.html
│           │       └── modal.html
│           └── pages
│               ├── auth
│               │   ├── admin
│               │   │   └── login.html
│               │   ├── user
│               │   │   ├── email_message.html
│               │   │   ├── forgot_password.html
│               │   │   ├── login.html
│               │   │   ├── register.html
│               │   │   ├── reset_password.html
│               │   │   └── verify_code.html
│               │   └── base.html
│               ├── errors
│               │   ├── 403.html
│               │   ├── 404.html
│               │   ├── 429.html
│               │   ├── 500.html
│               │   └── base.html
│               └── shared
│                   ├── admin
│                   │   ├── database.html
│                   │   └── new_post.html
│                   ├── posts
│                   │   ├── detail.html
│                   │   ├── list.html
│                   │   └── saved.html
│                   ├── user
│                   │   ├── contact.html
│                   │   └── email_message.html
│                   ├── base.html
│                   ├── home.html
│                   └── settings.html
├── instance
│   └── blog_website.db
├── .env
├── .env.example
├── .gitignore
├── README.md
├── Dockerfile
├── docker-compose.yml
├── main.py
└── requirements.txt
```

- - -

### 🏗 Setup & Installation:

#### Prerequisites:
- [Python 3.8+](https://www.python.org/downloads/)
- [Docker](https://docs.docker.com/engine/install/)

#### Steps:

1. **Clone the Repository:**
   ##### Using the web URL - HTTPS:
   ```
   git clone https://github.com/DaniilKalts/flask-blog-website.git
   cd flask-blog-website
   ```
   ##### Using a password-protected SSH key - SSH:
   ```
   git clone git@github.com:DaniilKalts/flask-blog-website.git
   cd flask-blog-website
   ```
2. **Setup External Services**
    - **Google Cloud Project:**  
      [Create a new Google Cloud project](./instructions/google-console)
    - **Gmail App Password:**  
      [Generate a Gmail app password](./instructions/gmail-app-password)
    - **Google OAuth Client:**  
      [Set up OAuth credentials](./instructions/google-authentication)
    - **Cloudinary API Credentials:**  
      [Obtain your Cloudinary keys](./instructions/cloudinary)
    - **Google reCAPTCHA:**  
      [Configure your reCAPTCHA project](./instructions/google-recaptcha)  
3. **Create and configure your `.env` file:**
    ```
    # Database Configuration
    DB_NAME=blog_website.db  # ← Replace with your database filename

    # Flask Configuration
    # SECRET_KEY: generate a secure random string from generate_token.py.
    # PREFERRED_URL_SCHEME: “http” for local dev, “https” for production.
    # FLASK_ENV: “development” or “production”.
    SECRET_KEY=REPLACE_WITH_SECURE_RANDOM_KEY    # ← Replace with your generated secret
    PREFERRED_URL_SCHEME=http                    # ← http or https
    FLASK_ENV=development                        # ← development or production

    # Admin Credentials
    # Set these to the admin account you will create.
    ADMIN_USERNAME=admin.user        # ← Replace with your desired admin username
    ADMIN_EMAIL=admin@example.com    # ← Replace with your admin gmail address
    ADMIN_PASSWORD=ChangeMe123!      # ← Replace with a strong admin password

    # Mail Configuration
    # Use the app-specific password.
    MAIL_PASSWORD=REPLACE_WTH_MAIL_APP_PASSWORD  # ← Replace with your mail password

    # Google OAuth Credentials
    # Obtain these from Google Cloud Console.
    CLIENT_ID=YOUR_GOOGLE_CLIENT_ID_HERE         # ← Replace with your Google OAuth client ID
    CLIENT_SECRET=YOUR_GOOGLE_CLIENT_SECRET_HERE # ← Replace with your Google OAuth client secret

    # Cloudinary Configuration
    # Get these from your Cloudinary dashboard.
    CLOUDINARY_NAME=example_cloud_name           # ← Replace with your Cloudinary cloud name
    CLOUDINARY_API_KEY=123456789012345           # ← Replace with your Cloudinary API key
    CLOUDINARY_SECRET=abcdefGhIjKLmnoPQRstuVwxYz # ← Replace with your Cloudinary API secret

    # reCAPTCHA Credentials
    # Register at Google reCAPTCHA to get these keys.
    RECAPTCHA_SITE_KEY=6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI   # ← Replace with your site key
    RECAPTCHA_SECRET_KEY=6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe # ← Replace with your secret key
    ```

3. **Run the Project:**

    - **With Docker:**
      1. **Run docker compose:**
          ```
          docker-compose up
          ```
      2. **Open in your browser:**  
          Navigate to: `http://127.0.0.1`

    - **Locally (without Docker):**
        1. **Create & activate a virtual environment:**
            - **Windows:**
              ```
              python -m venv .venv
              .venv\Scripts\activate
              ```  
            - **Linux/macOS:**
              ```
              python3 -m venv .venv
              source .venv/bin/activate
              ```
        2. **Install dependencies:**
           ```
           pip install -r requirements.txt
           ```
        3. **Start the project:**
           ```
           python main.py
           ```
        4. **Open in your browser:**  
           Navigate to: `http://127.0.0.1:5000`
