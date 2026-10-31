# Changelog

## 0.1.22

- 将小程序“开源致谢”模块移动到页面最后
- README 更新为两张最新的小程序实机截图
- 分别展示已连接状态和未连接/离线模式入口

## 0.1.21

- 小程序使用说明页新增开源致谢模块
- 列出所用开源项目及许可证类型

## 0.1.20

- 增加第三方开源组件许可证与致谢文件
- 服务端分发包同步包含第三方许可证说明和可用许可证文本
- README 增加开源许可与致谢入口

## 0.1.19

- 将 `requirements.txt` 中的注释改为纯 ASCII
- 修复 Windows 7 下 pip 按 GBK 读取 UTF-8 中文注释时的解码错误

## 0.1.18

- Windows Python 下载增加清华和北外镜像自动回退
- 自动下载全部失败时打开官方下载页，并明确提示手动安装
- 修复 PowerShell 下载失败后批处理误报“安装完成但找不到 Python”

## 0.1.17

- Windows 自动安装脚本兼容 PowerShell 2.0
- Windows 7/8/8.1 自动安装 Python 3.8.10
- Windows 10/11 继续自动安装 Python 3.11.9
- 下载器改为 Windows 7 可用的 `System.Net.WebClient`

## 0.1.16

- 微信小程序导航栏标题改为“扫码枪工具”
- 微信开发者工具中的项目描述同步更新

## 0.1.15

- 小程序说明页按指定顺序重新排列
- macOS 启动问题和连接超时合并为“常见问题”模块

## 0.1.14

- 精简 macOS“无法验证开发者”的处理说明，仅保留必要操作步骤

## 0.1.13

- 补充 macOS Gatekeeper“无法验证开发者”的处理说明
- 小程序提供解除隔离并启动 macOS 客户端的终端命令
- 说明如何在“隐私与安全性”中使用“仍要打开”

## 0.1.12

- 小程序使用说明页新增联系作者信息
- 增加作者邮箱复制按钮：`wechat_scanner@163.com`
- README、快速开始和通用服务端包同步加入联系方式

## 0.1.11

- 修复 Windows CMD 使用字符绘制二维码时比例失真、难以扫描的问题
- Windows 启动后自动生成并打开标准黑白 PNG 二维码
- 图片打开失败时保留手动 IP 和端口连接方式

## 0.1.10

- 修复微信代码包未包含 ZIP 文件导致的 `readFileSync` 文件不存在错误
- 将服务端通用 ZIP 编码为小程序 JS 模块，在点击转发时还原并保存
- 转发不再依赖读取代码包内的 ZIP 静态文件

## 0.1.9

- Windows 和 macOS 服务端合并为一个通用 ZIP 包
- 包内提供 `START-FOR-WINDOWS.bat` 和 `START-FOR-MAC.command` 两个明确入口
- 小程序改为只转发一个通用服务端包，并显示各系统应双击的文件
- 增加 `QUICKSTART.txt`，打开压缩包即可看到两平台启动说明

## 0.1.8

- 新增离线模式，不连接电脑也能扫码
- 离线模式下不发送任何网络请求，只保存最近结果和扫码记录
- 离线模式会记住上次选择，并可随时切回连接电脑

## 0.1.7

- 小程序新增使用说明页和电脑服务端文件转发入口
- Windows/macOS 服务端包内置到小程序代码包
- 用户可把服务端转发到“文件传输助手”，再在电脑微信中下载
- 小程序说明中显示 GitHub 开源地址
- Windows/macOS 启动脚本在缺少 Python 时自动下载安装 Python

## 0.1.6

- 修复 GitHub Actions 发布任务未识别当前仓库的问题
- 自动发布时显式指定仓库，并继续上传 Windows/macOS 服务端包和校验值

## 0.1.5

- README 增加服务端和小程序实机截图、通俗原理说明及常见问题
- 新增 GitHub Actions 发布流程
- 自动在 Windows/macOS runner 上构建服务端包并创建 GitHub Release

## 0.1.4

- 项目名称改为 `WeChat-Barcode-Scanner`
- 同步更新微信小程序标题、项目配置、服务标识、文档和发布包名称
- 继续兼容读取 `WxMiniScanGun` 及更早的 `ScannerHost` 配置

## 0.1.3

- 项目正式更名为“微信小程序扫码枪”，技术名称为 `wx-mini-scangun`
- 同步更新微信小程序标题、项目配置、电脑端服务标识和文档
- 改名后继续兼容读取旧版 `ScannerHost` 配置

## 0.1.2

- 电脑端最低 Python 版本降到 3.7
- Windows/macOS 启动脚本支持 Python 3.7、3.8、3.9、3.10
- 使用 Python 3.7 兼容的类型标注，并增加旧虚拟环境检测

## 0.1.1

- macOS 新增 `start-mac.command`，支持在 Finder 中双击启动
- 新增保留 Unix 可执行权限的 macOS 分发包

## 0.1.0

- 电脑端 Python 服务：局域网 HTTP 接口 `/ping`、`/scan`、`/status`
- 键盘注入：Windows 使用 `SendInput`（支持 Unicode），macOS 使用 `Quartz`，通用路径使用 `pyautogui`
- 多网卡支持：启动时列出全部网卡 IPv4，由手机端逐个尝试连接
- 微信小程序：扫码连接、单次扫码发送、记录列表、失败提示
- Windows 一键启动脚本（首次自动创建 venv 并安装依赖，使用清华镜像源）
- macOS 脚本：`start.sh` / `bootstrap.sh` / `setup_env.sh`
- 可选二维码输出（`segno`），缺失时自动降级为文本连接信息
