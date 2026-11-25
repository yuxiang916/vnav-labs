"""用手机拍摄的棋盘格照片估计相机内参和畸变。"""

import argparse
import json
import math
from pathlib import Path

import cv2
import numpy as np


SUPPORTED_IMAGES = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}


def read_image(path, mode):
    return cv2.imdecode(
        np.fromfile(path, dtype=np.uint8), mode | cv2.IMREAD_IGNORE_ORIENTATION
    )


def save_preview(path, image):
    # 报告插图用缩略图。标定始终使用原始分辨率。
    height, width = image.shape[:2]
    scale = min(1.0, 1600 / max(height, width))
    if scale < 1:
        image = cv2.resize(image, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    success, encoded = cv2.imencode(".jpg", image)
    if not success:
        raise ValueError(f"无法保存预览图 {path}")
    encoded.tofile(path)


def calibrate(args):
    paths = sorted(
        path for path in args.images.iterdir()
        if path.is_file() and path.suffix.lower() in SUPPORTED_IMAGES
    )
    if not paths:
        raise ValueError("照片文件夹里没有支持的图片。手机若拍成 HEIC，请导出为 JPG 后再试。")

    pattern = (args.cols, args.rows)
    # 棋盘格在 Z=0 平面，点坐标的单位是毫米。
    board = np.zeros((args.cols * args.rows, 3), dtype=np.float32)
    board[:, :2] = np.mgrid[:args.cols, :args.rows].T.reshape(-1, 2) * args.square_mm

    image_size = None
    used, points, skipped = [], [], []
    for path in paths:
        gray = read_image(path, cv2.IMREAD_GRAYSCALE) if path.stat().st_size else None
        if gray is None:
            skipped.append({"file": path.name, "reason": "无法读取"})
            print(f"跳过 {path.name}，无法读取")
            continue
        found, corners = cv2.findChessboardCornersSB(gray, pattern)
        if not found:
            # 对打印纹理或局部光照导致 SB 漏检的照片，采用传统检测作后备。
            found, corners = cv2.findChessboardCorners(
                gray, pattern, cv2.CALIB_CB_ADAPTIVE_THRESH | cv2.CALIB_CB_NORMALIZE_IMAGE
            )
            if found:
                corners = cv2.cornerSubPix(
                    gray, corners, (11, 11), (-1, -1),
                    (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_MAX_ITER, 50, 0.001),
                )
        if not found:
            skipped.append({"file": path.name, "reason": "未检出完整角点"})
            print(f"跳过 {path.name}，未检出完整角点")
            continue
        size = (gray.shape[1], gray.shape[0])
        if image_size is None:
            image_size = size
        elif size != image_size:
            raise ValueError(
                f"{path.name} 的分辨率 {size} 与前面照片 {image_size} 不一致。"
                "请把同一镜头、同一分辨率和相同拍摄方向的原图放在一个文件夹。"
            )
        used.append(path)
        points.append(corners)
        print(f"通过 {path.name}")

    if len(used) < 3:
        raise ValueError(
            f"只有 {len(used)} 张照片通过检测。请先核对行列内角点数，"
            "再用不同倾斜角度拍足够多张清晰照片。"
        )

    rms, matrix, distortion, rvecs, tvecs = cv2.calibrateCamera(
        [board] * len(used), points, image_size, None, None
    )
    if not math.isfinite(rms) or not np.isfinite(matrix).all() or not np.isfinite(distortion).all():
        raise ValueError("标定未得到有限结果。请增加棋盘格朝向和位置的变化后重拍。")

    per_image = []
    for path, observed, rotation, translation in zip(used, points, rvecs, tvecs, strict=True):
        projected, _ = cv2.projectPoints(board, rotation, translation, matrix, distortion)
        delta = observed.reshape(-1, 2) - projected.reshape(-1, 2)
        error = float(np.sqrt(np.mean(np.sum(delta * delta, axis=1))))
        per_image.append({"file": path.name, "rms_px": error})

    distortion_by_name = dict(
        zip(("k1", "k2", "p1", "p2", "k3"), distortion.ravel().tolist(), strict=True)
    )
    result = {
        "opencv_version": cv2.__version__,
        "image_size_px": {"width": image_size[0], "height": image_size[1]},
        "checkerboard": {"inner_cols": args.cols, "inner_rows": args.rows, "square_mm": args.square_mm},
        "camera_matrix": matrix.tolist(),
        "intrinsics_px": {
            "fx": float(matrix[0, 0]), "fy": float(matrix[1, 1]),
            "cx": float(matrix[0, 2]), "cy": float(matrix[1, 2]),
        },
        "distortion": distortion_by_name,
        "overall_rms_px": rms,
        "per_image": per_image,
        "skipped": skipped,
        "preview_source": used[0].name,
    }

    args.output.mkdir(parents=True, exist_ok=True)
    sample = read_image(used[0], cv2.IMREAD_COLOR)
    marked = sample.copy()
    cv2.drawChessboardCorners(marked, pattern, points[0], True)
    save_preview(args.output / "original.jpg", sample)
    save_preview(args.output / "corners.jpg", marked)
    save_preview(args.output / "undistorted.jpg", cv2.undistort(sample, matrix, distortion))
    result_path = args.output / "calibration.json"
    result_path.write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")

    print(f"\n参与标定 {len(used)} 张，跳过 {len(skipped)} 张")
    for key, value in result["intrinsics_px"].items():
        print(f"{key} = {value:.3f} px")
    print(f"总重投影 RMS = {rms:.4f} px")
    print(f"结果文件：{result_path.resolve()}")
    if len(used) < 10:
        print("当前有效照片少于 10 张，建议再补不同倾斜角度的照片。")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("images", type=Path, help="棋盘格照片文件夹")
    parser.add_argument("--cols", type=int, required=True, help="棋盘格较长边上的内角点数")
    parser.add_argument("--rows", type=int, required=True, help="棋盘格较短边上的内角点数")
    parser.add_argument("--square-mm", type=float, required=True, help="实测单格边长，单位毫米")
    parser.add_argument("--output", type=Path, default=Path("calibration_result"), help="结果文件夹")
    args = parser.parse_args()
    if not args.images.is_dir():
        parser.error(f"找不到照片文件夹 {args.images}")
    if args.output.resolve() == args.images.resolve():
        parser.error("结果文件夹要和照片文件夹分开，以免覆盖原图。")
    if args.cols < 3 or args.rows < 3:
        parser.error("内角点每行和每列至少 3 个。")
    if not math.isfinite(args.square_mm) or args.square_mm <= 0:
        parser.error("单格边长必须是有限的正数。")
    try:
        calibrate(args)
    except (ValueError, OSError, cv2.error) as error:
        parser.exit(1, f"标定失败：{error}\n")


if __name__ == "__main__":
    main()
