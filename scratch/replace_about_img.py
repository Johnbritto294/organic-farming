import os
import urllib.request
from io import BytesIO
from PIL import Image

workspace_dir = r"c:\Users\jason\OneDrive - Stackly\Desktop\Farm"
images_dir = os.path.join(workspace_dir, "images")
out_path = os.path.join(images_dir, "farm_about_gen.webp")

url = "https://images.unsplash.com/photo-1500937386664-56d1dfef3854?auto=format&fit=crop&w=1000&q=80"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

print(f"Downloading new farming image from {url}...")
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, timeout=15) as resp:
    data = resp.read()

img = Image.open(BytesIO(data)).convert("RGB")

# Crop/Resize to portrait ratio 4:5 for ideal fit
max_dim = 1000
if max(img.width, img.height) > max_dim:
    ratio = max_dim / float(max(img.width, img.height))
    new_size = (int(img.width * ratio), int(img.height * ratio))
    img = img.resize(new_size, Image.Resampling.LANCZOS)

quality = 85
buf = BytesIO()
img.save(buf, format="WEBP", quality=quality, method=6)

while buf.tell() > 102400 and quality > 15:
    quality -= 8
    buf = BytesIO()
    img.save(buf, format="WEBP", quality=quality, method=6)

if buf.tell() > 102400:
    scale = 0.85
    while buf.tell() > 102400 and img.width > 300:
        img = img.resize((int(img.width * scale), int(img.height * scale)), Image.Resampling.LANCZOS)
        buf = BytesIO()
        img.save(buf, format="WEBP", quality=45, method=6)

with open(out_path, "wb") as f_out:
    f_out.write(buf.getvalue())

size_kb = os.path.getsize(out_path) / 1024.0
print(f"Saved images/farm_about_gen.webp ({size_kb:.1f} KB, dimensions={img.width}x{img.height})")
