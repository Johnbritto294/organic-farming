import os
import re
import urllib.request
from io import BytesIO
from PIL import Image

workspace_dir = r"c:\Users\jason\OneDrive - Stackly\Desktop\Farm"
images_dir = os.path.join(workspace_dir, "images")
os.makedirs(images_dir, exist_ok=True)

html_files = [os.path.join(workspace_dir, f) for f in os.listdir(workspace_dir) if f.endswith('.html')]

# Regex for external images (Unsplash or direct image extensions)
url_pattern = re.compile(r'https://images\.unsplash\.com/[^\s"\'\<\>\)]+')

url_to_local = {}
count = 1

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

print(f"Found {len(html_files)} HTML files to process.")

# Collect unique URLs
all_urls = set()
for filepath in html_files:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        matches = url_pattern.findall(content)
        for m in matches:
            m_clean = m.rstrip(';,)"\'')
            all_urls.add(m_clean)

print(f"Found {len(all_urls)} unique external image URLs.")

for url in sorted(all_urls):
    filename = f"farm_img_{count:03d}.webp"
    local_path = os.path.join(images_dir, filename)
    rel_path = f"images/{filename}"
    
    print(f"[{count}/{len(all_urls)}] Downloading & processing: {url[:65]}...")
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()
        
        img = Image.open(BytesIO(data))
        
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGBA")
        else:
            img = img.convert("RGB")
            
        # Resize if width or height > 1000px
        max_dim = 1000
        if max(img.width, img.height) > max_dim:
            ratio = max_dim / float(max(img.width, img.height))
            new_size = (int(img.width * ratio), int(img.height * ratio))
            img = img.resize(new_size, Image.Resampling.LANCZOS)
            
        # Compress to WebP <= 100KB (102400 bytes)
        quality = 85
        buffer = BytesIO()
        img.save(buffer, format="WEBP", quality=quality, method=6)
            
        while buffer.tell() > 102400 and quality > 15:
            quality -= 10
            buffer = BytesIO()
            img.save(buffer, format="WEBP", quality=quality, method=6)
            
        if buffer.tell() > 102400:
            scale = 0.8
            while buffer.tell() > 102400 and img.width > 250:
                img = img.resize((int(img.width * scale), int(img.height * scale)), Image.Resampling.LANCZOS)
                buffer = BytesIO()
                img.save(buffer, format="WEBP", quality=50, method=6)
                
        with open(local_path, "wb") as f_out:
            f_out.write(buffer.getvalue())
            
        file_size_kb = os.path.getsize(local_path) / 1024.0
        print(f"  -> Saved {filename} ({file_size_kb:.1f} KB, quality={quality})")
        url_to_local[url] = rel_path
        count += 1
    except Exception as e:
        print(f"  FAILED to process {url}: {e}")

print("\n--- Replacing URLs in HTML files ---")
for filepath in html_files:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    replacements_made = 0
    for remote_url, local_rel in url_to_local.items():
        if remote_url in content:
            content = content.replace(remote_url, local_rel)
            replacements_made += 1
            
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print(f"Updated {os.path.basename(filepath)} with {replacements_made} image replacements.")

print("\nAll done! All images converted to WebP <= 100KB and downloaded locally.")
