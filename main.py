from fastapi import FastAPI, Form, HTTPException, Request, Path
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from datetime import datetime
import uuid
from typing import Annotated

app = FastAPI()
templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")

class Post(BaseModel):
    post_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    content: str
    author: str
    date: datetime = Field(default_factory=datetime.now)

# In-memory data structure to store posts
posts = {}

# Sample posts for testing index.html
def create_sample_posts():
    sample_posts = [
        Post(title="Post 1", content="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras fringilla dolor tincidunt molestie mollis. In faucibus finibus sollicitudin. Praesent consequat sem est, sed viverra urna blandit vel. Pellentesque venenatis molestie dolor, quis hendrerit magna molestie eget. Aenean finibus lobortis velit eu luctus. Pellentesque consectetur nulla sit amet eros convallis finibus. Nullam convallis luctus nisl ut mattis. Quisque id odio eleifend, dictum magna ut, consequat magna.", author="Author 1"),
        Post(title="Post 2", content="Ut dapibus sed ante quis porta.", author="Author 2")
    ]
    for post in sample_posts:
        posts[post.post_id] = post

create_sample_posts()


@app.get("/")
async def read_index(request: Request):
    sorted_posts = sorted(posts.values(), key=lambda x: x.date, reverse=True)
    return templates.TemplateResponse("index.html", {"request": request, "posts": sorted_posts})


@app.get("/post/{post_id}")
async def read_post(
    request: Request,
    post_id: Annotated[str, Path(title="The ID of the post to read")]
):
    if post_id not in posts:
        raise HTTPException(status_code=404, detail="post ID not found")
    return templates.TemplateResponse("post.html", {"request": request, "post": posts[post_id]})


@app.get("/create")
async def create_new_post(request: Request,):
    return templates.TemplateResponse("create.html", {"request": request})


@app.post("/create-post")
async def create_post(
    title: str = Form(...), 
    content: str = Form(...), 
    author: str = Form(...)
):
    new_post = Post(title=title, content=content, author=author)
    posts[new_post.post_id] = new_post
    return RedirectResponse("/", status_code=303)


@app.get("/edit/{post_id}")
async def edit_post(
    request: Request,
    post_id: Annotated[str, Path(title="The ID of the post to edit")],
):
    if post_id not in posts:
        raise HTTPException(status_code=404, detail="post ID not found")
    return templates.TemplateResponse("edit.html", {"request": request, "post": posts[post_id]})


@app.post("/edit-post/{post_id}")
async def update_post(
    post_id: Annotated[str, Path(title="The ID of the post to read")],
    content: str = Form(...)
):
    posts[post_id].content = content
    return RedirectResponse(f"/post/{post_id}", status_code=303)


@app.post("/delete/{post_id}")
async def delete_post(
    post_id: Annotated[str, Path(title="The ID of the post to read")]):
    del posts[post_id]
    return RedirectResponse("/", status_code=303)