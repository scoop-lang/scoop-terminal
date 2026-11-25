# Terminal 组件实现进度

目标是完整交付 [组件改进设计](terminal-component-design.md) 的本轮范围。此文件记录完成证据和剩余工作；部分测试通过不代表整个设计完成。

实现分支：`codex/terminal-component-foundation`。每个可验证变更提交并推送后继续。先完成本机功能与验证，再集中进行 Linux / Windows 回归。

## 工作清单

| 阶段 | 工作 | 状态 |
| --- | --- | --- |
| M1 | 分页历史、行 ID 索引、复用不可变行内容 | 已实现，核心测试通过 |
| M1 | 逻辑行、正文 reflow、宽字素、anchor 定位与淘汰/重置失效 | 已实现，核心及选择回归通过 |
| M1 | VT 编辑的 anchor 迁移、覆盖通知及消费者失效 | 待实现 |
| M1 | 已提交快照、变化集、session reading 与消费者迁移 | 已实现，快照与视图回归通过 |
| M1 | 有界 OSC 分派、流式 DCS/APC 生命周期与解析恢复 | 已实现，解析器 6 项测试通过 |
| M1 | 上下/左右边距、矩形滚动、宽字符编辑、DECSC/DECSTR/RIS | 已实现，核心 40 项测试通过 |
| M1 | Unicode 17 字素/宽度、创建时 ambiguous 策略、变体序列与零宽前缀 | 已实现，核心 46 项测试通过 |
| M1 | 运行中修改宽度策略的全量重排 | 待实现 |
| M1 | 传统键鼠、1016 像素鼠标、水平滚轮 | 已实现，5 项输入协议用例通过 |
| M1 | 下划线类型/颜色、光标形状、独立闪烁 | 已实现，4 项协议及 3 项绘制/缓存用例通过 |
| M1 | DECRQM/DECRQSS/XTGETTCAP、尺寸查询及共享 terminfo 能力表 | 已实现，5 项协议用例及生成一致性/语法检查通过；图形能力在图形阶段加入 |
| M2 | 同步输出 2026、序列边界提交、独立硬期限 | 已实现，完整核心 65 项通过；真实 PTY 期限在集中验收验证 |
| M2 | 异步宿主效果的有序回复票据 | 已实现，虚拟期限/乱序完成/关闭回归通过 |
| M2 | OSC 颜色查询/设置/重置 | 已实现，5 项协议、5 项快照及 4 项绘制/缓存用例通过 |
| M2 | OSC 8 超链接与交互 | 核心 6 项及交互/光栅 3 项通过；公开 controller 的 point 查询随 M3 接入 |
| M2 | OSC 52 与宿主剪贴板策略 | 已实现，4 项核心及 4 项桥接/队列用例通过；真实系统剪贴板在集中验收验证 |
| M2 | OSC 7 工作目录、9;4 进度事件 | 已实现，5 项核心用例及 UI 编译检查通过 |
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
- `scoop --sysroot ../scoop/sysroot test --release emulator`：46/46 通过，包括 8 项边距/编辑/复位、6 项解析、3 项存储、11 项 reflow、5 项快照及 6 项 Unicode 宽度测试。
- 同步输出改动后的完整 `emulator` 回归：65/65 通过。新增 5 项覆盖 feed 内多次 BSU/ESU、冻结期间查询与输入、重复 BSU 的同一期限代次、显式期限释放、EOF/resize/RIS 及旧历史快照隔离；UI 测试代码编译检查通过。
- `scoop --sysroot ../scoop/sysroot test --release emulator --filter InputProtocolTest`：5/5 通过，覆盖 Ctrl 别名、修饰功能键/方向键、小键盘、X10/传统原始字节、跟踪/编码独立切换、1016 像素及横向滚轮。视图从已接受布局的设备缩放计算像素坐标；未接受尺寸或 DPI 不用于鼠标报告。
- `scoop --sysroot ../scoop/sysroot test --release emulator --filter RenditionTest`：4/4 通过，覆盖 4:0..5、21/24、58/59、无效色彩空间、DECSCUSR、光标可见性/闪烁独立及保存恢复。
- `scoop --sysroot ../scoop/sysroot test --release emulator --filter CapabilityQueryTest`：5/5 通过，覆盖流顺序中的真实模式、SGR 回包回放、分块/取消/上限、未知查询失败及像素变化保留边距。UI 测试代码编译检查通过。
- `python3 tools/generate_capabilities.py --check` 与 `tic -x -c terminfo/scoop.terminfo`：通过；查询和安装 profile 来自同一能力表，生成临时文件自动清理。
- `scoop --sysroot ../scoop/sysroot test --release emulator --filter OscColorTest`：5/5 通过；`SnapshotTest` 5/5 通过；绘制/缓存 4/4 通过。覆盖 16-bit 查询、X11 `#` 高位与 `rgb:` 比例转换、批量参数、当前主题重置、独立的显式 RGB、冻结颜色及实际像素；快照配额已计入完整调色板的保守占用。
- OSC 52：核心 `ClipboardProtocolTest` 4/4、UI `ClipboardBridgeTest` 4/4 通过。覆盖默认拒绝读取、禁写、严格 Base64/UTF-8、空内容清空、字节限额、目标顺序、有序 PTY 票据、异步乱序完成、虚拟一秒期限、卸载/关闭后迟到结果、无服务、异常及最多 32 个待处理读取。已消费或取消的票据释放其输出字节。
- `ShellMetadataTest` 5/5 通过，覆盖 OSC 7 的远端 host/百分号路径、无效 URI、OSC 9;4 缺省与保留百分比、0..100 限制、冻结期间事件顺序和 EOF/RIS 清理。元数据计入快照配额；组件没有目录访问、通知、任务栏或进度工具 UI。
- OSC 8 核心 `HyperlinkTest` 6/6 通过；由于链接引用回收覆盖全部屏幕编辑路径，本次完整核心回归 85/85 通过。覆盖任意字节切分、参数保留、显式 ID 分组、宽格尾部、重排、矩形滚动、淘汰、保存光标与旧快照隔离；按记录数/字节限额拒绝新链接并产生诊断。链接记录保存在共享不可变索引中，单元格仅存 ID，已提交快照计入相应保守占用。
- `TerminalLinkInteractionTest` 3/3 通过，覆盖已接受帧的链接命中、宽字符尾列、拖动阈值/取消/越界/不同链接不激活，以及显式 ID 多片段悬停的实际像素。`TerminalViewOptions` 提供 `onLinkActivated` / `onLinkHovered`，普通点击仍选择，Ctrl/Command 修饰点击只触发回调；应用鼠标模式优先，Shift 绕过。指针 claim、取消通知及不可取消的 release 清理已接入；真实窗口事件路径留集中验收验证。
- `scoop --sysroot ../scoop/sysroot test --release terminal-ui --filter TerminalGlyphCacheTest`：3/3 通过；新增 CPU 光栅验证检查双下划线颜色、文字隐藏阶段和光标闪烁互不混淆。文字和光标计时只请求帧，复用已经排版的内容，卸载时取消计时。
- `scoop test --release terminal-ui --filter TerminalViewportTest`：5/5 通过，包括跨 reflow 保持选区、宽字符换行补齐不进入复制内容，以及已接受帧在 resize 后仍定位原字符。
- `scoop test --release terminal-ui --filter TerminalGlyphCacheTest`：2/2 通过，包括一列宽字素的实际替代符排版。
- `scoop test --release emulator --filter ParserTest`：6/6 通过，包括每个字节边界的切分、冒号子参数/中间字节、CAN/SUB/EOF、非法 DCS header、OSC 精确上限与超限整串丢弃。
- `scoop check --release demo --tests`：通过；session 消费者已迁移到只读 `reading`。
- 快照验证覆盖旧代次隔离、共享历史页及索引、同代次配额共享、关闭释放、文本/样式/光标版本分离；快照字节配额采用保守内容估算，不等同于进程实测 RSS。
- 存储与 reflow 测试覆盖旧快照隔离、跨页淘汰/恢复、宽字素的一列占位、保存光标/样式、主备屏、逻辑边界 affinity、硬换行、实际空格及多次宽度变化。
- Scoop 底层已补齐完整字素宽度、显式 ambiguous 策略及统一的 Unicode 17 字素分段，独立提交并合并 [PR #220](https://github.com/scoop-lang/scoop/pull/220) 和 [PR #221](https://github.com/scoop-lang/scoop/pull/221)。release clippy、charset 用例、原生 ABI 均通过。开发 sysroot 已使用安装编译器完整重建，后续命令显式传 `--sysroot ../scoop/sysroot`；没有修改编译器。

## 后续执行约束

外部依赖优先使用本地 `~/repos/scoop-dep`；需要下载时使用 `https_proxy=http://192.168.2.106:10809`。Linux 通过 `ssh nuc12`，在 `~/repos/` 创建本任务目录，依赖目录 `~/repos/scoop-deps`。Windows 通过 `/usr/bin/ssh 192.168.2.67`，在 `E:` 创建本任务目录，依赖目录 `E:/scoop-dep`。

如实际遇到编译器/底层库缺口，先在该仓库独立分支修复、验证、提交、推送、开 PR 并合并，再更新本地 main、合并回相应工作分支并更新工具链。临时文件只在仍用于后续工作时保留；阶段结束清理不再需要的文件。
