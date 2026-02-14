# UART MAC 地址读取工具

跨平台的 Python 工具，用于监控 USB UART/串口连接并从日志中提取设备信息（MAC 地址、域名/主机名）。支持 Windows、macOS 和 Linux。

## 功能特性

- **跨平台支持**：在 Windows、macOS 和 Linux 上运行
- **自动检测**：自动等待 USB UART 设备连接
- **MAC 地址提取**：从 `wifi:mode:sta (XX:XX:XX:XX:XX:XX)` 格式中提取 WiFi MAC 地址
- **域名解析**：检测服务器域名并判断环境（开发/生产）
- **会话日志**：保存带有毫秒级时间戳的日志
- **自动重连**：设备断开后自动重新连接

## 安装

### 从 GitHub 安装

```bash
# 安装最新版本
pip install git+https://github.com/375432636/uart-read-mac.git

# 安装指定版本
pip install git+https://github.com/375432636/uart-read-mac.git@v1.0.0
```

### 平台要求

**Linux:**
```bash
# 将用户添加到 dialout 组（访问 USB 串口需要）
sudo usermod -a -G dialout $USER
# 然后退出并重新登录
```

**macOS:**
- 可能需要为 USB-串口适配器安装驱动（FTDI、CH340、CP2102）

**Windows:**
- 使用 COM 端口，无需额外设置

## 使用方法

### 列出 UART 设备

列出所有已连接的 UART/串口设备及其详细信息：

```bash
list-uart
```

输出：
```
Platform: darwin
Found 1 UART device(s):

Device 1:
  Port:       /dev/ttyUSB0
  Name:       CP2102
  Description:  Silicon Labs CP2102
  Maker:       Silicon Labs
  Product:     CP2102
  Vendor ID:  10C4
  Product ID:  EA60
```

### 读取 MAC 地址

监控 UART 并提取 MAC 地址和域名信息：

```bash
# 自动检测并等待设备
uart-mac-reader

# 指定端口号
uart-mac-reader -p /dev/ttyUSB0

# 指定波特率（默认：115200）
uart-mac-reader -p /dev/ttyUSB0 -b 9600

# 运行一次（断开后不重连）
uart-mac-reader --once
```

输出：
```
[*] Monitoring for MAC addresses (Ctrl+C to stop)...

WiFi MAC Address: AA:BB:CC:DD:EE:FF
    Log: wifi:mode:sta (aa:bb:cc:dd:ee:ff) connecting to https://lumin-vas-dev.deep-edge.cn
    → host: lumin-vas-dev.deep-edge.cn, env: dev
```

### 打印日志

监控并记录 UART 输出，支持基于会话的文件保存：

```bash
# 自动检测并等待设备
print-log

# 指定端口号
print-log -p /dev/ttyUSB0

# 运行一次（断开后不重连）
print-log --once
```

**功能：**
- 日志保存到 `static/YYYYMMDD-HHMMSS.log` 文件
- 每次连接创建新的会话文件
- 日志文件包含毫秒级时间戳：`[2025-02-14 15:30:45.123] message`
- 会话标记显示开始/结束 ISO 时间戳

**日志文件示例：**
```
Session started: 2025-02-14T15:30:45.123456
============================================================
[2025-02-14 15:30:45.234] I (6099) AudioService: sample_rate=16000
[2025-02-14 15:30:46.123] I (7559) PowerManager: Battery: 70%
============================================================
Session ended: 2025-02-14T15:30:50.789012
```

## 命令行选项

所有工具都支持以下通用选项：

```bash
-p, --port    串口设备（如 /dev/ttyUSB0、COM3）
              未指定时自动等待设备连接
-b, --baudrate  波特率（默认：115200）
--once         运行一次后退出（断开时不重连）
```

## 域名/环境检测

工具自动从域名检测环境：

- **dev**：域名包含 "dev"（不区分大小写）
- **main**：其他情况

示例：
- `lumin-vas-dev.deep-edge.cn` → `env: dev`
- `lumin-vas.deep-edge.cn` → `env: main`

## 项目结构

```
uart-read-mac/
├── pyproject.toml          # 包配置
├── README.md               # 英文文档
├── README.zh-CN.md          # 中文文档（本文件）
├── LICENSE                 # MIT 许可证
├── uart_util.py            # 核心工具（UARTBase）
├── uart_mac_reader.py      # MAC 地址读取器
├── print_log.py             # 日志打印器（支持会话日志）
├── list_uart_devices.py    # 设备列表器
└── static/                  # 日志文件目录（自动创建）
```

## 开发

### 以可编辑模式安装

```bash
git clone https://github.com/375432636/uart-read-mac.git
cd uart-read-mac
pip install -e .
```

### 运行测试

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest
```

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件。

## 贡献

欢迎贡献！请随时提交 Pull Request。

## 支持

如有问题和建议，请使用 [GitHub Issues](https://github.com/375432636/uart-read-mac/issues)。
