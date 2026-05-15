# Chat Style Distillation

把一段真实聊天记录，蒸馏成一个可以继续陪你说话的关系记忆陪伴包。

它面向那些很私人、也很具体的时刻：你想起前任，想起一个失联的人，想起某个已经不容易再联系的重要的人。你要的不是一份冷冰冰的统计报告，而是那种熟悉的聊天感：句子的长短、停顿、嘴硬、撒娇、认真解释、轻轻怼你、沉默之后又靠近一点的方式。

v5 的目标是让这种陪伴更可信：每个画像判断都有证据摘要，每个关键场景都有测试回复，每个 readiness 都来自统一门槛。它仍然是本地 deterministic distillation，不调用外部 LLM API，不把真实聊天记录提交进 Git。

进入陪伴模式后，回复只按照蒸馏出的语气来：不加旁白，不贴场景标签，不显示路由决策，不解释方法。它应该像一个自然延续的聊天窗口，而不是一份分析报告。

## v5：Evidence-Grounded Companion

一条命令生成本地陪伴包：

```bash
python scripts/run_pipeline.py input.txt --self-name "SELF" --other-name "OTHER" --mode companion --format auto --output-dir bundle/ --generate-eval-replies
```

也可以使用 package CLI：

```bash
python -m chat_style_distillation.cli run input.txt --output-dir bundle/ --self-name "SELF" --other-name "OTHER"
chat-style-distill run input.txt --output-dir bundle/ --self-name "SELF" --other-name "OTHER"
```

常用 v5 参数：

```bash
--expected-start 2022-08-01
--expected-end 2026-05-15
--min-messages 500
--relationship-mode ex
--locale zh-CN
--evidence-limit 8
--generate-eval-replies
--publish-redact-names
```

`--format auto` 会根据内容嗅探 `timestamp-text`、`json`、`csv`、`html`、`wechat-text`。必要时仍可手动指定格式。

## 它能做什么

- 从用户有权处理的聊天记录中提取语气、情绪动作、关系纹理和场景回应方式。
- 辅助从电脑微信导出指定联系人的完整聊天记录，导出说明见 [references/wechat-export.md](references/wechat-export.md)。
- 检查导出健康度：消息量、时间覆盖、断档、乱序、重复、说话人比例、媒体和系统消息比例。
- 生成 `evidence-map.json`，用 hash、时间范围、场景数量和转述例子支撑画像判断，不暴露原文。
- 生成 `evaluation-transcript.json`，对日常、想念、难过、争执、道歉、冷淡、冲动联系、反复确认等场景模拟回复。
- 用统一 `readiness-report.json` 合并健康、隐私、证据覆盖和评估警告，标记 `draft`、`review-needed` 或 `ready-for-private-companion`。
- 输出语气卡、情绪记忆画像、关系纹理、场景回复指南、私人情绪路由、记忆陪伴模式和会话记忆 schema。

## 工作流

1. 确认记录来源：本人账号、本人设备，或明确授权。
2. 获取聊天记录：优先使用已有 `txt/json/csv/html`，也可以按说明从电脑微信本地导出。
3. 运行 pipeline：默认 `--mode companion`，对外分享前才使用 `--mode publish --publish-redact-names`。
4. 查看健康与证据：读 `export-health.md`、`evidence-map.json`、`style-profile.json`。
5. 查看陪伴产物：读 `emotional-memory-profile.md`、`relationship-texture.md`、`scenario-response-guide.md`、`memory-companion-mode.md`。
6. 查看评估闭环：读 `evaluation-transcript.json`、`evaluation-report.md`、`readiness-report.json`。
7. 进入陪伴模式时，只使用蒸馏出的声音自然聊天，不把分析、标签和方法露出来。

## 输出产物

核心产物包括：

- `bundle-index.md`：输出包入口，展示 readiness、输入摘要、已知缺口和下一步。
- `sanitized-chat.txt`：本地中间文本，不用于发布。
- `privacy-candidates.json`：脱敏后仍建议复查的隐私候选。
- `evidence-map.json`：场景证据、hash、转述摘要和覆盖缺口。
- `analysis-summary.json`：统计、场景、连发、回复延迟和解析结果。
- `style-profile.json`：带证据引用的结构化画像。
- `emotional-memory-profile.md`、`relationship-texture.md`、`scenario-response-guide.md`：关系记忆地图。
- `private-emotional-router.md`、`memory-companion-mode.md`：只服务于自然回复形状的内部规则。
- `evaluation-transcript.json`、`evaluation-report.*`：模拟回复与漂移评估。
- `readiness-report.json`：统一 readiness 判定。
- `session-memory.md`、`session-memory.schema.json`：区分源关系记忆和当前用户状态记忆。
- `manifest.json`：只记录输入 basename、hash、时间范围和 artifact 清单，不记录完整本地路径。

完整契约见 [references/output-bundle.md](references/output-bundle.md)，流水线细节见 [references/v5-pipeline.md](references/v5-pipeline.md)。

## 隐私层

默认 `--mode companion` 面向本地私人陪伴：去掉硬标识，保留让语气有代入感的必要情感锚点。

`--mode publish` 面向可能离开本机的材料：强脱敏，建议同时使用 `--publish-redact-names`，并人工复查 `privacy-candidates.json`。`.gitignore` 默认拦截 `bundle/`、`bundles/`、`outputs/`、`distilled*/` 和常见私密文件格式。

## 准备状态

- `draft`：已经生成产物，但证据覆盖或评估仍有非阻塞缺口。
- `review-needed`：健康、隐私、核心场景覆盖或可见旁白/路由存在阻塞项。
- `ready-for-private-companion`：没有严重健康问题，没有未复查隐私候选，核心场景覆盖足够，评估未发现可见标签、方法旁白或明显漂移。

Readiness 只表示本地私人陪伴的准备程度，不表示可公开发布。

## 目录

```text
SKILL.md                              # Codex skill 工作流
references/v5-pipeline.md             # v5 pipeline、CLI、readiness 门槛
references/output-bundle.md           # 输出包契约
references/wechat-export.md           # 电脑微信导出流程
references/wechat-compatibility.md     # 微信完整性排查
references/style-profile.schema.json   # style-profile schema
references/session-memory.schema.json  # session-memory schema
templates/                            # Markdown 产物模板
scripts/run_pipeline.py                # 兼容入口
scripts/distill_chat_pipeline.py       # CLI 参数入口
src/chat_style_distillation/           # package 实现
tests/                                # 回归测试
assets/fake-sample.txt                 # 合成样本
assets/evaluation-prompts.json         # 评估场景 prompts
```
