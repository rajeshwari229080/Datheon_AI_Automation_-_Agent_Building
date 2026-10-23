"""
Synchronize static distribution files for all GitHub Pages deployment methods:
1. Root (/index.html and /static)
2. Docs (/docs/index.html and /docs/static)
3. Ensure .nojekyll is present in root and docs
"""

import os
import shutil

def sync_assets():
    # Source files
    template_src = os.path.join("app", "dashboard", "templates", "index.html")
    static_src = os.path.join("app", "dashboard", "static")

    # 1. Sync to Root
    shutil.copy2(template_src, "index.html")
    if os.path.exists("static"):
        shutil.rmtree("static")
    shutil.copytree(static_src, "static")
    with open(".nojekyll", "w", encoding="utf-8") as f:
        f.write("")
    print("Synchronized root: index.html, static/, .nojekyll")

    # 2. Sync to Docs
    docs_dir = "docs"
    docs_static = os.path.join(docs_dir, "static")
    shutil.copy2(template_src, os.path.join(docs_dir, "index.html"))
    if os.path.exists(docs_static):
        shutil.rmtree(docs_static)
    shutil.copytree(static_src, docs_static)
    with open(os.path.join(docs_dir, ".nojekyll"), "w", encoding="utf-8") as f:
        f.write("")
    print("Synchronized docs: docs/index.html, docs/static/, docs/.nojekyll")

if __name__ == "__main__":
    sync_assets()
