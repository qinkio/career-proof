# 从Career Proof v0.1升级到v0.2

v0.2把Career Proof收敛为“职业资料与证据管理”Skill。升级不会覆盖原资产库。

## 主要变化

### 保留并加强

- 职业时间线、项目卡和事实Claim；
- 指标口径与个人贡献审核；
- 原始资料与公开Skill仓库隔离；
- 公开发布前的隐私检查。

### 新增

- 来源文件的增量索引和移动识别；
- 独立审核队列；
- Claim与能力映射分离；
- 内容敏感度、模型读取权限和发布权限三轴管理；
- Claim撤回、替代和变更记录；
- 安全快照与恢复预览；
- 面向其他Skill的最小JSON证据包。

### 迁出

- 完整面试手册交给 `prepare-interview-pack`；
- 简历写作、岗位发现、转型规划和投递漏斗不再由本Skill负责。

## 为什么部分旧Claim会变成待确认

旧版可能把“提升30%”及其解释保存在同一个自由文本字段。v0.2要求分别记录指标名称、基线、结果、单位、周期、范围、计算方式和个人归因。

迁移器不会猜测这些字段。结构不完整的指标会进入 `pending`，并在 `review-queue.csv` 产生审核项。这样可以避免迁移过程把旧表述错误升级成更强的事实。

旧版单一隐私字段也不能直接对应v0.2的三轴权限，因此不明确的权限会进入审核队列。

## 安全迁移

先预览：

```bash
python3 skills/career-proof/scripts/migrate_v01_to_v02.py \
  /absolute/old-vault \
  /absolute/new-vault
```

确认两个精确路径后执行：

```bash
python3 skills/career-proof/scripts/migrate_v01_to_v02.py \
  /absolute/old-vault \
  /absolute/new-vault \
  --yes
```

迁移器拒绝覆盖已存在的目标目录。旧库保持不变。

迁移后验证：

```bash
python3 skills/career-proof/scripts/validate_vault.py /absolute/new-vault
python3 skills/career-proof/scripts/detect_claim_candidates.py \
  /absolute/new-vault/canonical-claims.csv
```

## 建议审核顺序

1. 确认项目边界和父子关系；
2. 确认正式职称与实际职责；
3. 拆分旧指标口径；
4. 确认个人、共同和团队成果；
5. 确认读取权限和发布用途；
6. 建立能力映射；
7. 最后才生成面试或简历证据包。

在所有高风险审核项处理完成前，保留旧库作为只读参照。
