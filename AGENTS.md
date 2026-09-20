# AGENTS.md — 本机 Linux Codex fork 维护

## 维护边界

这是 IceSpark 内使用的显示定制，不是通用 Codex 发行版。只维护恢复会话时已完成工具
不进入普通显示/raw scrollback、详情仍可查询的行为。实时工具、模型上下文、认证、
订阅与计费遵循上游。不要在 IceSpark 中解析并过滤 Codex 的终端文本。

2026-09-21 的干净基线：官方 `upstream/main` 的
`2426ed7684c87f9a627c60b54271cfed77c979df`。
分支：`fork/minimal-20260921`。
本次验证结果见 [迁移记录](maintenance/VALIDATION-20260921.md)，其中明确列出未通过的
WSL 环境快照与人工验收边界。

| 补丁 | 处理 |
| --- | --- |
| `201dedbfad`，来源 `ee481ffae9` | 唯一必需产品补丁：恢复后的已完成工具仅保留在 transcript；适配新上游的文件修改回放测试 |
| `5a7af7edef` 订阅状态修复 | 错项目需求，明确废弃，禁止再次 cherry-pick |
| 本文与 `maintenance/` | 本地维护流程，独立于产品补丁 |

旧分支只作为历史档案；升级从官方 main 建新分支，不合并旧 fork 分支。
补丁目前修改 replay、history cell、transcript projection 及对应测试。
全屏 transcript 的 compact/detail 仍遵循上游，不能把 `fullscreen_transcript=false`
理解为“隐藏所有工具”。旧历史分页、resize 后重绘也必须在验收时检查。

## 更新步骤

只构建本机 `x86_64-unknown-linux-gnu`。不做全平台依赖分析、Windows/macOS 构建、
全 TUI 套件、全 workspace 测试或 `--all-features`。只执行显示补丁直接相关测试；
不为本次更新重构不相关代码，不分析或修复无关测试报错。本文是本 fork 唯一的维护
说明；从上游更新时保留这份精简 AGENTS.md，不重新引入上游通用开发规范。

1. 确认工作区干净，记录当前分支、HEAD、`codex`、`codex-stable` 和 `codex-official`
   的真实路径。未提交内容先保留，不能 reset。运行中的会话不停止、不重启 daemon。
2. `git fetch --no-tags upstream main`，记录确切 SHA。创建新的 `fork/minimal-日期`
   分支，起点为 `upstream/main`，仅 cherry-pick 上次的显示补丁提交。
   再携带维护文件的独立提交。不要按整个旧分支范围盲目 cherry-pick。
3. 查看 `git diff upstream/main`：产品差异只能涉及显示定制和必要测试。
   遇到冲突只适配补丁涉及的接口；检查是否已有等价上游行为，等价时删除补丁。
4. 在 `codex-rs/` 运行下面的验证和本机构建。首次会较慢，复用原有 target 缓存，
   不执行 cargo clean。不另建一套 target/profile 重复编译。

```bash
cd /home/yorkyer/codex/codex-rs
just fmt
env -u NO_COLOR TERM=xterm-256color just test -p codex-tui --lib \
  -E 'test(resumed_completed_tools_are_transcript_only) | test(resumed_initial_messages_render_history) | test(older_tool_projection_matches_initial_replay) | test(replayed_commands_preserve_individual_output_and_failure_status) | test(snapshot_formatter_completed_patch_needs_no_started_notification) | test(live_app_server_file_change_item_started_preserves_changes)' \
  --status-level fail --final-status-level fail
python3 ../maintenance/build_linux.py
```

只改 TUI 时不扩展到整个 TUI、core/app-server 套件。上述测试名随上游重命名时，
只定位对应行为的新测试名，不通过扩大测试范围寻找替代。补丁相关回归必须修复；
偶然遇到无关错误只记录，不展开处理。成功后不重复运行。

## 配套 host 与打包

必须同时编译并安装同一源码版本的 `codex` 与 `codex-code-mode-host`（准确名称不是
`codex-code-host`）。只复制 CLI 会导致 code mode 运行失败。host 必须位于 CLI 旁边，
不能依赖 PATH 中另一个版本的 host，也不能从旧安装中借用。

复用上游打包器，带上 Linux 的 bwrap、rg、patched zsh 和包清单。
下面使用已经构建的 native release 文件，打包阶段不会再次编译 CLI/host。
不要用 `--force` 覆盖旧版本目录。

```bash
cd /home/yorkyer/codex
fork_revision=$(git rev-parse HEAD)
fork_package="/home/yorkyer/.local/lib/codex-forks/$fork_revision"
just assemble-codex-package \
  --target x86_64-unknown-linux-gnu \
  --package-dir "$fork_package" \
  --entrypoint-bin "$PWD/codex-rs/target/release/codex" \
  --code-mode-host-bin "$PWD/codex-rs/target/release/codex-code-mode-host" \
  --bwrap-bin "$PWD/codex-rs/target/release/bwrap"
"$fork_package/bin/codex" --version
"$fork_package/bin/codex-code-mode-host" --help
python3 maintenance/activate.py "$fork_package"
```

源码构建可能报告 `0.0.0`，以提交 SHA 和不可变安装目录识别版本，不为美化版本号修改
整个 workspace。`build_linux.py` 复用上游 `scripts/codex_package/v8.py` 获取并校验
当前 Linux 的配套 archive/bindings，然后执行 native Cargo release 构建。
不要直接裸跑 cargo build：当前 V8 版本的默认 denoland 下载地址会 404，应使用上游
Codex 发布的 artifact。不要自行研究其他平台、源码编译 V8 或混用绑定与静态库。

## 符号链接约定

- `~/.local/bin/codex`：当前 fork，不指向官方 standalone/current。
- `~/.local/bin/codex-fork`：当前 fork 的别名，与 codex 相同。
- `~/.local/bin/codex-stable`：上次切换前的版本，固定到该版本的真实路径。
- `~/.local/bin/codex-official`：官方 standalone/current/bin/codex，独立保留。

`maintenance/activate.py` 在修改链接前检查完整候选包、CLI/host 可启动、现有链接，
用临时 symlink + replace 切换。先保存旧版到 stable，最后更新 codex；重复激活同一版
不覆盖 stable。不会删除旧包、修改官方 current、重启服务或停止已有会话。
多个链接不是一个整体事务；若中断，重复激活同一候选即可完成切换。

```bash
# 查看实际版本，而不是仅看命令名字
readlink -f /home/yorkyer/.local/bin/codex
readlink -f /home/yorkyer/.local/bin/codex-stable
readlink -f /home/yorkyer/.local/bin/codex-official

# 紧急回退：保留 stable，不旋转；新开会话生效
fork_previous=$(readlink -e /home/yorkyer/.local/bin/codex-stable)
test -x "$fork_previous"
test -x "$(dirname "$fork_previous")/codex-code-mode-host"
ln -sfnT "$fork_previous" /home/yorkyer/.local/bin/codex-fork
ln -sfnT "$fork_previous" /home/yorkyer/.local/bin/codex
```

官方安装器可能重写 `~/.local/bin/codex`；更新官方版后务必检查上述链接，再激活 fork。
本次迁移排除含错误订阅补丁的 `5a7af7edef`，用 `--previous-executable` 指定上一个
完整且不含此补丁的安装：
`/home/yorkyer/.local/lib/codex-forks/4aa6037a3a542f09b1d36504745f8da510542611/bin/codex`。
这是一次性例外；之后正常更新不传这个参数，自动保留上一版。历史档案中的错误构建
不作为 stable，也不再作为更新的起点。

## 安装后验收与交付

新开 IceSpark 会话：恢复包含命令、图片和长历史的会话，检查初始画面、向上翻页、
resize/重新打开终端；普通显示不应泄漏已完成工具详情，详细 transcript 仍可查询。
发送一次小任务，确认 code mode 调用 host 正常、实时工具和最终回答正常。
这一步会使用真实会话/credit，不能把 `--version` 冒充完整端到端验收。

记录上游 SHA、显示补丁 SHA、测试结果、安装目录、三个命令的真实目标，以及未完成的
人工验收。本地流程测试：`python3 -m unittest discover -s maintenance -p 'test_*.py'`。
