from fastapi import FastAPI,HTTPException,status,Depends
from pydantic import BaseModel
from database import engine,SessionLocal
from typing import Annotated
import models
from sqlalchemy.orm import Session

app= FastAPI()
models.Base.metadata.create_all(bind=engine)

class PostBase(BaseModel):
    title: str
    content: str
    user_id: int
class UserBase(BaseModel):
    username: str

def get_db():
    db= SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Annotation for our database injection
db_dependency= Annotated[Session, Depends(get_db)]

# Endpoint to create post
@app.post("/post/", status_code= status.HTTP_201_CREATED)
async def create_post(post:PostBase, db: db_dependency):
    db_post= models.Post(**post.dict())
    db.add(db_post)
    db.commit()
# Endpoint to fetch post
@app.get("/post_id/{post_id}", status_code=status.HTTP_200_OK)
async def read_post(post_id:int, db:db_dependency):
    post= db.query(models.Post).filter(models.Post.id==post_id).first()
    if post is None:
        raise HTTPException(status_code= 404, detail="Post not Found")
    return post

# Endpoint to delete post
@app.delete("/post_id/{post_id}", status_code=status.HTTP_200_OK)
async def delete_post(post_id: int, db: db_dependency):
    post= db.query(models.Post).filter(models.Post.id==post_id).first()
    if post is None:
        raise HTTPException(status_code= 404, detail= "Post not Found")
    db.delete(post)
    db.commit() 

# Endpoint to create User
@app.post("/user/", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserBase, db: db_dependency):
    db_user= models.User(**user.dict())
    db.add(db_user)
    db.commit()

@app.post("/user/", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserBase, db: db_dependency):
    # Check if the username already exists
    existing_user = db.query(models.User).filter(models.User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    db_user = models.User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)  # Optional: Refresh to get the auto-generated ID
    return {"detail": "User created successfully", "user": db_user}
# Endpoint to fetch all Users
@app.get("/user/", status_code=status.HTTP_200_OK)
async def fetch_all_users(db: db_dependency):
    users = db.query(models.User).order_by(models.User.id.asc()).all()
    if not users:
        raise HTTPException(status_code=404, detail="No users found")
    return users
# Endpoint to delete User
@app.delete("/user_id/{user_id}", status_code=status.HTTP_200_OK)
async def delete_user(user_id: int, db: db_dependency):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not Found")
    
    db.delete(user)
    db.commit()

    # Return a success message after commit
    return {"detail": f"User with id {user_id} deleted successfully"}

@app.put("/user_id/{user_id}", status_code=status.HTTP_200_OK)
async def update_user(user_id: int, user: UserBase, db: db_dependency):
    # Fetch the user to update
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update the user's information
    db_user.username = user.username
    db.commit()
    db.refresh(db_user)  # Refresh to get updated data from the database
    
    return {"detail": f"User with id {user_id} updated successfully", "user": db_user}
# Endpoint to fetch a user by ID
@app.get("/user_id/{user_id}", status_code=status.HTTP_200_OK)
async def fetch_user_by_id(user_id: int, db: db_dependency):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

