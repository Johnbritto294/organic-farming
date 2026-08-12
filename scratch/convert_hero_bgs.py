import os
from PIL import Image

images_dir = r"c:\Users\jason\OneDrive - Stackly\Desktop\Farm\images"

hero_files = ["shopbg.jpg", "journalbg.jpg", "blogbg.jpg", "aboutbg.jpg", "contactbg.jpg"]

for fname in hero_files:
    in_path = os.path.join(images_dir, fname)
    out_name = os.path.splitext(fname)[0] + ".webp"
    out_path = os.path.join(images_dir, out_name)
    
    if not os.path.exists(in_path):
        print(f"Skipping {fname}, file not found.")
        continue
        
    print(f"Processing {fname} -> {out_name}...")
    img = Image.open(in_path).convert("RGB")
    
    # Resize hero background to max dimension 1400px for crisp display
    max_dim = 1400
    if max(img.width, img.height) > max_dim:
        ratio = max_dim / float(max(img.width, img.height))
        new_size = (int(img.width * ratio), int(img.height * ratio))
        img = img.resize(new_size, Image.Resampling.LANCZOS)
        
    quality = 85
    buffer_data = None
    
    from io import BytesIO
    buf = BytesIO()
    img.save(buf, format="WEBP", quality=quality, method=6)
    
    while buf.tell() > 102400 and quality > 15:
        quality -= 8
        buf = BytesIO()
        img.save(buf, format="WEBP", quality=quality, method=6)
        
    if buf.tell() > 102400:
        scale = 0.85
        while buf.tell() > 102400 and img.width > 500:
            img = img.resize((int(img.width * scale), int(img.height * scale)), Image.Resampling.LANCZOS)
            buf = BytesIO()
            img.save(buf, format="WEBP", quality=45, method=6)
            
    with open(out_path, "wb") as f_out:
        f_out.write(buf.getvalue())
        
    size_kb = os.path.getsize(out_path) / 1024.0
    print(f"  -> Created {out_name} ({size_kb:.1f} KB, dimensions={img.width}x{img.height})")

print("Hero backgrounds converted successfully!")
