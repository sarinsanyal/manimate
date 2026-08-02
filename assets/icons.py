import urllib.request
import os

os.makedirs("assets/icons", exist_ok=True)

# Corrected filenames for newer Lucide versions
icons = [
    "arrow-right",
    "book-open",
    "building",
    "building-2",      # was "landmark"
    "cloud-rain",
    "coins",
    "factory",
    "function-square", # might be "square-function" now
    "gavel",
    "globe",
    "hammer",
    "lightbulb",
    "rocket",
    "scroll",
    "thermometer",
    "trending-up",
    "triangle",
    "user",
    "users",
    "wheat",
    "wind",
    "square",
    "circle",
]

base = "https://raw.githubusercontent.com/lucide-icons/lucide/main/icons"

for icon in icons:
    url = f"{base}/{icon}.svg"
    dest = f"assets/icons/{icon}.svg"
    try:
        urllib.request.urlretrieve(url, dest)
        print(f"OK: {icon}.svg")
    except Exception as e:
        print(f"FAILED: {icon}.svg — {e}")