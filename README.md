# Azhi_skills

我自己用的简单 skills 集合，主要是工程规范 / 开发流程类，随用随加。

## 安装

```bash
npx skills add Azhi-ss/Azhi_skills
```

只装单个 skill：

```bash
npx skills add Azhi-ss/Azhi_skills/skills/orca-ticket-loop
```

## Skills

- **orca-ticket-loop** — 一票一上下文的开发循环：每个全新 Pi 上下文只认领一个 GitHub issue，TDD 实现、过 gate 和 code review，提交并关闭后，在当前 Orca worktree 里派发新 Pi 处理下一个合格 ticket，然后停止。依赖 Orca CLI、gh、pi。
