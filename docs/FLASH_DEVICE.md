<!-- SPDX-FileCopyrightText: 2026 YIYO-Designer -->
<!-- SPDX-License-Identifier: LicenseRef-Kiikoread-Personal-Study-1.0 -->

# 将本仓库固件烧录到 Metalio S31

本 Cloud Agent 环境**无法访问你电脑上的 USB 串口**。请在本机（已连接电纸书的电脑）完成编译与烧录。

## 1. 准备

- 设备：Metalio E-INK4 Plus 4.7 **V1.5**（ESP32-S31）
- 电脑：已用数据线连接设备；Chrome/Edge 或 esptool
- 工具链：ESP-IDF **v6.1**（含 `esp32s31`）
- 源码：本仓库分支（例如 `cursor/metalio-s31-only-security-0709`）

若使用星曈云同步，构建前设置：

```bash
export KIIKO_XTEINK_APP_SECRET='你的密钥'
# 可选：export KIIKO_XTEINK_APP_ID='cl-20260508'
```

## 2. 编译（默认原生翻页，对齐官方 rc114）

```bash
# 先 source ESP-IDF export.sh
python tools/build_firmware.py --board metalio47 \
  --idf-metalio47 "$IDF_PATH" \
  --python "$(command -v python)" \
  --output build/boards
```

产物在 `build/boards/packages/metalio47/`（含 bootloader、partitions、ota_data、应用 bin、`flash_args` / `flash-command.txt`）。

## 3. 烧录方式

### A. 网页刷机（推荐第一次或修复）

1. 设备：**设置 → 升级和恢复 → BOOT 刷机**，进入下载模式  
2. 电脑打开 [kiikoread 官网刷机](https://kiikoread.com/?device=metalio#flash-action) 或本机构建的 flasher（若有）  
3. 用 Chrome/Edge 选择串口；**保留数据时不要勾选擦除**  
4. 也可上传本仓库打出的 USB 全量 ZIP 中的镜像（确认芯片为 esp32s31）

### B. esptool 命令行（本机构建包）

查看包内 `flash-command.txt`。典型形式（串口改成你的，如 `/dev/ttyUSB0` 或 `COM12`）：

```bash
python -m esptool --chip esp32s31 --port /dev/ttyUSB0 --baud 115200 \
  --before default-reset --after hard-reset --no-stub write-flash \
  --flash-mode dio --flash-size 16MB --flash-freq 80m \
  @flash_args
```

在 `build/boards/packages/metalio47/` 目录执行；S31 保留 `--no-stub`。

### C. 16 MiB 全闪存镜像（会清空账户/设置）

仅当需要整片恢复时使用，见 `docs/FULL_FLASH_16MB.md`。从地址 `0x0` 写入，**不要**写到 `0x10000`。

### D. TF 卡应用升级

将构建出的应用升级 bin 命名为 `Metalio-S31-update.bin` 放到 TF 根目录，在设备「升级和恢复」中升级。这不能替代完整基础包。

## 4. 烧录后核对

- 启动日志/关于页版本为 **0.3.3-rc114**（或本分支清单版本）  
- 微信读书页仍可用；恢复出厂会清除 WeRead 登录态  
- 传书热点口令为**设备随机生成**（屏上显示），网页须通过设备二维码打开以携带会话令牌
