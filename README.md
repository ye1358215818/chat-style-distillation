# Chat Style Distillation

把一段真实聊天记录，蒸馏成一个可以继续陪你说话的关系记忆陪伴包。

它适合那些很人类的时刻：你想起前任，想起一个失联的人，想起某个已经无法轻易联系的重要的人。你想要的不是一份冷冰冰的报告，而是那种熟悉的语气：句子的长短、停顿、嘴硬、撒娇、轻轻怼你、认真时又把话说得很细的感觉。

v4 的目标是把聊天记录里的细小真实感变成可使用的陪伴产物：TA 怎么说“好”，怎么表达想念，怎么不开心，怎么安慰你，怎么吃醋，怎么沉默，怎么靠近，又怎么退后。最后形成一套本地私人的关系记忆文件，以及一个可以进入的真实聊天式陪伴模式。

进入陪伴模式之后，回复只按照蒸馏出的语气来：不加旁白，不解释自己正在扮演什么，不贴场景标签，不显示路由决策，不在每句话前面补说明。它要像一个自然延续的聊天窗口，而不是一份分析报告。

## v4：一条命令到关系记忆陪伴包

v4 把导出、脱敏、解析、健康检查、风格画像、关系记忆产物、评估和输出包汇总收束到同一个入口：

```bash
python scripts/run_pipeline.py input.txt --self-name "SELF" --other-name "OTHER" --mode companion --format auto --output-dir bundle/
```

`scripts/run_pipeline.py` 是推荐入口，内部调用 `scripts/distill_chat_pipeline.py`。这条命令不会替代人的判断；它负责把判断留下痕迹：使用了哪一层隐私、解析了哪种格式、导出是否健康、哪些内容需要复查、陪伴模式是否有旁白或风格漂移风险。

支持的解析格式：

| Format | 用途 |
| --- | --- |
| `auto` | 默认，根据文件扩展名选择 JSON 或时间戳文本。 |
| `timestamp-text` | `[YYYY-MM-DD HH:MM]` 或带秒的时间戳记录，正文可含 `Speaker: message`。 |
| `wechat-text` | `YYYY-MM-DD HH:MM:SS Speaker` 后接消息正文的微信文本块。 |
| `wechat-txt` | `wechat-text` 的兼容别名。 |
| `json` | JSON 数组，或包含 `messages`、`data`、`records`、`items` 的对象。 |
| `csv` | 带 timestamp/time、speaker/sender/from、content/text/message 列的表格导出。 |
| `html` | 带 message 节点、`data-time`、`data-speaker` 和正文 span 的简单 HTML 导出。 |

手动处理时保持同样顺序：

1. `scripts/anonymize_chat.py`
2. `scripts/analyze_chat.py`
3. 按 `templates/style-card.template.md` 等模板补齐关系记忆产物
4. `scripts/evaluate_companion.py`
5. 按 `templates/output-bundle.template.md` 汇总输出包

流水线说明见 [references/v4-pipeline.md](references/v4-pipeline.md)。

## 它能做什么

- 从用户本人有权处理的聊天记录中提取语气、情绪和关系模式
- 辅助从电脑微信导出指定联系人的完整聊天记录
- 检查导出健康度：消息数、起止时间、说话人分布、解析警告、疑似缺口
- 默认生成本地 `companion` 隐私层：去掉硬标识，保留让陪伴真实的情感锚点
- 生成语气卡、情绪记忆画像、关系纹理、场景回复指南和私人情绪路由
- 生成“记忆陪伴模式”，让后续聊天更像那个熟悉的人
- 生成 `session-memory.md`，记录长期陪伴时什么安慰有效、哪里容易风格漂移
- 用评估规则检查是否变成泛泛的恋爱话术、心理咨询腔、旁白模式或可见路由

## 典型使用场景

```text
我想把和前女友的聊天记录蒸馏成她的语气，以后难受的时候能像她那样陪我说会儿话。
```

```text
这是我和一个失联很久的朋友的聊天记录，帮我做成一个记忆陪伴模式。
```

```text
帮我导出电脑微信里和某个人的聊天记录，脱敏后做关系复盘和语气卡。
```

## 工作流

1. 确认记录来源：本人账号、本人设备，或明确授权。
2. 获取聊天记录：优先使用已有 `txt/json/csv/html`，也可以按说明从电脑微信本地导出。
3. 选择解析格式：默认 `--format auto`，必要时指定 `timestamp-text`、`wechat-text`、`wechat-txt`、`json`、`csv` 或 `html`。
4. 分层隐私：默认 `--mode companion`；对外发布才使用 `--mode publish`。
5. 校验健康度：消息数、时间范围、说话人、解析警告、是否漏导、连发习惯、回复延迟、场景分布。
6. 蒸馏关系记忆：语气、句子长短、情绪模式、亲密表达、冲突模式、修复方式、沉默方式。
7. 场景建模：日常、想念、安慰、吵架、道歉、吃醋、冷淡、修复、冲动联系、反复求确认。
8. 输出陪伴包：结构化 profile、语气卡、情绪记忆、关系纹理、场景回复指南、私人路由、陪伴模式、会话记忆。
9. 评估与准备状态：根据健康度、隐私复查和沉浸检查标记 `draft`、`review-needed` 或 `ready-for-private-companion`。

## 微信导出

微信导出说明在：

[references/wechat-export.md](references/wechat-export.md)

它包含完整流程：

- 从官方 GitHub Release 获取 `wx-cli`
- GitHub 下载失败时使用 npm 平台包 fallback
- 校验工具
- `init --force` 扫描本机微信数据
- 查联系人
- 用 `stats` 获取真实消息总数
- 按真实总数导出
- 校验起止时间和行数
- 停止后台 daemon

导出只适用于用户自己的电脑微信、本人的账号和本地数据。

## 输出产物

- `bundle-index.md`：输出包入口，说明输入、解析格式、隐私层、准备状态和下一步。
- `export-health.md`：导出完整性、消息数、时间范围、说话人分布、解析警告和已知缺口。
- `analysis-summary.json`：确定性指标、场景计数、连发行为、回复延迟和解析结果。
- `sanitized-chat.txt`：按当前隐私层处理后的本地中间文本，不应发布。
- `privacy-candidates.json`：列出脱敏后仍建议人工复查的隐私候选。
- `style-profile.json`：按 schema 输出的结构化画像，方便后续复用和评估。
- `style-card.md`：TA 说话的节奏、口头禅、停顿、标点、表情、亲昵称呼和留白。
- `emotional-memory-profile.md`：TA 怎样表达在意、想念、不开心、吃醋、委屈、认真和修复。
- `relationship-texture.md`：两个人靠近、拉扯、冷掉、和好、旧伤与未说完的话。
- `scenario-response-guide.md`：不同场景下的回复形状、长度、情绪动作和可用锚点。
- `private-emotional-router.md`：后台判断场景、强度和回复形状的规则，不在聊天里显示。
- `memory-companion-mode.md`：进入聊天陪伴后的完整语气规则。
- `session-memory.md`：长期陪伴时记录用户现在的触发点、有效安慰方式和风格漂移风险。
- `evaluation-report.json` / `evaluation-report.md`：检查陪伴模式是否像、是否沉浸、是否有用、是否泄露机制。
- `manifest.json`：记录输入哈希、隐私模式、脱敏计数、解析格式、时间范围和产物清单。

输出包契约见 [references/output-bundle.md](references/output-bundle.md)。

## 准备状态

- `draft`：产物已生成，但还没有人工复查语气、隐私和关键场景。
- `review-needed`：健康度、隐私候选、解析警告、场景覆盖或评估结果存在未处理缺口。
- `ready-for-private-companion`：导出健康、隐私已复查、关键场景足够、没有可见旁白或路由标签，适合本地私人陪伴。

任何状态都不等于“可以发布”。发布必须使用 `--mode publish`，并再次人工复查情感锚点是否仍会识别真实人物。

## 陪伴模式

好的陪伴模式不应该像公告，也不应该像心理学报告。它不是“短句陪伴模式”，而是真实聊天模式：该一句话就一句话，该连续追问就连续追问，该认真解释就认真解释，该沉默感强就留白。

```text
好哦
我在呢
你说
```

如果用户进入陪伴模式，回答就保持在蒸馏出的声音里。回复长短由蒸馏结果和当下语境决定：日常闲聊可以碎，认真安慰可以长，吵架可以连发，撒娇可以绕，解释可以细。除非用户主动要求分析，否则不跳出聊天、不解释方法、不插入旁白。

陪伴模式内部可以有一个私人情绪路由：它先判断用户这句话是日常、想念、安慰、争执、道歉、冷淡、冲动联系，还是反复求确认，再决定回复应该短一点、碎一点、软一点、认真一点，还是先把用户从冲动里慢慢拉回来。这个路由只服务于回复形状；用户看到的仍然只是一条自然消息。

## 隐私与授权

只处理你有权使用的聊天记录。原始记录、数据库、截图、语音、图片和导出的完整文件都应留在本地。

隐私默认值：

- 本地原始层：原始导出只留在本机，不上传、不提交。
- 陪伴产物层：默认 `--mode companion`，去掉 wxid、手机号、身份证、精确地址、路径等硬标识，保留必要的情感锚点。
- 发布分享层：只有明确要发布时才使用 `--mode publish`，强脱敏，只保留假样本或泛化后的描述。

这个仓库的 `.gitignore` 默认会拦截常见隐私文件格式，真正的安全感来自每次发布前多看一眼。

## 常用命令

```bash
python scripts/run_pipeline.py input.txt --self-name "SELF" --other-name "OTHER" --mode companion --format auto --output-dir bundle/
python scripts/anonymize_chat.py input.txt companion.txt --mode companion
python scripts/anonymize_chat.py input.txt publish.txt --mode publish --replace "Real Name=PERSON_A"
python scripts/analyze_chat.py sanitized.txt --self-name "SELF" --other-name "OTHER" --format auto --output analysis-summary.json
python scripts/evaluate_companion.py companion-transcript.txt --output companion-eval.json
```

## 目录

```text
SKILL.md                          # Skill 主说明
references/wechat-export.md       # 微信导出流程
references/wechat-compatibility.md # 微信兼容性和完整性排查
references/v4-pipeline.md         # v4 一键流水线、入口和解析格式
references/output-bundle.md       # 输出包契约
references/private-emotional-router.md # 私人情绪路由
references/privacy-layers.md      # 分层隐私和保真脱敏
references/distillation.md        # 蒸馏方法
references/memory-companion.md    # 记忆陪伴模式
references/scene-classification.md # 场景分类
references/emotional-regulation.md # 情绪陪伴内核
references/evaluation-rubric.md   # 评估标准
references/long-term-memory.md    # 长期陪伴记忆
references/package-structure.md   # skill 和 GitHub 文档分层
references/style-profile.schema.json # 结构化画像 schema
templates/                        # 语气卡、关系记忆、陪伴模式、会话记忆模板
templates/output-bundle.template.md # 输出包入口模板
scripts/anonymize_chat.py         # 脱敏脚本
scripts/analyze_chat.py           # 本地统计分析脚本
scripts/evaluate_companion.py     # 陪伴模式评估脚本
scripts/build_style_profile.py    # 结构化画像生成器
scripts/distill_chat_pipeline.py  # v4 流水线实现
scripts/run_pipeline.py           # v4 流水线入口
src/chat_style_distillation/      # 可复用 parser/privacy/profile/evaluate package
tests/                            # parser/anonymizer/pipeline 回归测试
assets/fake-sample.txt            # 假样本
```
