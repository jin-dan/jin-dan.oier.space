# coding: UTF-8
import requests, json
from bs4 import BeautifulSoup
import urllib.parse
from retry import retry

def getCategory(name: str, category: str) -> dict:
    content = requests.get("https://{}.oier.space/api/category.json?slug={}".format(name, category)).json()
    if content["status"] == "succeed":
        return content["category"]
    else:
        reason = "Get category failed"
        if "error" in content:
            reason = content["error"]
        raise RuntimeError(reason)

def getPosts(name: str, category = None) -> dict:
    content = {}
    if category is None:
        content = requests.get("https://{}.oier.space/api/posts.json".format(name)).json()
        if content["status"] == "succeed":
            return content["posts"]
        else:
            reason = "Get posts failed"
            if "error" in content:
                reason = content["error"]
            raise RuntimeError(reason)
    else:
        return getCategory(name, category)["posts"]

def getPost(name: str, post: str) -> dict:
    content = requests.get("https://{}.oier.space/api/post.json?slug={}".format(name, post)).json()
    if content["status"] == "succeed":
        return content["post"]
    else:
        reason = "Get post failed"
        if "error" in content:
            reason = content["error"]
        raise RuntimeError(reason)

'''
deprecated, use getInfo instead
def getName(name: str):
    content = requests.get("https://{}.oier.space/".format(name), headers={
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"
    })
    if content.status_code == 404:
        return "404"
    else:
        return BeautifulSoup(content.text, features="html5lib").title.string
'''

def getInfo(domainPrefix: str) -> dict:
    return requests.get("https://{}.oier.space/api/info.json".format(domainPrefix)).json()["category"]

def getCategories(domainPrefix: str) -> dict:
    return requests.get("https://{}.oier.space/api/categories.json".format(domainPrefix)).json()["categories"]

@retry(tries=3, delay=1)
def newPost(
        domainPrefix: str,
        token: str,
        post_slug: str,
        post_title: str,
        post_intro: str,
        post_content: str,
        post_category: str,
        post_topping_level: str
    ) -> dict:
    for category in getCategories(domainPrefix):
        if category["slug"] == post_category:
            post_category = category["pk"]
            break
    r = requests.post(
        "https://oier.space/api/new_post.json",
        data = {
            "token": token,
            "post_slug": post_slug,
            "post_title": post_title,
            "post_intro": post_intro,
            "post_content": post_content,
            "post_category": post_category,
            "post_topping_level": post_topping_level
        }
    )
    if r.status_code != 200 or json.loads(r.text)["status"] != "succeed":
        print(r.status_code, "Failed to create post, retrying...")
        raise RuntimeError("Failed to create post")
    return json.loads(r.text)

@retry(tries=3, delay=1)
def deletePost(token: str, pk: int) -> dict:
    r = requests.post("https://oier.space/api/delete_post.json", data = {
        "token": token,
        "post": pk
    })
    if r.status_code != 200 or json.loads(r.text)["status"] != "succeed":
        print(r.status_code, "Failed to delete post, retrying...")
    return json.loads(r.text)