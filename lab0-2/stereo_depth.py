"""LAB0-2：OpenCV Aloe 双目稠密视差与相对深度。

运行：python stereo_depth.py
可选真实标定：python stereo_depth.py --focal-px 700 --baseline-m 0.12
其中 focal-px 必须对应降采样后的图像；示例数字不是 Aloe 的标定值。
"""
import argparse
import csv
import hashlib
import json
import platform
import sys
from pathlib import Path
from time import perf_counter

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
FONT = "C:/Windows/Fonts/simsun.ttc"
CONFIGS = [
    ("BM_D128_B9", "BM", 128, 9),
    ("BM_D128_B15", "BM", 128, 15),
    ("SGBM_D128_B3", "SGBM", 128, 3),
    ("SGBM_D128_B5", "SGBM", 128, 5),
    ("SGBM_D128_B9", "SGBM", 128, 9),
    ("SGBM_D96_B5", "SGBM", 96, 5),
]


def read_image(path, flag=cv2.IMREAD_COLOR):
    """兼容 Windows 中文路径。"""
    if not path.is_file():
        raise FileNotFoundError(f"缺少 {path}，请先运行 download_data.py")
    image = cv2.imdecode(np.fromfile(path, dtype=np.uint8), flag)
    if image is None:
        raise ValueError(f"无法解码图像：{path}")
    return image


def save_image(path, image):
    ok, encoded = cv2.imencode(path.suffix, image)
    if not ok:
        raise ValueError(f"无法编码图像：{path}")
    encoded.tofile(path)


def make_matcher(algorithm, num_disp, block_size, min_disp=0):
    if num_disp <= 0 or num_disp % 16:
        raise ValueError("视差范围必须是正的16的倍数")
    if algorithm == "BM":
        obj = cv2.StereoBM_create(numDisparities=num_disp, blockSize=block_size)
        obj.setMinDisparity(min_disp)
        obj.setTextureThreshold(10)
        obj.setUniquenessRatio(10)
        obj.setSpeckleWindowSize(100)
        obj.setSpeckleRange(2)
        obj.setDisp12MaxDiff(1)
        return obj
    return cv2.StereoSGBM_create(
        minDisparity=min_disp, numDisparities=num_disp, blockSize=block_size,
        P1=8 * block_size**2, P2=32 * block_size**2,
        disp12MaxDiff=1, preFilterCap=31, uniquenessRatio=10,
        speckleWindowSize=100, speckleRange=2,
        mode=cv2.STEREO_SGBM_MODE_SGBM_3WAY,
    )


def disparity_color(disp, valid, max_disp=128):
    """所有实验共用0至128像素的颜色尺度，便于横向比较。"""
    values = np.uint8(np.clip(disp / max_disp, 0, 1) * 255)
    rgb = cv2.applyColorMap(values, cv2.COLORMAP_TURBO)
    rgb[~valid] = 0
    return rgb


def panel(images, labels, cols, path, cell_width=641):
    font = ImageFont.truetype(FONT, 24)
    rows = (len(images) + cols - 1) // cols
    h = round(images[0].shape[0] * cell_width / images[0].shape[1])
    canvas = Image.new("RGB", (cols * (cell_width + 20) + 20,
                               rows * (h + 55) + 20), "white")
    draw = ImageDraw.Draw(canvas)
    for i, (img, label) in enumerate(zip(images, labels)):
        x = 20 + (i % cols) * (cell_width + 20)
        y = 20 + (i // cols) * (h + 55)
        draw.text((x, y), label, font=font, fill="black")
        rgb = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        rgb = rgb.resize((cell_width, h), Image.Resampling.LANCZOS)
        canvas.paste(rgb, (x, y + 35))
    canvas.save(path)


def check_epipolar(left, right, output):
    sift = cv2.SIFT_create(nfeatures=4000)
    kp1, des1 = sift.detectAndCompute(left, None)
    kp2, des2 = sift.detectAndCompute(right, None)
    if des1 is None or des2 is None:
        raise RuntimeError("SIFT没有找到足够特征")
    pairs = cv2.BFMatcher().knnMatch(des1, des2, k=2)
    good = [a for group in pairs if len(group) == 2
            for a, b in [group] if a.distance < 0.7 * b.distance]
    p1 = np.float32([kp1[m.queryIdx].pt for m in good])
    p2 = np.float32([kp2[m.trainIdx].pt for m in good])
    if len(p1) < 8:
        raise RuntimeError("特征匹配点不足8个")
    _, inliers = cv2.findFundamentalMat(p1, p2, cv2.FM_RANSAC, 1.0, 0.999)
    if inliers is None:
        raise RuntimeError("基础矩阵估计失败")
    selected = inliers.ravel().astype(bool)
    residual = np.abs(p1[selected, 1] - p2[selected, 1])
    a, b = cv2.cvtColor(left, cv2.COLOR_GRAY2BGR), cv2.cvtColor(right, cv2.COLOR_GRAY2BGR)
    for y in range(40, left.shape[0], 70):
        cv2.line(a, (0, y), (a.shape[1] - 1, y), (0, 220, 0), 1)
        cv2.line(b, (0, y), (b.shape[1] - 1, y), (0, 220, 0), 1)
    panel([a, b], ["左图  水平参考线", "右图  水平参考线"], 2,
          output / "epipolar_check.png")
    return {"ratio_threshold": 0.7, "ransac_threshold_px": 1.0,
            "ratio_matches": len(good), "ransac_inliers": int(selected.sum()),
            "vertical_median_px": float(np.median(residual)),
            "vertical_p95_px": float(np.percentile(residual, 95))}


def run(args):
    if (args.focal_px is None) != (args.baseline_m is None):
        raise ValueError("真实焦距与基线必须同时提供")
    if args.focal_px is not None and min(args.focal_px, args.baseline_m) <= 0:
        raise ValueError("焦距与基线必须为正数")
    if args.repeats < 1:
        raise ValueError("计时重复次数至少为1")
    output = args.output
    output.mkdir(parents=True, exist_ok=True)
    cv2.setNumThreads(1)
    cv2.setRNGSeed(42)
    original_l = read_image(ROOT / "data" / "aloeL.jpg")
    original_r = read_image(ROOT / "data" / "aloeR.jpg")
    if original_l.shape != original_r.shape:
        raise ValueError("左右图像尺寸不一致")
    left, right = cv2.pyrDown(original_l), cv2.pyrDown(original_r)
    gl = cv2.cvtColor(left, cv2.COLOR_BGR2GRAY)
    gr = cv2.cvtColor(right, cv2.COLOR_BGR2GRAY)
    height, width = gl.shape
    # 固定公共评价区域，避免较大搜索范围和窗口导致边界损失影响比较。
    x0, y0, x1, y1 = 128 + 7, 7, width - 7, height - 7
    roi = np.zeros(gl.shape, dtype=bool)
    roi[y0:y1, x0:x1] = True
    yy, xx = np.indices(gl.shape)
    metrics, displays, labels, disps = [], [], [], {}
    panel([left, right], ["左图 aloeL", "右图 aloeR"], 2, output / "stereo_pair.png")
    epi = check_epipolar(gl, gr, output)
    for name, algorithm, num_disp, block_size in CONFIGS:
        matcher = make_matcher(algorithm, num_disp, block_size)
        matcher.compute(gl, gr)  # 预热不计入统计
        times = []
        for _ in range(args.repeats):
            start = perf_counter()
            raw = matcher.compute(gl, gr)
            times.append((perf_counter() - start) * 1000)
        disp = raw.astype(np.float32) / 16.0
        valid = (disp > 0) & (disp < num_disp)
        # 反向匹配的视差为负值，搜索范围与正向匹配相对应。
        reverse_min = -num_disp + 1
        reverse = make_matcher(algorithm, num_disp, block_size, reverse_min)
        dr = reverse.compute(gr, gl).astype(np.float32) / 16.0
        xr = np.rint(xx - disp).astype(np.int32)
        in_bounds = (xr >= 0) & (xr < width)
        sampled = dr[yy, np.clip(xr, 0, width - 1)]
        reverse_valid = (sampled > reverse_min - 1) & (sampled < 0)
        checked = valid & roi & in_bounds & reverse_valid
        consistent = checked & (np.abs(disp + sampled) <= 1.0)
        np.save(output / f"{name}_disparity.npy", disp)
        view = disparity_color(disp, valid)
        save_image(output / f"{name}.png", view)
        metrics.append({
            "config": name, "algorithm": algorithm,
            "num_disparities": num_disp, "block_size": block_size,
            "median_ms": float(np.median(times)), "times_ms": times,
            "valid_roi_percent": float(100 * (valid & roi).sum() / roi.sum()),
            "lr_checked_pixels": int(checked.sum()),
            "lr_pass_percent": float(100 * consistent.sum() / checked.sum()) if checked.any() else None,
            "lr_consistent_roi_percent": float(100 * consistent.sum() / roi.sum()),
            "roi_disparity_median_px": float(np.median(disp[valid & roi])),
        })
        displays.append(view)
        labels.append(f"{algorithm}  D={num_disp}  窗口={block_size}")
        disps[name] = (disp, valid, consistent)
        print(name, json.dumps(metrics[-1], ensure_ascii=False))
    panel(displays, labels, 3, output / "comparison_all.png")
    panel([displays[i] for i in [0, 2, 3, 4]],
          [labels[i] for i in [0, 2, 3, 4]], 2, output / "comparison_four.png")
    # 固定ROI放大观察叶片、背景纹理与遮挡边缘。
    crop = (240, 160, 500, 400)
    xa, ya, xb, yb = crop
    panel([left[ya:yb, xa:xb]] + [displays[i][ya:yb, xa:xb] for i in [0, 3, 4]],
          ["左图局部", "BM 窗口9", "SGBM 窗口5", "SGBM 窗口9"],
          2, output / "detail_comparison.png", cell_width=520)
    disp, valid, consistent = disps["SGBM_D128_B5"]
    rel = np.full(gl.shape, np.nan, dtype=np.float32)
    rel[valid] = 1.0 / disp[valid]
    np.save(output / "relative_depth.npy", rel)
    np.save(output / "valid_mask.npy", valid)
    np.save(output / "lr_consistent_mask.npy", consistent)
    limits = np.percentile(rel[valid & roi], [2, 98])
    gray_depth = np.zeros(gl.shape, dtype=np.uint8)
    gray_depth[valid] = np.uint8(np.clip((rel[valid] - limits[0]) /
                                       (limits[1] - limits[0]), 0, 1) * 255)
    depth_color = cv2.applyColorMap(gray_depth, cv2.COLORMAP_TURBO)
    depth_color[~valid] = 0
    save_image(output / "relative_depth.png", depth_color)
    panel([displays[3], depth_color],
          ["视差  暖色表示视差较大", "相对深度  暖色表示距离较远"],
          2, output / "depth_result.png")
    # 固定位置统计用于报告解释，只用于相对比较。
    regions = {"background": (145, 100, 210, 160),
               "plant": (270, 220, 350, 300),
               "foreground": (370, 405, 440, 470)}
    region_stats = {}
    for label, (a, b, c, d) in regions.items():
        mask = valid[b:d, a:c]
        ds = disp[b:d, a:c][mask]
        region_stats[label] = {"xyxy": [a, b, c, d], "valid_pixels": int(mask.sum()),
                               "median_disparity_px": float(np.median(ds)),
                               "median_relative_depth": float(np.median(1.0 / ds))}
    if args.focal_px is not None:
        depth_m = rel * args.focal_px * args.baseline_m
        np.save(output / "depth_m.npy", depth_m)
    result = {"environment": {"python": platform.python_version(),
                               "opencv": cv2.__version__, "numpy": np.__version__,
                               "platform": platform.platform(), "opencv_threads": 1},
              "input_size_wh": [original_l.shape[1], original_l.shape[0]],
              "processing_size_wh": [width, height], "downsampling": "cv2.pyrDown",
              "repeats": args.repeats, "common_roi_xyxy": [x0, y0, x1, y1],
              "roi_pixel_count": int(roi.sum()), "epipolar_check": epi,
              "disparity_display_range_px": [0, 128],
              "relative_depth_display_percentiles": [2, 98],
              "relative_depth_display_limits": limits.tolist(),
              "detail_crop_xyxy": list(crop), "region_statistics": region_stats,
              "focal_px": args.focal_px, "baseline_m": args.baseline_m,
              "metrics": metrics,
              "data_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                              for p in (ROOT / "data").glob("*.jpg")}}
    (output / "results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    fields = [key for key in metrics[0] if key != "times_ms"]
    with (output / "metrics.csv").open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows({key: value for key, value in m.items() if key in fields}
                         for m in metrics)
    print("Results:", output)


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "results")
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--focal-px", type=float, help="降采样后图像对应的真实像素焦距")
    parser.add_argument("--baseline-m", type=float, help="真实双目基线，单位米")
    run(parser.parse_args())
