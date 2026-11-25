# Scoop 终端模拟器

`scoop.terminal.emulator` 是纯 Scoop 的 VT 核心。`Terminal.feed()` 接收输出字节并更新屏幕和历史，`encodeInput()` 根据当前模式编码文本、按键、鼠标和粘贴。回包、标题和响铃以值返回，可以在无窗口环境回放测试。

`scoop.ui.terminal` 提供桌面会话和 `terminalView(session)`。在 `Application.runWithAsyncio` 的作用域中调用 `TerminalEmulatorSession.start(command)`，把视图挂到 UI 树。会话通过 `EventLoop.spawnPty()` 启动子进程，并按序写入用户输入和 VT 回包。视图处理已接受的尺寸、历史浏览、选择、剪贴板和输入法。通过 `session.reading` 读取已提交的不可变画面；需要跨更新保留内容时取得 `session.snapshot()` 并在使用结束后关闭。嵌入方负责调用 `session.close()`，自然退出后可以继续展示最后的屏幕和状态。

组件后续改进见 [Terminal 组件改进设计](docs/terminal-component-design.md)，包含核心正确性、OSC、选择与搜索 API、字体连字、图形和性能；外围工具 UI 留给后续 demo。

组件提供 [scoop-terminal terminfo](terminfo/README.md)，与 XTGETTCAP 使用同一份能力表。核心也支持 DECRQM、DECRQSS 和字符/设备像素尺寸查询；无窗口使用者通过 `resize(..., pixels = ...)` 提供已接受的像素尺寸，未提供时像素查询报告 0。

OSC 52 默认允许写入、拒绝读取，文本上限为 1 MiB。可在创建核心或会话时传入 `TerminalClipboardPolicy(read = true)`，也可禁用写入；这不影响用户主动复制/粘贴。挂载的视图提供本机剪贴板及实际可用的 PRIMARY selection，未挂载时可通过 `start(clipboard = Some(adapter))` 注入 `TerminalClipboardAdapter`。异步读取的完成回调必须回到会话 owner，返回的 `Disposable` 用于取消；默认一秒期限、拒绝或服务不可用都会完成空回复。PTY 写队列为每个读取预留位置，后续回复和用户输入保持顺序。宿主服务错误可通过 `onHostServiceError` 观察。

## 开发

使用包含伪终端接口的 Scoop 工具链。使用 Scoop 源码仓库的开发 sysroot 时显式传入其路径。

```sh
scoop --sysroot ../scoop/sysroot test --release emulator
scoop --sysroot ../scoop/sysroot test --release terminal-ui
scoop --sysroot ../scoop/sysroot run --release demo
```

示例启动本机默认 shell，可以在 `--` 后指定可执行文件和参数。在有桌面会话的 macOS、Linux GNU 或 Windows 环境运行 `scoop --sysroot ../scoop/sysroot test --release demo`，可验证真实窗口 resize 和 shell 退出后的输出。Unix 用例还检查子进程发出的 VT 光标查询。
