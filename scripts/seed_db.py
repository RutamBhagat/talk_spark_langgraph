import os
import json
from sqlalchemy.orm import Session
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())
from app.db.controllers.bio import save_new_user
from app.db.database import get_db
from app.models import models
from app.db.database import engine

db: Session = get_db()
models.Base.metadata.create_all(bind=engine)

# Get the current working directory
cwd = os.getcwd()

# Construct the full path to the JSON file
file_path = os.path.join(cwd, "scripts", "response.json")

# Load the JSON data from the file
with open(file_path, "r") as file:
    data = json.load(file)

# Iterate over the data and save each user to the database
for linkedin_url, user_data in data.items():
    save_new_user(linkedin_url=linkedin_url, scrapped_data=user_data)
