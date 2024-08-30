# NeuroXiv Backend Project

This repository contains the backend project of NeuroXiv built with Flask, a lightweight WSGI web application framework. The backend handles API requests, interacts with the database, and provides data processing functionalities. The application is designed to be deployed using WSGI for a production environment.

## Project Architecture

- ### Project Architecture

  The project is structured as follows:

  - **LLM/**: Directory containing code and resources related to the Language Model (LLM) functionality.
  - **MoE/**: Contains modules and scripts for the Mixture of Experts (MoE) system.
  - **atlas/**: Directory for handling atlas-related functionalities, potentially including brain atlases or mappings.
  - **config/**: Configuration files and settings for the project, such as environment-specific configurations.
  - **database_generate_pipeline/**: Contains scripts and code for generating or processing the database, including data pipelines.
  - **features/**: Directory dedicated to feature extraction or related functionalities.
  - **storage/**: Directory for storing data, possibly including static files, datasets, or other persistent data.
  - **README.md**: Project documentation that provides an overview of the project, setup instructions, and usage guidelines.
  - **requirements.txt**: Lists all the dependencies and Python packages required for the project.
  - **__init__.py**: Initialization file for Python packages.
  - **basicfunc.py**: Contains basic utility functions used across the project.
  - **config.py**: Configuration file for the application settings, such as database connection strings and environment-specific variables.
  - **database.py**: Script handling database-related functionalities, possibly including ORM configurations or direct database queries.
  - **dataset.py**: Script for handling dataset loading, preprocessing, or manipulation.
  - **dataset_db.py**: Script for managing datasets that interact with the database.
  - **service.py**: Core service logic, likely contains the primary application logic and endpoint definitions.
  - **service.wsgi**: WSGI entry point to run the application in a production environment, enabling deployment with a WSGI server like Gunicorn or uWSGI.

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Pip (Python package installer)
- A WSGI server (e.g., Gunicorn, uWSGI)

### Installation

1. **Clone the repository:**

   ```
   git clone https://github.com/SEU-ALLEN-codebase/NeuroXiv.git
   cd backend
   ```

2. **Create and activate a virtual environment:**

   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install the dependencies:**

   ```
   pip install -r requirements.txt
   ```

4. **Run the application locally:**

   ```
   python service.py
   ```

   The application should now be running on `http://127.0.0.1:5000`.

## Deploying with WSGI

To deploy the Flask application in a production environment, we use a WSGI server. Here, we'll use Gunicorn as an example.

### Step 1: Install Gunicorn

Install Gunicorn using pip:

```
pip install gunicorn
```

### Step 2: Create a WSGI Entry Point

Ensure you have a `wsgi.py` file that exposes the Flask application object:

```
# wsgi.py
from app import app

if __name__ == "__main__":
    app.run()
```

### Step 3: Run the Application with Gunicorn

Run the application using Gunicorn:

```
gunicorn --workers 4 --bind 0.0.0.0:8000 wsgi:app
```

- `--workers 4`: Specifies the number of worker processes.
- `--bind 0.0.0.0:8000`: Binds the application to `0.0.0.0` on port `8000`.

### Step 4: Configure a Reverse Proxy (Optional)

In a production environment, it's recommended to use a reverse proxy like Nginx in front of Gunicorn. This provides an additional layer of security, handles static files, and improves performance.

#### Example Nginx Configuration:

```
server {
    listen 80;
    server_name your_domain.com;

    location / {
        root /var/www/html/dist;
        index index.html index.htm;
        try_files $uri $uri/ /index.html;

    }

    location /data/ {
        alias /<your data path>/dataset/;
    }

    location /api/ {
        rewrite ^/api/(.*) /$1 break;
        proxy_pass http://localhost:5000;
    }
}
```

Restart Nginx after making the configuration changes:

```
sudo systemctl restart nginx
```

### Step 5: Secure the Application

- **Use HTTPS**: Ensure your site is accessible over HTTPS. Use Let's Encrypt or another certificate authority to get an SSL certificate.
- **Environment Variables**: Keep sensitive information like `SECRET_KEY` and `DATABASE_URI` in environment variables and never hard-code them into your codebase.

## Conclusion

Your Flask application is now set up and ready to be deployed in a production environment using WSGI. Make sure to monitor the application performance and error logs to ensure smooth operation.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.
