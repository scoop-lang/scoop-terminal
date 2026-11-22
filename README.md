# Scoop 终端模拟器

`scoop.terminal.emulator` 是纯 Scoop 的 VT 核心。`Terminal.feed()` 接收输出字节并更新屏幕和历史，`encodeInput()` 根据当前模式编码文本、按键、鼠标和粘贴。回包、标题和响铃以值返回，可以在无窗口环境回放测试。

`scoop.ui.terminal` 提供桌面会话和 `terminalView(session)`。在 `Application.runWithAsyncio` 的作用域中调用 `TerminalEmulatorSession.start(command)`，把视图挂到 UI 树。会话通过 `EventLoop.spawnPty()` 启动子进程，并按序写入用户输入和 VT 回包。视图处理已接受的尺寸、历史浏览、选择、剪贴板和输入法。嵌入方负责调用 `session.close()`，自然退出后可以继续展示最后的屏幕和状态。

## 开发

使用包含伪终端接口的 Scoop 工具链。使用 Scoop 源码仓库的开发 sysroot 时显式传入其路径。

```sh
scoop --sysroot ../scoop/sysroot test --release emulator
scoop --sysroot ../scoop/sysroot test --release terminal-ui
scoop --sysroot ../scoop/sysroot run --release demo
```

示例启动本机默认 shell，可以在 `--` 后指定可执行文件和参数。在有桌面会话的 macOS、Linux GNU 或 Windows 环境运行 `scoop --sysroot ../scoop/sysroot test --release demo`，可验证真实窗口 resize 和 shell 退出后的输出。Unix 用例还检查子进程发出的 VT 光标查询。
