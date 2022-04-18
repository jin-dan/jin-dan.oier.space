# coding: UTF-8
from bs4 import BeautifulSoup
import requests, json, sys
import pyoierspace

def get_slugs(target: list) -> list:
    target_slugs = []
    for i in target:
        target_slugs.append(i["slug"])
    return target_slugs

# 配置
token = sys.argv[1]
domain_prefix = sys.argv[2]

# 新建文章
with open("posts.json") as f:
    local_posts = json.load(f)
    remote_posts = pyoierspace.getPosts(domain_prefix)
    remote_slugs = get_slugs(remote_posts)
    for post in local_posts:
        if not post["slug"] in remote_slugs: 
            # 这篇的 slug 不在远程的 slug 列表里面，要新建
            with open("posts/{}.md".format(post["slug"])) as fc:
                print(pyoierspace.newPost(
                    domain_prefix,
                    token,
                    post["slug"],
                    post["title"],
                    post["intro"],
                    fc.read(),
                    post["category"],
                    post["top_level"]
                ))

# 修改文章
# TODO

# 删除文章
with open("posts.json") as f:
    local_posts = json.load(f)
    local_slugs = get_slugs(local_posts)
    remote_posts = pyoierspace.getPosts(domain_prefix)
    for post in remote_posts:
        if not post["slug"] in local_slugs: 
            # 远程的 slug 不在本地的 posts 里面，要删除
            pyoierspace.deletePost(token, post["pk"])