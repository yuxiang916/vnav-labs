"""从 OpenCV 官方仓库下载本实验使用的原始双目图像。"""
from pathlib import Path
import hashlib
import json
import urllib.request

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)
BASE = "https://raw.githubusercontent.com/opencv/opencv/4.x/samples/data/"

manifest = []
for name in ["aloeL.jpg", "aloeR.jpg"]:
    path = DATA / name
    if not path.exists():
        with urllib.request.urlopen(BASE + name, timeout=60) as response:
            payload = response.read()
        if not payload.startswith(b"\xff\xd8"):
            raise ValueError(f"{name} 不是有效的 JPEG 文件")
        path.write_bytes(payload)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    manifest.append({"file": name, "url": BASE + name,
                     "sha256": digest, "bytes": path.stat().st_size})
    print(name, path.stat().st_size, digest)
(DATA / "sources.json").write_text(
    json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
