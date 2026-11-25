# Terminal 组件实现进度

目标是完整交付 [组件改进设计](terminal-component-design.md) 的本轮范围。此文件记录完成证据和剩余工作；部分测试通过不代表整个设计完成。

实现分支：`codex/terminal-component-foundation`。每个可验证变更提交并推送后继续。先完成本机功能与验证，再集中进行 Linux / Windows 回归。

## 工作清单

| 阶段 | 工作 | 状态 |
| --- | --- | --- |
| M1 | 分页历史、行 ID 索引、复用不可变行内容 | 已实现，核心测试通过 |
| M1 | 逻辑行、正文 reflow、宽字素、anchor 定位与淘汰/重置失效 | 已实现，核心及选择回归通过 |
| M1 | VT 编辑的 anchor 迁移、覆盖通知及消费者失效 | 待实现 |
| M1 | 已提交快照、变化集、session reading 与消费者迁移 | 待实现 |
| M1 | VT 编辑/边距/复位/Unicode、传统键鼠、样式与光标 | 待实现 |
| M1 | 能力查询、准确的 capability 表、terminfo | 待实现 |
| M2 | 同步输出 2026、期限、流顺序与有序效果 | 待实现 |
| M2 | OSC 颜色查询/设置/重置 | 待实现 |
| M2 | OSC 8、OSC 52 与宿主服务策略 | 待实现 |
| M2 | OSC 7 工作目录、9;4 进度事件 | 待实现 |
| M3 | controller、高级选择、拖动滚动、复制规则 | 待实现 |
| M3 | 字面量搜索、casefold 映射、分页/取消/限额 | 待实现 |
| M3 | reveal、矩形、高亮与结果失效 | 待实现 |
| M3 | OSC 133 命令块及可选分割线 | 待实现 |
| M4 | 连字、网格校验、字体 fallback、装饰及缓存 | 待实现 |
| M5 | 串行后台 model、图片 store/decoder/cache、预算 | 待实现 |
| M5 | Sixel 编码、颜色、滚动、查询及生命周期 | 待实现 |
| M5 | Kitty 静态 profile、分块、放置/删除/探测 | 待实现 |
| M6 | 帧调度、局部失效、缓存/批量处理及基准报告 | 待实现 |
| M6 | 本机窗口/PTY、实际应用、资源释放与错误路径 | 待实现 |
| M6 | Linux 本轮完整回归 | 待本机完成后执行 |
| M6 | Windows 本轮完整回归 | 待本机完成后执行 |

搜索框、标签页、分屏和会话管理等外围 UI 按设计留待后续 demo；Kitty 的后续扩展范围以设计第 9 节为准，不将其冒充为已支持。

## 已执行验证

- 工具链：`~/.scoop/bin/scoop`，`0.0.0-dev.20261126`，编译器 `bb295704d`。
- `scoop test --release emulator`：23/23 通过，包括 3 项存储测试及 11 项 reflow 测试。
- `scoop test --release terminal-ui --filter TerminalViewportTest`：4/4 通过，包括跨 reflow 保持选区和宽字符换行补齐不进入复制内容。
- `scoop test --release terminal-ui --filter TerminalGlyphCacheTest`：2/2 通过，包括一列宽字素的实际替代符排版。
- 存储与 reflow 测试覆盖旧快照隔离、跨页淘汰/恢复、宽字素的一列占位、保存光标/样式、主备屏、逻辑边界 affinity、硬换行、实际空格及多次宽度变化。
- 当前 `~/repos/scoop/sysroot` 与安装工具链的测试执行入口不匹配；本轮使用完整的已安装 sysroot。没有发现需要修改编译器的缺口。

## 后续执行约束

外部依赖优先使用本地 `~/repos/scoop-dep`；需要下载时使用 `https_proxy=http://192.168.2.106:10809`。Linux 通过 `ssh nuc12`，在 `~/repos/` 创建本任务目录，依赖目录 `~/repos/scoop-deps`。Windows 通过 `/usr/bin/ssh 192.168.2.67`，在 `E:` 创建本任务目录，依赖目录 `E:/scoop-dep`。

如实际遇到编译器/底层库缺口，先在该仓库独立分支修复、验证、提交、推送、开 PR 并合并，再更新本地 main、合并回相应工作分支并更新工具链。临时文件只在仍用于后续工作时保留；阶段结束清理不再需要的文件。
