# LAB0-1 相机标定

`calibrate_phone.py` 完成棋盘格角点检测、相机内参估计与图像去畸变；`photos/portrait` 为输入照片，`results` 为本次标定结果。

在当前目录运行：

```bash
python -m pip install -r requirements.txt
python calibrate_phone.py photos/portrait --cols 8 --rows 5 --square-mm 30 --output calibration_reproduce
```

棋盘格有 8×5 个内角点，单格边长 30 mm。打印板上的 100 mm（10 cm）线段用于校验打印尺寸。

[实验报告](../reports/LAB0-1_实验报告.pdf) · [论文译文](../translations/LAB0-1_论文翻译.pdf)
