import json
from sqlalchemy.orm import Session
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())
from app.db.access_layer.linkedin_bio import save_new_user
from app.db.database import get_db

db: Session = get_db()
# Load the JSON data from the file
with open("response.json", "r") as file:
    data = json.load(file)

# Iterate over the data and save each user to the database
for linkedin_url, user_data in data.items():
    save_new_user(linkedin_url=linkedin_url, scrapped_data=user_data)
