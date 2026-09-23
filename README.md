# Azhi_skills

我自己用的简单 skills 集合，主要是工程规范 / 开发流程类，随用随加。

## 安装

```bash
npx skills add Azhi-ss/Azhi_skills
```

只装单个 skill：

```bash
npx skills add Azhi-ss/Azhi_skills/orca-ticket-loop
```

## Skills

- **orca-ticket-loop** — v2 自主开发循环：首票即在当前 Orca worktree 新开 Pi 终端，一上下文只处理一票；TDD、测试和审查问题自主修复，上下文不足续接同票，单票阻塞时安全转做独立票。保留真实决策授权、验收门槛与单写入者约束，完成后提交、关闭并派发下一票；不默认 push。依赖 Orca CLI、gh、pi。
