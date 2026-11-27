# GameBridge 验收基线

更新日期：2026-11-24

这是 GameBridge 的“保护锁清单”。新会话不得从聊天记录猜测结论，修改代码前必须以本文件和当前测试为准。

后续统一启动架构的整理想法已存档在 `docs/unified-launch-refactor-plan.md`。该文档目前只是计划，不代表已经开始替换现有启动路线。

## 结论等级

- **已真机验收**：源码、回归测试和实际安装包的真机结果一致，属于发布保护项。
- **已观察到**：真机只走到了某个阶段，只保护已观察的部分。
- **已发现故障**：真机已稳定复现失败，修复前不得宣称该功能正常。
- **自动检查**：有代码测试保护，但不能代表真游戏或真账号成功。
- **待验证**：不得宣称已完成，也不能用它推断其他平台或机器。

## 当前真机基线

测试设备：Xbox Ally X（x86_64 SteamOS 实机）

已安装包：`GameBridge-dev.zip`
安装包 SHA-256：`0985275e3f08fff8587c73222b77b08966de06bfe9fa1615bf7b39510561154c`

2026-08-28 的米哈游四款游戏复测均从 Steam 大屏幕模式的统一卡片发起。“进入用户协议或游戏首屏”只代表启动链路通过，不代表账号登录已验证。

2026-08-29 用户在同一安装包上完成四款游戏的官服、B 服和国际服完整回归，并明确确认全部通过验收。本次固化的是大屏幕启动链路、区服路由和已验收的渠道切换边界；不把未实际完成的账号登录扩大记录为通过。

2026-08-29 修复国际服原神从国服直启卡片内二次启动 Proton 的脆弱链路。选择国际服后，同一 Steam 卡片会自动切换为原生 GameBridge 路由并清空 Steam 外层兼容工具；实机自动启动后确认 `GenshinImpact.exe` 使用国际服独立 Prefix 和 DWProton 11.0-11，Steam 焦点进入游戏，屏幕显示 HoYoverse 登录页。未输入账号或验证登录。

2026-08-29 使用 `GameBridge-v0.19.0-beta.5-progress-test.zip`（SHA-256：`f101f783b8fbaae645e2086e790fc3a893410ae6a1d7de7ec08c8d77fc8228b`）完成第一轮兼容组件进度真机测试。当前海外网络由固定网关分配到官方源；移除 DWProton 后从大屏幕原神卡片触发按需准备，界面显示当前步骤、真实百分比和“官方源”，DWProton 11.0-11 下载、校验、安装及后续运行均由用户确认正常。本轮不扩大为 GE-Proton、国内源、UMU 或 Legendary 已验收。

随后使用调整为“按钮 → 进度条 → 状态与百分比 → 线路”的最新版测试包（SHA-256：`e4230117354420acbb290cf8c3ea0b133e8c2f9c6cf1790b66d7f73ec7fe9b09`）清空四个受管组件后完成海外全量复测。网关四条路由均返回官方源；原神依次安装 UMU 1.4.0 和 DWProton 11.0-11，崩坏3安装 GE-Proton 11-5，Epic 连接流程安装 Legendary 0.21.0。用户确认界面顺序和运行均正常，后台确认固定散列、可执行权限、完整解压及临时文件清理正常。本轮仍不代表中国大陆线路已验收。

2026-08-30 再次清空相同四个组件后，在中国大陆全局网络下完成同一最新版测试包的国内源全量复测。用户确认 UMU、DWProton、GE-Proton 和 Legendary 下载期间界面均显示“国内源”，进度布局和运行正常；本地安装时间连续，四项最终文件完整、可执行，DW/GE 核心文件与已验收海外副本一致，Legendary 固定 SHA-256 正确，且没有残留临时下载文件。测试结束后用户主动断开 VPN，因此 00:00:46 的最后一次离线报告显示官方源；该报告反映断开后的网络，不推翻下载时由用户确认的国内源结果。

2026-08-30 安装 `GameBridge-v0.19.0-beta.5-progress-test.zip`（SHA-256：`2447efa0280f2f445316d251b916cd6a2b14b13b35540525b1cf28ad544eb061`）后，在兼容运行环境已安装完成的状态下重新打开米哈游游戏大屏幕详情页，用户确认原生操作按钮已恢复为播放图标和“开始游戏”。“正在准备兼容运行环境”仅在实际准备期间显示，本次未改动启动路由、Prefix 或区服配置。

2026-08-30 安装常亮进度条测试包（SHA-256：`4d549ce9fe538d4a8bb3f1f4fc5d73250decc06e3ea2199db8ffbfc126c3c987`）后，将 UMU、DWProton、GE-Proton 和 Legendary 四个受管组件移出安装位置，由用户重新触发兼容运行环境下载并确认进度条在下载过程中保持清晰常亮。游戏下载进度条使用同一常亮显示规则并有自动测试保护，但本轮未重新下载游戏，不扩大为游戏下载常亮已真机验收。

2026-08-30 安装 `GameBridge-v0.19.0-beta.5-progress-test.zip`（SHA-256：`7225d310c349c6e1dc051765816e550600f444a3047ac4e8f0c6b13543febebe`）后，同时连接 `Game` 和“女神的家”两个外置存储，并临时隐藏 `Game` 盘中国服、国际服共八个游戏目录模拟未安装。用户确认米哈游启动器的目录选择页能通过全部外置存储入口看到多个分区，测试后八个游戏目录已原名恢复。本机 Prefix 测试前已存在可用的全存储盘符；全新 Prefix 自动创建 `V:`、盘符被占用时改用 `W:` 且不覆盖用户映射，目前由自动测试保护，不冒充为另一台全新 Steam Deck 已验收。

2026-08-30 安装 `GameBridge-v0.19.0-beta.5-epic-account-sync-test.zip`（SHA-256：`c7d8da2445f20521a50847541dff3aa9f92684a5ec56d1beb6776fd355367ce7`）后，从原有 20 款游戏的 Epic 账号切换到实际只有 1 款游戏的新账号。用户在大屏幕模式确认 EPIC 标签由 `20` 正确变为 `1`。本次只验收当前账号目录替换和数量刷新；不把另一账号的 `PRIVACY_POLICY_ACCEPTANCE` 处理路线记为通过。不删除已安装游戏文件、Steam 快捷方式和云存档的边界由自动测试保护，本轮未单独对这三项做真机删除性复核。

2026-08-30 在一台曾稳定出现“Epic 登录成功但标签为 0、手动同步失败”的 Steam Deck 上，日志确认 `legendary list --json` 返回的游戏库资料超过原有 4 MiB 通用输出上限。安装 `GameBridge-v0.19.0-beta.5-epic-128mb-library-test.zip`（SHA-256：`99f502b2a0482bd52194fc8e57e9fc84705131d7a372e865c30191fa7f1f384b`）后，用户确认 Epic 游戏库同步通过。本次验收 Epic 游戏库单条命令的 128 MiB 有界容量、手动同步和数量刷新；其他外部命令仍保持 4 MiB 通用上限。本次不扩大为该机的 Epic 隐私协议处理路线已通过。

Steam Deck 的真机结论需要单独记录，不得直接继承 Xbox Ally X 的验收结论。

| 平台 / 功能 | 等级 | 已验证边界 | 保护要求 |
| --- | --- | --- | --- |
| beta5 四组件按需下载进度（海外官方源） | 已真机验收 | Xbox Ally X + SteamOS；UMU、DWProton、GE-Proton、Legendary 均从固定网关分配到官方源，界面按“进度条 → 状态与百分比 → 线路”显示，下载、校验、安装及后续运行正常 | 保持只下载当前流程所需组件和固定散列校验；中国大陆线路的独立验收边界见下一项 |
| beta5 四组件按需下载进度（中国大陆国内源） | 已真机验收 | Xbox Ally X + SteamOS，中国大陆全局网络；UMU、DWProton、GE-Proton、Legendary 下载期间均显示国内源，布局、下载、校验、安装及后续运行正常，结束后无临时残包 | 保护固定网关的大陆分流、百度直链主机校验、真实进度和最终散列校验；测试结束后断开 VPN 产生的官方源报告不得误写成下载线路 |
| 米哈游兼容层就绪后的原生开始按钮 | 已真机验收 | Xbox Ally X + SteamOS 大屏幕模式；兼容环境已就绪时显示 Steam 原生播放图标与“开始游戏” | 不得把就绪状态重新显示为下载图标或“启动米哈游”；实际准备期间仍须显示准备状态 |
| 兼容层下载进度条常亮 | 已真机验收 | Xbox Ally X + SteamOS；清空四个受管组件后重新触发下载，用户确认进度条全程保持清晰亮色 | 下载及暂停状态不得因按钮失焦或父级样式而压暗；游戏下载常亮目前仅有自动保护，待下次实际下载游戏时补真机验收 |
| 米哈游多外置分区可见 | 已真机验收 | Xbox Ally X + SteamOS；`Game` 和“女神的家”同时连接，隐藏八个游戏本体后，米哈游启动器目录页可通过全存储入口看到多个分区；测试后游戏已恢复 | 保留 `G:` 的首选盘真实容量，并保留 `/run/media` 的全用户、全分区入口；不覆盖用户已有盘符。另一台全新 Steam Deck 仍需单独验收自动创建行为 |
| 米哈游四款 × 官服 / B 服 / 国际服完整回归 | 已真机验收 | 2026-08-29 从 Steam 大屏幕模式完成原神、崩坏3、星穹铁道、绝区零的官服、B 服和国际服回归，用户明确确认全部通过验收 | 任何发布前必须保持四款游戏、三类服务器的路由、Prefix、运行时和渠道配置隔离；修改共用链路时必须整组回归 |
| 米哈游国际服四款 + LSFG（小黄鸭） | 已真机验收 | 2026-08-29 用户确认国际服崩坏3、星穹铁道和绝区零使用小黄鸭均通过；国际服原神修复为原生 GameBridge 路由后，自动复测确认 LSFG 创建交换链、Steam 聚焦游戏并完整显示 HoYoverse 登录页。未输入账号 | 小黄鸭必须围绕真实游戏进程生效，保持四款国际服各自的 Prefix 和运行时隔离；不得把通过范围扩大为尚未复测的官服/B 服或 DeckyFG 组合模式 |
| Epic 账号连接 | 已真机验收 | 2026-08-29 用户确认当前安装包的 Epic 账号流程已经通过，可以完成连接并正常使用账号状态 | 保护官方登录流程和本地凭据隔离 |
| Epic 退出账号 → 重新登录 | 已真机验收 | 2026-08-29 用户明确确认 Epic 退出账号和重新登录流程已通过 | 保护退出后本地授权状态刷新和重新授权链路；本项不扩大为浏览器所有 Cookie 必须全部清除 |
| Epic 游戏下载与安装 | 已真机验收 | 2026-08-29 用户确认当前安装包的 Epic 游戏下载流程已经通过，下载后可以正常完成安装 | 保护 Legendary 下载、安装进度和安装记录；不得把本项扩大为尚未单独确认的更新、取消、断点恢复或卸载 |
| Epic 游戏卸载 | 已真机验收 | 2026-08-29 用户明确确认 Epic 游戏卸载真机测试通过 | 只能删除用户确认卸载的目标游戏和对应安装记录，不得扩大到其他 Epic 游戏、米哈游游戏或其他存储路径 |
| Epic 启动参数与 LSFG（小黄鸭）组合 | 已真机验收 | 2026-08-29 用户明确确认 Epic 启动参数、小黄鸭及组合启动测试通过 | 保护用户启动参数、GameBridge 主启动命令与 LSFG 包装顺序；恢复默认时不得遗留或吞掉参数 |
| Epic 云存档下载与上传 | 已真机验收 | 2026-08-29 用户确认当前安装包的 Epic 云存档功能已经通过；此前《霍格沃茨之遗》也有真机下载与上传成功记录 | 下载或上传前继续保留本地备份和危险覆盖保护；不得把本项扩大为尚未逐项复测的断网、空存档和时间冲突边界 |
| SteamGridDB 更换封面 | 已真机验收 | 2026-08-29 用户确认当前安装包能够通过 SteamGridDB 更换 Steam 游戏卡片封面，实际显示结果正常 | 保护素材查找、下载、写入和 Steam 卡片刷新链路；不得把本项扩大为尚未单独确认的全部素材类型、API Key 初次配置或网络异常恢复 |
| SteamGridDB 其他素材与网络异常 | 已真机验收 | 2026-08-29 用户明确确认除封面外的其他 SteamGridDB 素材流程和网络异常处理已通过 | 保护已验证的其他素材查找、下载、写入与失败回退；异常时不得覆盖已有素材或破坏 Steam 卡片。本记录未拆分每种素材和每个网络错误码，不对未出现过的新异常做扩大承诺 |
| Epic 首次同步后的标签数量刷新 | 已真机验收 | 2026-08-30，曾稳定出现 `EPIC 0` 的 Steam Deck；日志定位为 Epic 游戏库资料超过 4 MiB，安装 128 MiB 有界容量测试包后，用户确认手动同步通过 | 保留 Epic 游戏库专用 128 MiB 有界容量、同步结果显示、后端开始/成功/失败日志与前端缓存刷新；其他命令不得因此取消通用安全上限 |
| Epic 切换账号后的游戏库替换 | 已真机验收 | 2026-08-30 Xbox Ally X + SteamOS 大屏幕模式；新账号实际为 1 款，原账号缓存为 20 款，安装新包后 EPIC 标签正确由 `20` 变为 `1` | Epic 成功同步后必须以当前账号权益库替换旧账号目录；不得借此删除已安装游戏、Steam 快捷方式或云存档。本项不代表全新机器的 `EPIC 0` 问题已验收 |
| 彻底清理后米哈游首次定位 | 已真机验收 | 2026-08-29 Xbox Ally X + SteamOS：游戏本体保留在 Game 盘，GameBridge 状态彻底清空后，复现原神含旧 B 服 SDK 残留、星铁/绝区零仍为 `channel=14` 导致新启动器拒绝定位。修复后四款主程序仍在，三款渠道资料已备份并恢复官服定位状态；用户重试后确认当前问题已无碍并明确要求上锁 | 保护从已验证官方启动器旁自动发现游戏的逻辑；定位前必须先备份 B 服配置与 SDK，再恢复官服状态，不得删除或移动游戏本体。本项不代表 Steam Deck 或其他目录布局已真机验收 |
| 国服原神首次 DWProton 准备与重启提示 | 已真机验收 | 临时撤掉 DWProton 和旧原神卡片后，首次打开会自动重新准备运行时，完成后明确提示只需重启一次 Steam；重启后四款三服回归全部通过 | 不得在 Steam 尚未识别新 DWProton 时直接启动；提示只在运行时刚安装但当前 Steam 尚不可见时出现 |
| 绝区零国服启动 | 已真机验收 | 通过统一快捷方式启动，越过黑屏阶段并进入官服登录界面 | `nap_cn` 继续使用 UMU + 米哈游 CN 共享 Prefix，不得悄悄切回独立卡片 Prefix |
| 绝区零 B 服启动 | 已真机验收 | 自动准备官方 B 服 SDK，启动 Bilibili 登录组件 | 保留官方 SDK 下载、完整性检查和渠道配置隔离 |
| 绝区零官服 → B 服 → 官服 | 已真机验收 | 两次切换后官服 `config.ini` 恢复为原始内容，Steam 入口不变 | 共用游戏本体，渠道组件不得串用，返回官服不得依赖网络 |
| 星穹铁道 B 服启动 | 已真机验收 | 复测可启动至“用户协议和隐私政策”页面，并纳入 2026-08-29 完整回归；未代替用户同意协议，未扩大宣称账号登录 | 保护 B 服配置应用和游戏启动，不得宣称未实际验证的账号登录 |
| 星穹铁道返回官服 | 已真机验收 | 返回后配置散列与切换前相同，B 服组件不再运行，官服也可重新启动至协议页，并纳入 2026-08-29 完整回归 | 官服回退必须可离线使用已保存的本地配置 |
| 崩坏3启动 | 已真机验收 | 官服和 B 服选择下都能启动同一 PC 客户端；2026-08-29 完整回归再次确认通过；未代替用户扫码或登录 | B 服保持同客户端扫码路线，不得宣称未实际验证的 B 站账号登录 |
| 原神国服启动 | 已真机验收 | 7.0.0 从 Steam 专用快捷方式直接启动 `YuanShen.exe`，使用 DWProton 11.0-11 和专用超时修复，进入“用户协议和隐私政策”页面，未再产生新的 `[4,643,0]` 报错 | `hk4e_cn` 必须保持 Steam 直启路线、专用超时参数和 DWProton 自动选择；不得悄悄切回统一 UMU 路由 |
| 原神 B 服启动 | 已真机验收 | 启动前自动把 B 服 `config.ini` 和 72 个官方 B 服 SDK 组件完整应用到游戏目录，文件逐个校验一致，并纳入 2026-08-29 完整回归；未代替用户同意协议，未扩大宣称 B 站账号登录 | 保护启动前自动渠道切换和 SDK 完整性；不得宣称未实际验证的 B 站登录 |
| 原神官服 → B 服 → 官服 | 已真机验收 | 同一 Steam 入口连续启动三次；B 服启动前配置散列准确切换，返回官服后 `config.ini` 恢复为切换前的完全相同散列，官服再次进入协议页 | 官服本地备份必须可离线恢复，渠道组件不得串用，Steam 入口不得因切服变化 |
| 国际服原神 | 已真机验收 | 国际服 7.0.0 从大屏幕统一卡片启动，实际运行 `GenshinImpact.exe`；2026-08-29 修复后再次进入 HoYoverse 登录页。国际服选择会让同一卡片自动改用原生 GameBridge 路由，Steam 外层兼容工具为空；未输入账号 | 保护统一卡片、自动入口切换、DWProton 11.0-11 和 `hoyoplay-global/hk4e_global` 独立 Prefix；国际服不得再从国服 DWProton 外壳内二次启动 |
| 国际服星穹铁道 | 已真机验收 | 国际服 4.5.0 从大屏幕统一卡片启动 `StarRail.exe`，显示列车加载画面；同一修复包的前一次复测已进入 HoYoverse 登录页 | 保护 DWProton 11.0-11 和 `hoyoplay-global/hkrpg_global` 独立 Prefix；不得仅以后台进程作为通过依据 |
| 国际服绝区零 | 已真机验收 | 国际服 3.1.0 从大屏幕统一卡片启动 `ZenlessZoneZero.exe`，越过黑屏并进入 HoYoverse 登录页 | 保护 DWProton 11.0-11 和 `hoyoplay-global/nap_global` 独立 Prefix；不得恢复四游戏共用 Prefix |
| 国际服崩坏3 | 已真机验收 | 国际服 9.0.0 从大屏幕统一卡片启动 `BH3.exe`，自动发现 Game 盘的 Valve `Proton Hotfix`，进入游戏内“资源下载”选择页，未再产生新的 `[4,643,0]` 错误 | 国际服 9.0 只使用任意已挂载 Steam 库中的 Proton Hotfix，保留 `hoyoplay-global/bh3_global` 独立 Prefix；缺失时由 Steam 自动补装；国服 / B 服仍使用已验证的 GE-Proton 路线 |

2026-11-24 在一台 aarch64 掌机（Armada 20261116.2fc282e，Steam 原生 arm64、Decky 等价 PluginLoader 以 x86_64 经 FEX 运行插件后端）上定位 Epic 登录卡在“正在连接下载线路…”的原因：固定下载网关的 `/download/legendary`、`/download/umu`、`/download/dw`、`/download/ge` 四条路由当时全部返回 502（`{"ok":false,"error":"Download route temporarily unavailable"}`），而 x86_64 构建的受管组件只有网关单条线路、没有备用线路，安装在 connecting 阶段抛错，前端因此从未打开 Epic 登录页。该设备 `providers/epic/tools/` 为空、`compatibility/tools/` 为空，与这一结论一致。

同一设备上确认Legendary 的 x86_64 构建在 FEX 下无法加载自带原生依赖（`Cryptodome.Util._cpuid_c` 要求 `cpython-314-aarch64-linux-gnu.so`），`legendary list` 与 `legendary status --json` 直接失败；原生 aarch64 构建在同一最小环境下正常，`status --offline --json` 报告已登录，`list --json` 返回 352 款。修复按 `uname -m` 的子进程架构选择 Legendary 构建，兼容层仍保持 x86_64 构建。

更正（2026-11-24 晚）：先前把该设备的 Legendary 问题归因为“FEX 不会把模拟延伸到子进程的原生模块，所以要按 `uname -m` 选 aarch64 构建”是错的。对照实验结果：`FEXBash -c uname -m` 返回 x86_64；同一个 aarch64 版 Legendary 从原生 shell 运行成功（退出码 0），从 `FEXBash` 下运行必定失败，报 `Cannot load native module 'Cryptodome.Util._cpuid_c'` 并要求 `cpython-314-x86_64-linux-gnu.so`。也就是说插件宿主处于 FEX 翻译树时，它 exec 出来的子进程同样以 x86_64 身份运行，托管路径需要的是 x86_64 构建；`child_architecture()` 用 `uname -m` 子进程探测在本机确实返回 x86_64，与 `platform.machine()` 结果一致，所以 beta.6 的架构选择在真机上没有改变任何行为。把 aarch64 构建放进 `providers/epic/tools/legendary` 是我手工调试留下的状态。另一个真实故障源是 `cache/legendary/vendored` 这个解压缓存不区分架构：同一个构建被原生 shell（aarch64 解释器）和宿主（x86_64 解释器）交替使用时，两边互相要求对方架构的 `.so`，表现为“另一个架构的原生模块加载不了”。2026-11-24 19:38 设备状态：托管 Legendary 使用 x86_64 固定构建（SHA-256 `c83d1595a9e2cbae4e66b69ecaa1f8649da99b617a72f93312d342e6a5a799c7`，14,022,624 字节），`GameBridge-v0.19.0-beta.9.zip`（SHA-256 `1ff012c347552b9db596617b272593ce5c5bc4fea3330b95894ff42f9690aed4`）完整装入该设备，安装后文件清单与包内一致，宿主日志显示 `Loaded GameBridge (v0.19.0-beta.9)` 与 `GameBridge backend ready`。

测得的机制（推翻本轮早前的两次误判）：插件的 Epic 数据根是 `data/providers/epic`，解压缓存是 `data/providers/epic/cache/legendary/vendored`，其中 `.so` 的架构跟随已安装的构建包；插件宿主处于 FEX 翻译态时它派生的子进程同样在 x86_64 翻译态运行（解释器索要 `_cpuid_c.cpython-314-x86_64-linux-gnu.so`），所以更换构建必须同时删除该缓存，否则报 `Cannot load native module`。`uname -m` 在该场景返回 x86_64，`child_architecture()` 选择 x86_64 构建是正确的；18:11、19:06、19:18、19:20 的 `storage_locations` 失败都来自手工放置的 aarch64 构建与残留缓存。Epic 登录凭证文件是 `data/providers/epic/config/legendary/user.json`（15:08 起存在，账号有效），此前“登录态已被清除”的判断来自把探针指向 `data/config/legendary` 这个由探针自身创建的目录，该结论作废，探针创建的 `data/config/legendary` 与 `data/cache/legendary` 已删除。

2026-11-24 19:25–19:34 在同一设备完成 Epic 游戏安装链路真机验证：Brotato（`e8bbb84be35640cda646233152ff3428`）读取安装体积、列出存储位置、选择内部存储后开始下载，任务状态从 `downloading_game` 到 `completed`，进度到达 1.0，下载 267.56 MiB，安装目录 `/var/home/armada/Games/GameBridge/Epic/Brotato` 325 MB（`Brotato.exe`、`Brotato.pck`、EOS 运行库），`installed.json` 记录安装路径，Steam 库 352 条 Epic 记录中 1 条为已安装并拿到 Steam app id `3060452607`。这是在 aarch64 掌机 + FEX 模拟 x86_64 插件宿主的设备类别上完成的结果。Epic 游戏的启动、更新、断点恢复与外置存储安装仍未真机验证。期间发现的“下载进行中打开安装位置被通用 30 秒超时打断”已在 beta.9 改为独立的 90 秒有界窗口，该修复本身待下一次安装时真机复验。

以上修复以源码文件同步方式装入设备上的 GameBridge-v0.19.0-beta.5（SHA-256：`27df8318ee893b462a6cb4458f56a58d71868e5d214f5245df26b39f16e7d416`）插件目录后复测：用户在大屏幕中完成 Epic 登录，插件保存会话并显示“已连接”，`connection_status` 与 `library()` 通过插件自身代码路径返回 352 款（8.1 秒），`sync_provider_library("epic")` 返回 352 款耗时 45.7 秒，`steam_library_games()` 返回 352 条 Epic 记录耗时 0.4 秒；此前 Epic 标签显示 0，是登录成功后的首次库同步被通用 30 秒命令超时打断，数据库从未写入 Epic 记录。该结果当时来自手工文件同步，因此先记录为“已观察到”。随后 `GameBridge-v0.19.0-beta.6.zip`（SHA-256：`d756d1feca32424658e505cbfcc9bbd8248b3232a2a03575296ace886310de0f`）按 `scripts/build_plugin_zip.py` 生成并完整装入该设备，安装后文件清单与包内一致，宿主日志显示 `Loaded GameBridge (v0.19.0-beta.6)` 与 `GameBridge backend ready`，通过安装包内的代码路径确认 Epic 已连接、库内 352 条 Epic 记录仍在；2026-11-24 用户在该设备大屏幕上确认 EPIC 标签显示 352 款，Epic 卡片同时显示“已连接”。但同日复查发现该设备上的托管 Legendary 当时被手工换成 aarch64 构建，插件宿主发起的 Legendary 调用在该状态下全部失败（宿主日志计数：`storage_locations` 9 次、`automatic_epic_login` 3 次、`install_provider_tool` 2 次、`sync_provider_library` 1 次、`get_dashboard` 1 次），卡片上的“已连接”来自缓存登录状态而不是实时查询，352 条记录来自手工在原生 shell 里跑同步的结果。因此本项保持“已观察到”：界面显示与数据库记录一致已被确认，宿主侧 Epic 连接、库同步与安装入口需要在恢复 x86_64 构建后重新验收；Epic 游戏的下载、更新、启动，以及 aarch64 主机上 FEX 与 x86_64 兼容层的组合同样仍待真机验证。

`GameBridge-v0.19.0-beta.7` 处理了同轮记录的两个问题：`SteamBrowserAuthorization` 只有在 Steam 内嵌浏览器读不到页面正文时才使用会话 cookie 回退，用户仍在 Epic 登录页输入凭据时不再每 0.3 秒重放 Epic 授权接口；Epic 已发出授权码但首次游戏库同步失败或过慢时登录不再整体失败，改返回已连接并提示游戏库待同步；前端 Epic 登录等待窗口由 360 秒提高到 480 秒，覆盖等待授权码、Legendary 交换令牌和首次大库同步的总时长。`GameBridge-v0.19.0-beta.7.zip`（SHA-256：`641754b934865b65720e7ca3e7b7f46b4f6df762fcdbbecbf5ee0b0318732569`）按 `scripts/build_plugin_zip.py` 生成并完整装入该设备，安装后文件清单与包内一致，宿主日志显示 `Loaded GameBridge (v0.19.0-beta.7)` 与 `GameBridge backend ready`，Epic 仍报告已连接、库内 352 条 Epic 记录保持不变。这三条登录链路改动本身需要在用户重新登录时才能复验，目前保持“自动检查”等级，暂不提升验收等级。该设备上的 steamwebhelper 与 PluginLoader 各崩溃过一次（steamwebhelper SIGTRAP 转储核心、PluginLoader `concurrent map writes` / `unknown caller pc`），崩溃时前端同样表现为“后端响应超时”。

2026-11-24 21:47-21:52 在同一台 aarch64 掌机（Armada，Steam 原生 arm64、PluginLoader 以 x86_64 经 FEX 运行插件后端）上定位 Epic 游戏「安装完成但从 Steam 启动失败」。`GameBridge-v0.19.0-beta.12.zip`（SHA-256 `b424a256f1d0d7aae18dc57af3ad2693d11f40ae4f519526d85f765ec5429ead`）由 `scripts/build_plugin_zip.py` 生成并完整装入该设备，安装后文件清单与包内一致，宿主日志出现 `Loaded GameBridge (v0.19.0-beta.12)` 与 `GameBridge backend ready`。

根因：同一个 `providers/epic/tools/legendary` 被两种执行上下文共用。插件宿主（x86_64 经 FEX 翻译）派生的子进程处于翻译态，需要 x86_64 构建；Steam 直接启动的 `gamebridge/launcher.py` 是主机原生 aarch64，调用同一文件时解释器索要 `_cpuid_c.cpython-314-aarch64-linux-gnu.so`，`legendary launch --json` 退出码 1，日志只剩 `launch plan failed 1`。两者还共用 `cache/legendary/vendored` 这一个解压目录，交替使用时互相要求对方架构的 `.so`。同一原因让同一次启动里的 `cloud download` 抛 RuntimeError。

在模拟宿主内读取系统二进制判定架构同样不可靠：FEX 根文件系统使 `native_architecture()` 在宿主内也返回 x86_64（原生 shell 下测得 `native: aarch64 / child: aarch64`，宿主内两者都是 x86_64），插件宿主无法自行推断游戏客户端的架构。修正为：Steam 启动的原生 launcher 把自身架构写入 `providers/epic/launch-architecture.txt`，宿主读取这个回报值决定是否补装 `tools/legendary-<架构>`；每个 Legendary 构建使用各自的解压目录（宿主仍用 `cache/`，其它构建用 `cache/variants/<架构>/`），`clear_cli_bundle_cache()` 一并清理。

设备实测（该次为按发布流程生成的安装包内代码路径）：先删除手工放置的 `tools/legendary-aarch64` 与残留缓存，原生 launcher 记录 `aarch64` 并报 `launch plan failed 1 cli=legendary reason=cli_architecture_mismatch`；重启插件宿主后宿主日志出现 `Epic CLI installed for the game client architecture path=…/providers/epic/tools/legendary-aarch64 version=0.21.0`，落盘文件 SHA-256 `ed0a523c7310aec590a0da9ecdada185fc3b02e75fa5148c0e7ef0680095dce5`，与 aarch64 固定发布一致（该构建没有国内网关线路，由设备直连 GitHub 取回）；再用 Steam 的实际调用方式复现（工作目录为插件根，`/usr/libexec/armada/armada-game-launch /usr/bin/python3 gamebridge/launcher.py --provider epic --game-id e8bbb84be35640cda646233152ff3428`），launcher 选中 `cli=legendary-aarch64 arch=aarch64`，不再出现 `launch plan failed`，`cloud download` 返回 `unchanged`，链路进入 umu-launcher 1.4.0 并开始拉取 `steamrt4-arm64` 运行时（本次 120 秒观察窗口内被中断，`providers/epic/.local/share/umu/steamrt4-arm64` 当时为空目录）。`cache/legendary` 与 `cache/variants/aarch64` 同时存在，说明两条上下文已隔离。Epic 游戏从 Steam 卡片「开始游戏」进入游戏仍未确认，本项保持「已观察到」，Steam 侧启动与兼容层运行时首次拉取待用户在该设备复验。

2026-11-24 22:42-23:07 同一台 aarch64 掌机（Armada，Steam 原生 arm64、插件宿主 x86_64 经 FEX）上继续 Epic 启动链路。`GameBridge-v0.19.0-beta.13.zip`（SHA-256 `b0ee145cfc79e537a0686afd959b582cec4ebc3a7870fe1559767b673b0b44e0`）与 `GameBridge-v0.19.0-beta.14.zip`（SHA-256 `f088271e797e483a7bff588dee91cc0583276a9759296e73020b65fb36ce99e2`）按 `scripts/build_plugin_zip.py` 生成并完整装入该设备，安装后文件清单与包内一致，宿主日志出现 `Loaded GameBridge (v0.19.0-beta.14)` 与 `GameBridge backend ready`。

测得的机制：Steam 对 GameBridge 创建的非商店快捷方式给出的环境里没有 `SteamLaunchId`（`SteamAppId`、`SteamClientLaunch`、`Steam3Master` 等仍在），而该 Proton 版本的 `c:\windows\system32\steam.exe` 引导器无条件运行（脚本 2137-2175 行的 `waitforexitandrun` 与 `run` 都走它），引导器向客户端查询本次启动状态失败即弹出 `Assertion failed!`、`File: ...\src\issteamclient\steamclient_main.c`、`Line: 375`、`Expression: "status"`。对照实验：把抓到的同一份环境变量与同一串命令行从原生 shell 直接喂给同一个 `proton run`，Brotato 正常启动，说明断言只在 Steam 自己拉起的进程树里出现。

改动与结果：beta.13 把 Epic 的兼容层入口从托管 umu 换成直接调用客户端自带 Proton，日志新增 `runtime route=client layer=<名称>`，同时不再需要 umu 自行下载的 467 MB `steamrt4-arm64` 运行时与第二层容器。beta.14 从 Epic 游戏环境中移除 Steam 客户端会话身份（`SteamAppId`、`SteamAppUser`、`SteamClientLaunch`、`Steam3Master`、`SteamOverlayGameId`、`SteamTenfoot`、`SteamUser`），保留 `SteamGameId`，因为该镜像的 Proton 用它匹配每应用翻译配置。两次改动后启动确实进入 Proton 与 DXVK：设备启动日志出现 `[Gamescope WSI] pEngineName: DXVK`、`xalia.exe`、`explorer.exe`、`fsync: up and running`，22:04 那次游戏进程运行约 33 秒后以退出码 3 结束（日志 `exit 3`），22:06 那次仍回到同一个断言对话框，结果不稳定。

在该镜像上跳过 Proton 脚本直接调用其 `files/bin-arm64/wine` 不可行：缺少 Proton 注入的运行时环境，Wine 进程无法启动（同一环境下直接执行该 wine 二进制，20/40/60/90 秒四次采样都没有游戏进程）。

结论：Epic 游戏启动在这一设备类别上仍记为「未通过真机验收」（该结论已被下方 2026-11-24 23:34-23:39 的 beta.15 记录取代）。GameBridge 自身的两处问题已经消除：架构错配导致的 `launch plan failed`（beta.12）、以及多余的运行时容器层级（beta.13/14）。剩余失败发生在设备镜像自带的 Proton Experimental (ARM64) 引导器与其 Gamescope WSI、xalia、Epic Online Services 组合上，需要单独一轮针对该 Proton 构建的排查。Epic 的下载与安装在该设备类别上的结果保持不变（已真机完成）。

发布基线包变更：本工作副本是 2026-11-24 从 `github.com/leioukupo/GameBridge` 新克隆，`releases/GameBridge-v0.19.0-beta.4.zip`（原锁定 SHA-256 `b8ab2de76f7fee0c511e99b24914032bc9e7f71aa4093dd2367092ed6059c9f7`）在本机与其它主机均已找不到。用户要求发布 release，无法恢复该历史基线包，本次将 `docs/protected-baseline.json` 的 `releaseArchive`/`releaseSha256` （改动已向用户说明）改为记录设备上实际在用、SHA-256 已核对的 `releases/GameBridge-v0.19.0-beta.5.zip`（`27df8318ee893b462a6cb4458f56a58d71868e5d214f5245df26b39f16e7d416`），`gitCommit` 仍是 beta4 锚点，Git 祖先校验和全部已锁测试保持不变。

2026-11-24 23:34-23:39 在同一台 aarch64 掌机（Armada，Steam 原生 arm64、插件宿主 x86_64 经 FEX 运行插件后端）上完成 Epic 游戏从 Steam 启动的真机验收。`GameBridge-v0.19.0-beta.15.zip`（SHA-256 `12a8327fc4294cd929336edd13d67eb4d3b0cf89525acff9ae847b23978a73cc`）由 `scripts/build_plugin_zip.py` 生成并完整装入该设备，安装后文件清单与包内逐文件一致（`IDENTICAL`），宿主日志出现 `Loaded GameBridge (v0.19.0-beta.15)` 与 `GameBridge backend ready`。

补完的根因：该 Proton 构建的 `c:\windows\system32\steam.exe` 引导器用 `SteamGameId` 拼出 `steam://launch/<id>`，把本次启动交接给正在运行的 Steam 客户端，并对客户端返回的状态断言。二进制内的相关字符串是 `SteamGameId`、`steam://launch/%s`、` to native steam failed, status %#lx.`，断言点为 `src/issteamclient/steamclient_main.c:375`、`Expression: "status"`。GameBridge 创建的 Epic 快捷方式在客户端没有本次启动记录，交接必然失败，游戏进程还没创建就弹断言框。beta.14 去掉的是会话身份，没有去掉引导器用来命名本次会话的 `SteamGameId`，所以现象保持不变。

改动范围：只有 Epic 走客户端自带 Proton 的路线（`runtime route=client`）会额外去掉 `SteamGameId`、`SteamExe`、`SteamPipe`、`SteamLaunchId`、`SteamPID`；GameBridge 自行下载的 GE-Proton、DWProton 继续走托管 umu 入口，环境保持 beta.14 验收时的样子。Proton 脚本自身按 `SteamGameId` 匹配的每应用配置只覆盖 Valve 收录的商店应用编号，Epic 快捷方式编号在其中没有任何命中，去掉后不损失该镜像的默认翻译与 FEX 配置。设备实测该快捷方式的环境里只有 `SteamGameId` 存在，启动日志新增 `proton bootstrapper handoff removed SteamGameId`。

设备实测（按发布流程生成的安装包内代码路径）：通过 Steam 自身的启动入口触发，即 `/usr/bin/steam steam://launch/<快捷方式 appid>`，客户端已在运行并转发该命令行，与在卡片上点「开始游戏」是同一条启动链。launcher 记录 `runtime route=client layer=Proton Experimental (ARM64)` 与上面的 handoff 移除行；此后 45/70/95/120/145 秒五次采样都是 `Brotato.exe` 3 个进程、wine 1 个进程，不再出现 `Assertion failed!` 对话框，用户确认掌机进入游戏画面并可正常游玩。引导用的 `steam.exe` 进程在交接后不再常驻（同一采样里 `bootstrap=0`）。同一会话在 23:42 正常退出，启动日志记录 `cloud upload … uploaded` 与 `exit 0`：存档上传这一次确实发生了（不是 beta.12/14 那样的 `unchanged`），退出码 0 说明 Steam 侧看到的是一次完整结束的游戏会话。

结论：Epic 游戏从 Steam「开始游戏」进入游戏画面，在这一 aarch64 设备类别上为「已真机验收」。此前记录的架构错配（beta.12）、多余运行时容器层级（beta.13/14）与 Proton 引导器交接断言（beta.15）三个问题均已消除。

2026-11-25 00:20-00:58 在同一台 aarch64 掌机（Armada，Steam 原生 arm64、插件宿主 x86_64 经 FEX 运行插件后端）上定位「正在下载一款 Epic 游戏时，再下载另一款会报 Python 异常；已安装的游戏变成找不到安装」。

测得的机制（设备宿主日志 + 同机现场复现）：

- 下载进行中打开另一款的安装对话框，宿主日志反复出现 `Method storage_locations of plugin GameBridge failed ... Exception: epic.cli_failed`，其中一次是 `command timed out after 90s`，即 90 秒有界窗口内没有等到 Epic 的应答。
- 在同一台设备、同一份 Epic 配置下直接调用同一个 aarch64 Legendary 构建做同一件事（`info <游戏编号> --json`）：返回码 1，stderr 末段是 `requests.exceptions.ReadTimeout`。下载占满链路时 Epic 的元数据请求会超时，这与插件无关，属于外部条件。
- 体积查询失败会让整个对话框判失败：`enough_space` 全为假、安装按钮禁用，而存储位置与剩余空间只是本地 `statvfs` 读数，不需要网络。
- 界面显示的是后端异常原文。PluginLoader 把失败包成 `Exception: <代码>`，语言表按裸代码匹配，因此 `epic.cli_failed` 没被翻译。
- 两个 Legendary 安装并跑会互相抹掉安装记录：`installed.json` 是每个 Legendary 结束时整份重写，后写完的会覆盖前一个的条目。`install.py` 里已有「Legendary exited without registering the installation; a previous download process may still be shutting down」的检测，指向同一根因。设备侧观察到某款游戏有 Steam 快捷方式但没有安装记录，launcher 当时只写了一行 `prepare failed: ‘<游戏编号>’`（KeyError 文本）。

改动：存储位置列表与体积查询解耦（体积读不到时仍列出可写入位置、显示剩余空间、允许开始安装，`sizes_available=false` + `sizes_reason` 说明原因）；上一次成功的体积按游戏缓存在 `providers/epic/cache/install-sizes.json`，失败时回退；同一时间只允许一款 Epic 下载占位（含已暂停，其写入进程只是被挂起；下载失败的任务不占位），第二款的安装请求给出 `install.another_running` 并提示等完成或取消；安装成功后把本次开始前记录在案、结束后却消失且文件仍在磁盘上的安装项写回 `installed.json`；前端先剥掉 `Exception:` 前缀再查语言表；launcher 找不到安装记录时写 `launch <游戏编号> not installed`。

状态：`GameBridge-v0.19.0-beta.16.zip`（SHA-256 `a56c32455a91487080476f8012db70785c77c6ed942a9df49f82467cb80d3317`）由 `scripts/build_plugin_zip.py` 生成并完整装入该设备，安装后逐文件清单与包内一致，宿主日志出现 `Loaded GameBridge (v0.19.0-beta.16)` 与 `GameBridge backend ready`。下载进行中打开另一款对话框的实际界面结果、以及占位规则的真机表现待用户在设备上点一次确认，本轮只到「已装入安装包 + 自动检查通过」。升级重启插件宿主会打断进行中的下载：该设备上任务 `2dc25e07aa624edf9ff132c09ce23a7c` 停在 `paused` 21.9%，需要在任务卡片上继续；断点续传路径本身仍未做过真机验收。

自动保护新增 8 条锁定测试：体积成功答案写缓存并在失败时回退、无缓存时仍返回稳定代码、体积不可读时仍列存储位置且不禁用安装、已有下载时第二款被拒、暂停中的下载同样占位、下载失败的任务不占位、安装记录被抹掉后回写、记录完整时不改写，以及安装对话框按 `sizes_available` 放行的界面合同。

2026-11-27 定位「`plugin_loader.service` 下有很多 `legendary` python 进程，负载约 4.8，Wi-Fi 与 CPU 被吃满」。

设备上的机制证据（2026-11-25 00:20-00:49 同一台 aarch64 掌机，当时只有一个 Epic 安装在跑）：`pgrep -cf tools/legendary` 计到 21，进程列表里除安装主进程外还有多个 `multiprocessing.forkserver` 进程，argv 中同样带 `providers/epic/tools/legendary` 路径。GameBridge 的 `SafeProcessRunner` 超时分支只 `process.kill()` 直接子进程，Legendary 自己 fork 出来的 worker 不属于被杀范围，会存活并保持已建立的连接；调用被重试时每次再加一组，这就是堆积的来源。Epic 云存档的 `subprocess.run(timeout=…)` 同样只处理直接子进程。

改动：`SafeProcessRunner` 用 `start_new_session=True` 让命令自成进程组，超时与 `asyncio.CancelledError` 都按进程组收尾（TERM、CONT，3 秒后 KILL）；`EpicProvider` 增加进程内互斥，同一账号的 Legendary 命令一次只跑一个，20 秒内拿不到锁返回 `epic.cli_busy`（已加本地化文案）；并发的游戏库请求共用同一个 `legendary list` 任务，不再各自起一次冷启动；`EpicCloudSaveManager` 的两处 Legendary 调用改为按进程组收尾并沿用原有 `TimeoutExpired` 语义。

状态：本轮只有自动检查。新增 6 条锁定测试（超时与取消都要带走 worker、云存档超时带走 worker、库请求合并、Legendary 不并行、排队超时返回 `epic.cli_busy`），Python 回归、类型检查与前端构建全部通过。测试设备离线，进程堆积是否消失、以及 `epic.cli_busy` 的实际界面表现均未做真机验证，保持「待验证」。

## 自动保护基线

下列部分必须继续通过 Python 测试、TypeScript 类型检查和前端构建：

- Provider 安装检测、游戏路径保留和外置存储未连接状态。
- 受管组件下载在网关失败或返回错误内容时按同一固定散列回退官方源；全部线路失败时明确报错并清理临时文件。
- Legendary 构建按 `uname -m` 报告的子进程架构选择，x86_64 兼容层选择保持不变；换架构安装时清理 Legendary 解压缓存。
- Epic 游戏库命令使用独立的有界执行窗口与输出上限。
- Epic 安装体积查询使用独立的有界执行窗口；外部命令失败时保留输出末尾而非开头。
- Epic 走客户端自带 Proton 时不把启动交接回 Steam 客户端（引导器的 `SteamGameId`、`SteamExe`、`SteamPipe`、`SteamLaunchId`、`SteamPID` 已从游戏环境移除），托管 umu 路线的游戏环境保持原样。
- Steam 浏览器只有在读不到 Epic 页面正文时才使用会话 cookie 回退；登录页正文可读时不再重放 Epic 授权接口。
- Epic 登录在首次游戏库同步失败时仍返回已连接并给出可重试提示，前端等待窗口覆盖后端各阶段的总时长。
- 兼容层自动发现、按需准备和运行时选择。
- UMU Launcher、GE-Proton、DWProton 与 Legendary 已由自动测试保护为同一固定网关入口，并显示真实下载百分比、当前步骤及国内源/官方源。海外官方源和中国大陆国内源均已完成清空四项后的 beta5 真机验收。
- 国际服《崩坏3》缺少 Proton Hotfix 时的 Steam 官方自动补装已通过接口与代码回归检查；仍需在一台未安装 Hotfix 的干净机器上补一次完整下载验收。
- 米哈游国服、B 服和国际服路由及数据隔离。
- 彻底清理后，官方启动器旁的已有游戏自动重新发现，B 服渠道资料保存后恢复为可定位的官服状态。
- Steam 快捷方式参数、启动修饰器和恢复逻辑。
- Decky 分发 ZIP 中原神启动保护脚本的可执行权限。
- 清理范围、外置游戏保留和 Decky / 其他插件不受影响。
- UI 中的已安装状态、区服选择、错误报告和 SteamGridDB 配置合同。

运行：

```bash
python3 scripts/regression_guard.py
```

自动检查通过只能说“代码回归检查通过”，不能代替上面的真机结论。

## 待从旧版和旧验收记录补录

Epic 尚未在上表确认的更新、取消/断点恢复和外置存储边界，以及错误报告、清理器和其他已做过的功能，在没有找到对应安装包、测试日期和真机边界前，先由自动测试保护，不虚构“已真机验收”记录。
