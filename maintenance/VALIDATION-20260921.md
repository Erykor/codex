# 2026-09-21 干净基线迁移记录

- 官方基线：`2426ed7684c87f9a627c60b54271cfed77c979df`。
- 分支：`fork/minimal-20260921`。
- 唯一产品补丁：`201dedbfadebf140c7fd4eedefd89a07ecf693d1`。
- 误提交 `5a7af7edef` 不在新分支祖先链中；新分支相对官方的产品差异仅 7 个 TUI
  实现/测试文件。login、app-server、订阅状态实现未修改。
- 工作流与本机脚本为独立维护提交，不混入显示补丁。

## 自动验证

以下全套结果为用户进一步限定测试范围之前的历史记录，不是未来更新的必做步骤。
今后只运行 AGENTS.md 中列出的 6 项补丁相关测试，不重跑完整套件，
也不继续处理下列无关快照问题。本次这些补丁相关测试已经通过，不重复执行。

`env -u NO_COLOR TERM=xterm-256color just test -p codex-tui --lib --status-level fail --final-status-level fail`：
5325 项执行，5319 通过（其中 1 项重试后通过）、6 项失败、4 项跳过。
不是全绿。显示补丁的恢复/详情保留测试和文件修改回放测试均通过。

6 项失败均为上游键盘帮助快照在 WSL 下的 `ctrl+v` / `ctrl+alt+v` 差异：

- `agents_navigation_tests::agents_navigation_hint_snapshots`
- `sparkle::tests::shortcut_help_preserves_an_unused_sparkle_but_literal_question_marks_do_not`
- `sparkle::tests::shortcut_help_hides_visible_sparkles_without_restarting_their_deadline`
- `status_surface::tests::shortcut_help_stays_above_the_prompt_and_bottom_status`
- `tests::footer_mode_snapshots`
- `tests::shortcut_footer_displays_configured_chords`

以上路径均在 `bottom_pane::chat_composer` 下。对应目录与官方基线无差异；
`shortcut_overlay.rs` 明确在 `props.is_wsl` 时显示 Ctrl+Alt+V，Linux WSL 检测来自
`/proc/version`，因此只清除 WSL 环境变量不能消除差异。不修改产品代码或接受这些
环境相关快照来伪造全绿。首次测试的 4 项光标颜色失败在取消 NO_COLOR 后已通过。

链接激活脚本的 4 项测试通过：版本轮换、重复激活保留 stable、缺少 host 时拒绝、
保护普通文件、显式排除错误旧版本（版本轮换测试同时覆盖重复激活与官方链接保留）。

## 安装结果

Linux release 构建成功，CLI、`codex-code-mode-host`、bwrap 来自同一次构建。
上游打包器校验通过，host 的 `--help` 与 CLI 的 `--version` 启动检查通过。
安装目录：
`/home/yorkyer/.local/lib/codex-forks/e88e63d915cc4a059fbd4deb7b9a337df504f2ef`。

- `codex`、`codex-fork` → 上述目录的 `bin/codex`（源码构建报告 `0.0.0`）。
- `codex-stable` → `4aa6037a3a542f09b1d36504745f8da510542611/bin/codex`，
  位于相同 codex-forks 根目录；刻意排除含误改的 `5a7af7edef`。
- `codex-official` → 官方 standalone/current，验证为 `0.155.1`。

## 人工验收边界

未对生产 IceSpark 会话执行交互式验收，未调用真实模型，也未停止已有进程。
新开终端后的 resume、旧历史分页、resize、详细 transcript 和 code mode 调用仍需要
实际使用验收。已有会话继续运行原二进制，切换链接不会热替换已运行的程序。
