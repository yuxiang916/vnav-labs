# LAB0-2 双目深度估计

`stereo_depth.py` 比较 BM 和 SGBM，输出视差、相对深度及左右一致性统计。输入位于 `data`，原有结果位于 `results`。

在当前目录运行：

```bash
python -m pip install -r requirements.txt
python stereo_depth.py --output results_reproduce
```

输入图片已包含在仓库中；重新下载可运行 `python download_data.py`。图片来源与哈希见 `data/sources.json`。

图表文字使用 Windows 宋体；在其他系统运行时，将脚本中的 `FONT` 改为本机可用的中文字体路径。默认深度是 1/d；计算米制深度需同时提供与输入图像对应的 `--focal-px` 和 `--baseline-m`。

[实验报告](../reports/LAB0-2_实验报告.pdf) · [论文译文](../translations/LAB0-2_论文翻译.pdf)
