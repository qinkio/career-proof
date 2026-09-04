# Career Proof 职业资料库

[![Tests](https://github.com/qinkio/career-proof/actions/workflows/test.yml/badge.svg)](https://github.com/qinkio/career-proof/actions/workflows/test.yml)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)

> **让你的每次求职，都从真实做过的事出发。**

把散落在简历、项目文档和工作复盘里的经历，整理成一套**可信、可复用、由你控制**的职业资料库。

以后写简历、准备面试或考虑转岗时，不必重新翻遍文件，也不用担心AI把经历说过头——它只能使用你确认过的内容。

**它不是替你写得更夸张，而是让你每次都能写得更具体、更一致、更有底气。**

[立即开始](#一分钟开始) · [查看完整示例](examples/fictional-career-vault) · [了解安全设计](#它怎样保护你的资料)

## 你是否遇到过这些问题？

- 做过很多项目，真正写简历时却想不起关键细节；
- 同一个成果在不同版本简历里出现了不同数字；
- AI写得很漂亮，但你不确定面试时能不能讲清楚；
- 想转岗，却不知道哪些经验能够迁移、哪些能力还缺证明；
- 工作资料涉及隐私，不希望AI一次性读取整个文件夹。

Career Proof就是为这些问题设计的。

## 一次整理，反复使用

| 原来的状态 | 使用Career Proof后 |
|---|---|
| 项目散落在不同文件里 | 每个项目都有清晰的背景、职责和结果 |
| 成果数字靠记忆 | 数字附带来源、口径和时间范围 |
| 团队成果容易被写成个人成果 | 明确区分独立负责、共同负责和团队成果 |
| 每次求职都从零整理 | 已确认的经历可以按岗位重复调用 |
| AI可能读到不该读的资料 | 先登记、后授权，只读取你允许的文件 |
| 简历、面试说法不一致 | 两者使用同一套已确认事实 |

你最终会得到：

- **项目清单**：快速回忆自己做过什么、解决了什么问题；
- **可信成果**：明确哪些职责、行动和结果已经有资料支持；
- **能力地图**：每项能力都能对应到具体项目和事实；
- **待确认清单**：集中处理数字口径、个人贡献和资料冲突；
- **安全证据包**：只向简历或面试工具提供当前任务需要的内容。

## 30秒看懂一个例子

假设你的材料里写着：

```text
参与客服审批流程优化，提升了处理效率。
```

Career Proof不会直接把它包装成“主导重大效率提升”，而是帮助你拆清楚：

```text
项目：客服审批流程试点
你的行动：访谈6名客服，将11个重复节点归并为5个标准节点
结果：40个试运行工单的审批时间中位数从8.0天降至5.5天
归因：与产品和客服主管共同负责
证据：项目复盘中的访谈记录和试运行结果表
状态：已由用户确认，可用于求职材料
```

于是AI可以生成更具体的简历要点和面试故事，同时保留真实的职责边界。

查看[完整虚构案例](examples/fictional-career-vault)，了解两份原始材料如何变成项目卡、可信成果、能力地图和面试证据包。案例中的人物、项目和数字全部为虚构。

## 适合谁

- 工作资料散落在简历、述职、项目文档、演示文稿和表格里；
- 工作多年，但很难快速说清自己的项目价值和核心能力；
- 正在转岗，需要用具体经历证明能力可以迁移；
- 经常用AI写简历或准备面试，又担心数字、归因和隐私失控；
- 想长期积累职业资产，而不是每次求职都重新开始。

如果你只有一份简单简历、只想快速润色几句话，这个Skill可能过重。

## 一分钟开始

### 让Agent安装

把下面这句话发送给支持Agent Skills的工具：

```text
请安装这个Skill：
https://github.com/qinkio/career-proof/tree/main/skills/career-proof
```

### Codex手动安装

```bash
git clone https://github.com/qinkio/career-proof.git
mkdir -p ~/.codex/skills
cp -R career-proof/skills/career-proof ~/.codex/skills/career-proof
```

### Claude Code手动安装

```bash
git clone https://github.com/qinkio/career-proof.git
mkdir -p ~/.claude/skills
cp -R career-proof/skills/career-proof ~/.claude/skills/career-proof
```

安装后新建任务并输入：

```text
用 $career-proof 为我建立一个私有职业资料库。
先展示准备创建的路径和文件，不要读取未经我批准的资料。
```

Skill会先展示精确计划并停下来。只有你确认路径后，它才会创建文件。

## 它怎样保护你的资料

```text
1. 先登记文件，不读取正文
2. 你逐份决定是否允许读取
3. AI提出项目和成果，先进入待确认清单
4. 只有你确认后，内容才进入正式资料库
5. 使用时只导出当前任务需要的最少内容
```

安全边界：

- 未经批准不读取正文，也不计算内容哈希；
- 标为 `do-not-model` 的文件永远不读取、不哈希、不提取；
- “内容是否可信”和“是否允许对外使用”分开管理；
- 不自动连接Notion，不自动上传资料，没有遥测；
- 真实职业资料必须保存在公开仓库之外。

它不会编造经历、夸大个人贡献，也不会因为一句模糊描述就认定成果真实。最终确认权始终属于你。

## 与面试Skill配合

Career Proof负责保存可信事实，[prepare-interview-pack](https://github.com/qinkio/prepare-interview-pack)负责把事实组织成面试答案：

```text
散落的职业资料
      ↓ Career Proof整理和确认
可复用的职业资料库
      ↓ 只导出目标岗位需要的内容
prepare-interview-pack
      ↓
自我介绍、项目故事、预测问题和练习计划
```

这样，简历和面试可以使用同一套事实，面试工具也不需要扫描你的整个私人目录。

## 资料库结构

```text
career-vault/
├── profile.md                 个人背景和求职约束
├── career-timeline.md         职业时间线
├── sources.csv                文件目录与读取权限
├── canonical-claims.csv       已审核的职责、行动和成果
├── capability-map.csv         能力与证明事实的对应关系
├── review-queue.csv           待确认问题
├── change-log.csv             变更历史
├── projects/                  项目证据卡
├── evidence/                  可选的受管证据副本
├── exports/                   提供给其他Skill的最小证据包
└── archive/                   安全快照
```

这里的 `Claim` 指一句能够单独核验的事实，例如“我负责需求访谈”或“该流程覆盖35家虚构门店”，不是包装完成的简历文案。

## 从v0.1升级

v0.2聚焦职业资料和事实管理，完整面试准备已迁移到 `prepare-interview-pack`。迁移器只创建新副本，不覆盖旧库。

参见：[v0.1升级到v0.2](docs/migration-v0.1-to-v0.2.md)。

## 开发和验证

核心脚本仅使用Python标准库，支持Python 3.10及以上版本。

```bash
python3 -m unittest discover -s tests -v
python3 skills/career-proof/scripts/preflight_public_repo.py .
```

自动测试覆盖初始化、增量索引、读取权限、结构校验、冲突检测、用途导出、安全快照、公开示例和旧库迁移。

`v0.2.0-beta`仍是测试版本。结构验证通过不代表事实已经被证明或获得发布许可。

## License

MIT
