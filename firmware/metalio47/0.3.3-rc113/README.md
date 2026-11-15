# Metalio S31 0.3.3-rc113 完整刷写包

本目录提供 Metalio S31（Metalio 4.7 V1.5，ESP32-S31）的完整固件安装包和刷写说明。

## 下载与校验

- 固件包：[`kiikoread-metalio47-0.3.3-rc113-full-flash.zip`](kiikoread-metalio47-0.3.3-rc113-full-flash.zip)
- SHA-256：见本目录 [`SHA256SUMS.txt`](SHA256SUMS.txt)

Windows PowerShell 可用以下命令校验下载文件：

```powershell
(Get-FileHash .\kiikoread-metalio47-0.3.3-rc113-full-flash.zip -Algorithm SHA256).Hash.ToLower()
```

计算结果应与 `SHA256SUMS.txt` 一致。校验失败时不要刷写，请重新下载。

## 包含内容

ZIP 内含 bootloader、分区表、应用固件、OTA 数据初始化镜像、完整安装命令、镜像清单与校验值。镜像写入地址由构建时针对 S31 分区表校验。

这是用于完整安装固件软件组件的多镜像包，不是整颗闪存的原始镜像。刷写会更新 bootloader、分区表、应用分区和 OTA 数据分区；**不会执行全片擦除，也不会覆盖 NVS、书籍存储或 coredump 分区**，因此现有设置和存储数据会保留。刷写前仍建议备份重要数据。

## Windows 刷写步骤

1. 确认设备是 Metalio S31 4.7 V1.5，不要用于 Pico 或其他板型。
2. 安装 Python 3，并安装与包内命令兼容的 esptool：

   ```powershell
   python -m pip install esptool==5.6.0
   ```

3. 解压固件 ZIP。用设备管理器确认 USB 串口号，并关闭占用该串口的串口监控程序。
4. 在 PowerShell 中切换到解压目录，执行下列命令，将 `COM12` 换成设备实际串口号：

   ```powershell
   python -m esptool --chip esp32s31 --port COM12 --before default-reset --after hard-reset --no-stub write-flash --flash-mode dio --flash-size 16MB --flash-freq 80m 0x2000 bootloader.bin 0x8000 partitions.bin 0x10000 firmware.bin 0xd000 ota_data_initial.bin
   ```

   ZIP 中的 `flash-command.txt` 也包含该命令，其中 `PORT` 是需要替换的占位符。esptool v5 请使用这个完整命令；不要将旧版 `@flash_args` 写法直接传给 v5。

5. 等待刷写完成。每个镜像都应显示 `Hash of data verified`，最后设备会通过 RTS 硬复位。

刷写期间不要拔线或关闭终端。若提示串口忙，请先关闭串口监控等占用程序。此包只写固件清单列出的四个地址，不需要先擦除整片闪存。

## 固件信息

- 版本：`0.3.3-rc113`
- 芯片目标：`esp32s31`
- 应用分区：`ota_0` / `ota_1`，每个 6 MiB
- PIE 像素、文字水波纹及 Reader Panel GL37 配置已启用
- 本包只用于本目录标明的 S31 板型
