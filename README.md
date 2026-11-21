# Scoop 终端模拟器

终端核心是一个纯 Scoop Cone，接收子进程输出字节，维护 VT 终端状态和屏幕。核心的输入、输出和宿主事件用普通值表示，可以直接测试字节回放。桌面会话接入 Scoop 的 `EventLoop.spawnPty()`，由活动视图提交尺寸、呈现网格和处理交互。

## 开发

使用包含伪终端接口的 Scoop 工具链。使用 Scoop 源码仓库的开发 sysroot 时显式传入其路径。

```sh
scoop --sysroot ../scoop/sysroot test --release emulator
```
