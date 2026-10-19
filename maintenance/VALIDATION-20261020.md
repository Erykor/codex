# 2026-10-20 官方 main 更新记录

## 源码与补丁

- 分支：`main`；更新前工作区干净，本地 HEAD 与抓取的 `origin/main` 均为
  `7d8cd6f54658ef0e9da7a6975eced36398ab7c68`。
- 本次抓取的官方基线：`c3bb20602d77b0c8e62f84e9956e8086f439dfeb`。
- 旧 HEAD 保存在本地 `refs/archive/pre-rebase-20261020/main`。
- 唯一产品补丁：`83c6407ef939c572317955130a2d030170e30c34`。
  上游尚无等价的恢复工具隐藏行为，保留原有 7 个 TUI 实现/测试文件的差异。
- 适配上游 `activity_disclosure` 接口及命令记录的 `sandbox_type` 字段；转发新增的
  `image_path` 接口并补充断言，保留恢复图片的 transcript 预览。
- rebase 唯一文本冲突为上游删除、本地修改 `AGENTS.md`；保留本地精简维护说明。
  废弃提交 `5a7af7edef` 不在新分支祖先链中。
- CLI、host 和 bwrap 的构建源码提交：
  `c611162461108495798e61534800fea32f00dbc5`。后续提交仅更新维护脚本和记录，
  不改变已验证的 Rust 产品源码。

## 验证

- `just fmt` 成功，`git diff --check` 通过。
- AGENTS.md 指定的 6 项 TUI 回归测试全部通过，5817 项未选中；未扩展测试范围。
- `python3 -m unittest discover -s maintenance -p 'test_*.py'`：4 项通过。
  激活脚本适配上游包结构后重新运行，4 项仍通过。
- `python3 maintenance/build_linux.py`：native Linux release 构建成功，耗时 10m 04s；
  复用原 target 缓存，通过上游解析器获取并校验 V8 152.2.0 的配套 archive/bindings。
- 构建报告上游 bwrap C 警告、app-server `unused_mut` 和 cloud-tasks 未使用导入警告；
  未修改或展开处理这些无关代码。
- 上游打包器验证成功；CLI `--version` 和同包 host `--help` 均成功。
  源码构建报告 `codex-cli 0.0.0`，以源码 SHA 和安装目录识别版本。
- 首次激活被旧 patched zsh 文件检查拒绝，未切换链接。上游 `a645742bb5` 已停止
  打包 patched zsh，当前运行时也已移除该后端；同步移除维护脚本和测试夹具的旧要求，
  更新 AGENTS.md 后激活成功。没有补装旧 zsh，也没有修改上游打包器或运行时。

## 安装与回退

完整包目录：
`/home/yorkyer/.local/lib/codex-forks/c611162461108495798e61534800fea32f00dbc5`。
包含同源码的 CLI/host/bwrap、rg 和上游包清单；未覆盖旧包目录。

- `codex`、`codex-fork` →
  `/home/yorkyer/.local/lib/codex-forks/c611162461108495798e61534800fea32f00dbc5/bin/codex`。
- `codex-stable` →
  `/home/yorkyer/.local/lib/codex-forks/7d8cd6f54658ef0e9da7a6975eced36398ab7c68/bin/codex`。
- `codex-official` →
  `/home/yorkyer/.codex/packages/standalone/releases/0.155.1-x86_64-unknown-linux-musl/bin/codex`。
- 更新前 `codex` 为上述 `7d8cd6f5` 包；`codex-stable` 为
  `/home/yorkyer/.local/lib/codex-forks/e88e63d915cc4a059fbd4deb7b9a337df504f2ef/bin/codex`；
  官方目标未改变。

## 人工验收边界

未新开真实 IceSpark 会话调用模型，未消耗真实模型 credit，未停止会话或重启 daemon。
仍需人工验证恢复包含命令、图片和长历史的会话：初始画面、向上翻页、resize、
重新打开终端、详细 transcript，以及一次实际 code mode host 调用和最终回答。
启动检查不等于端到端验收；已运行的进程继续使用原二进制。
