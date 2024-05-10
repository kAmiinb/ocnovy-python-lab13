from fastapi import FastAPI, HTTPException, Path
from typing import Dict
import uvicorn
import requests
from pymongo import MongoClient
from pydantic import BaseModel


app = FastAPI()

# Підключення до MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["blog"]

# Колекції MongoDB для постів, коментарів та користувачів
posts_collection = db["posts"]
comments_collection = db["comments"]
users_collection = db["users"]


# Імпровізована база даних для зберігання постів
db: Dict[int, dict] = {
    1: {"id": 1, "title": "Перший пост", "content": "Це вміст першого поста"},
    2: {"id": 2, "title": "Другий пост", "content": "Це вміст другого поста"}
}

request_counts = {"version": 0, "posts": 0, "stats": 0}

class UserProfile(BaseModel):
    first_name: str
    last_name: str
    age: int
    


@app.get("/version")
def read_version():
    request_counts["version"] += 1
    return {"version": "1.0"}

@app.get("/posts/{post_id}")
def read_post(post_id: str = Path(..., title="The ID of the post to read")):
    post = posts_collection.find_one({"_id": post_id})
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@app.post("/posts")
def create_post(title: str, content: str, user_id: str):
    new_post = {"title": title, "content": content, "user_id": user_id}
    result = posts_collection.insert_one(new_post)
    return {"id": str(result.inserted_id), **new_post}

@app.put("/posts/{post_id}")
def update_post(post_id: int, title: str, content: str):
    request_counts["posts"] += 1
    if post_id not in db:
        raise HTTPException(status_code=404, detail="Post not found")
    db[post_id] = {"id": post_id, "title": title, "content": content}
    return db[post_id]

@app.delete("/posts/{post_id}")
def delete_post(post_id: int):
    request_counts["posts"] += 1
    if post_id not in db:
        raise HTTPException(status_code=404, detail="Post not found")
    del db[post_id]
    return {"message": "Post deleted"}

@app.get("/stats")
def get_stats():
    request_counts["stats"] += 1
    return request_counts

@app.post("/comments")
def create_comment(post_id: str, content: str, user_id: str):
    new_comment = {"post_id": post_id, "content": content, "user_id": user_id}
    result = comments_collection.insert_one(new_comment)
    return {"id": str(result.inserted_id), **new_comment}

@app.get("/comments/{comment_id}")
def read_comment(comment_id: str = Path(..., title="The ID of the comment to read")):
    comment = comments_collection.find_one({"_id": comment_id})
    if comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment

@app.post("/users")
def create_user(username: str, email: str):
    new_user = {"username": username, "email": email}
    result = users_collection.insert_one(new_user)
    return {"id": str(result.inserted_id), **new_user}

@app.get("/users/{user_id}")
def read_user(user_id: str = Path(..., title="The ID of the user to read")):
    user = users_collection.find_one({"_id": user_id})
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/profiles")
def create_profile(user_id: str, profile_data: UserProfile):
    user_profile = profile_data.dict()
    user_profile["user_id"] = user_id
    result = profiles_collection.insert_one(user_profile)
    return {"id": str(result.inserted_id), **user_profile}

@app.get("/profiles/{user_id}")
def read_profile(user_id: str = Path(..., title="The ID of the user to read profile")):
    profile = profiles_collection.find_one({"user_id": user_id})
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


response = requests.get("http://127.0.0.1:8000/version")
print("Version Endpoint Test:")
print("Status Code:", response.status_code)
print("Response Body:", response.json())
print()

# Тестовий сценарій для /posts/{post_id} (GET)
response = requests.get("http://127.0.0.1:8000/posts/1")
print("Read Post Endpoint Test:")
print("Status Code:", response.status_code)
print("Response Body:", response.json())
print()

# Тестовий сценарій для /posts (POST)
new_post_data = {"title": "Третій пост", "content": "Це вміст третього поста"}
response = requests.post("http://127.0.0.1:8000/posts", json=new_post_data)
print("Create Post Endpoint Test:")
print("Status Code:", response.status_code)
print("Response Body:", response.json())
print()

# Тестовий сценарій для /posts/{post_id} (PUT)
updated_post_data = {"title": "Оновлений пост", "content": "Оновлений вміст третього поста"}
response = requests.put("http://127.0.0.1:8000/posts/3", json=updated_post_data)
print("Update Post Endpoint Test:")
print("Status Code:", response.status_code)
print("Response Body:", response.json())
print()

# Тестовий сценарій для /posts/{post_id} (DELETE)
response = requests.delete("http://127.0.0.1:8000/posts/3")
print("Delete Post Endpoint Test:")
print("Status Code:", response.status_code)
print("Response Body:", response.json())
print()

# Тестовий сценарій для /stats (GET)
response = requests.get("http://127.0.0.1:8000/stats")
print("Stats Endpoint Test:")
print("Status Code:", response.status_code)
print("Response Body:", response.json())

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

#uvicorn lab11:app --reload
    
