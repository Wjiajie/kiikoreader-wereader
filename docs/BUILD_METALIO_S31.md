<!-- SPDX-FileCopyrightText: 2026 YIYO-Designer -->
<!-- SPDX-License-Identifier: LicenseRef-Kiikoread-Personal-Study-1.0 -->

# Metalio S31 构建指南

## 环境

- ESP-IDF `v6.1`（使用其他版本可能导致依赖锁文件或芯片驱动不兼容）。
- Python 和 CMake/Ninja 由 ESP-IDF 环境提供。
- 本机 Windows 开发优先使用 ESP-IDF PowerShell；Linux/macOS 可 source ESP-IDF 的 `export.sh`。

## 构建

在仓库根目录、ESP-IDF 环境已启用时执行：

```bash
python tools/build_firmware.py --board metalio47 --idf-metalio47 "$IDF_PATH" --python "$(command -v python)" --output build/boards --s31-pie --s31-text-ripple --s31-reader-panel37
```

Windows PowerShell 示例（请把 IDF 路径替换为本机 v6.1 安装目录）：

```powershell
python tools/build_firmware.py --board metalio47 --idf-metalio47 $env:IDF_PATH --python (Get-Command python).Source --output build/boards --s31-pie --s31-text-ripple --s31-reader-panel37
```

构建脚本负责选取板级源文件、调用 ESP-IDF 并验证输出包。实际产物路径以脚本末尾报告为准；临时中间文件保存在 `build/`。不要将本地构建目录或烧写包提交到源码仓库。

## CI

`.github/workflows/build.yml` 包含板级构建和主机侧回归检查。推送到 GitHub 后可在仓库 **Actions** 页面查看结果。发布固件前仍需对目标设备型号、镜像分区布局和校验值做独立确认。

## 设备烧写

本项目文档以源码构建为主。写入设备会覆盖固件分区并影响设备运行状态；务必确认板型、分区方案和镜像来源。不要把应用 OTA 镜像当作全量基础包，也不要在此 README 中引用个人串口号或本机绝对路径。
