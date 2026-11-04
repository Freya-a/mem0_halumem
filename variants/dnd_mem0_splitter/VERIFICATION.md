# 验证记录

验证日期：2026-11-03（用户时区 Asia/Shanghai）。环境：Python 3.12.7。

## 初始状态与范围

创建前检查：目标目录不存在，因而 DESIGN.md 也不存在，无既有设计差异需要报告。所有最终文件通过排他创建写入，没有覆盖任务开始时已有文件。

项目位置不是 Git 仓库；按用户指定路径直接创建独立目录，没有创建分支、提交或 worktree。只使用标准库和手写自拟样例，未调用真实模型、Mem0 或子代理，未安装依赖，未读取 API 密钥、开发子集或知识库，也未改动 external/。

## 测试先行与模块测试

先保存设计、自拟 JSON 和 test_splitter.py，再运行模块测试：23 项测试因 splitter.py 尚未实现而失败（含子测试共 44 个失败断言，退出码 1）。

实现后执行：

```bash
python3 -B -m unittest discover -s . -p test_splitter.py -v
```

实际结果：Ran 23 tests；OK；退出码 0。

覆盖：必填字段和类型、可选上下文、源 ID 唯一性、顶层回显与事实/依据 ID 冲突、连续整数编号、原文和空白保留、后端参数修改隔离、返回对象隔离、原记忆/上下文引文匹配、未知来源、只有上下文依据、待确认结构、未知字段、重复 JSON 键、无效 JSON、文件不存在，以及 CLI 成功和无部分输出的失败行为。

没有运行项目级测试或开发子集，以遵守本次范围限制。

## 正常模拟

命令：

```bash
python3 -B splitter.py --input examples/input.json --mock-response examples/mock_response.json
```

实际退出码：0。stdout 为下面的完整 JSON，stderr 为空（CLI 测试另有断言）。这是手写模拟响应经过程序校验后的输出，不是模型生成结果。

```json
{
  "memory_id": "EXAMPLE_ONLY_NOT_A_REAL_MEM0_ID",
  "memory_text": "李娜去年没有搬到上海；王强说，如果获批，他可能明年搬去。",
  "facts": [
    {
      "fact_index": 1,
      "source_memory_id": "EXAMPLE_ONLY_NOT_A_REAL_MEM0_ID",
      "raw_subfact": "李娜去年没有搬到上海。",
      "contextualized_subfact": "李娜去年没有搬到上海。",
      "evidence": [
        {
          "source_type": "memory",
          "source_id": "EXAMPLE_ONLY_NOT_A_REAL_MEM0_ID",
          "quote": "李娜去年没有搬到上海",
          "supports": "李娜在“去年”没有搬到上海这一否定陈述。"
        }
      ],
      "pending_confirmations": [
        {
          "item": "“去年”对应的具体年份",
          "reason": "没有提供能够确定该相对时间的可靠锚点。"
        }
      ]
    },
    {
      "fact_index": 2,
      "source_memory_id": "EXAMPLE_ONLY_NOT_A_REAL_MEM0_ID",
      "raw_subfact": "王强说，如果获批，他可能明年搬去。",
      "contextualized_subfact": "王强说，如果获批，王强可能明年搬到上海。",
      "evidence": [
        {
          "source_type": "memory",
          "source_id": "EXAMPLE_ONLY_NOT_A_REAL_MEM0_ID",
          "quote": "王强说，如果获批，他可能明年搬去。",
          "supports": "王强的引述、人物指代、获批条件、相对时间和可能性。"
        },
        {
          "source_type": "context",
          "source_id": "ctx-1",
          "quote": "王强：这里的“搬去”是指搬到上海。",
          "supports": "补足王强所说的搬迁目的地为上海。"
        }
      ],
      "pending_confirmations": [
        {
          "item": "“明年”对应的具体年份",
          "reason": "没有提供能够确定该相对时间的可靠锚点。"
        },
        {
          "item": "“获批”所指的申请或事项",
          "reason": "旧记忆及来源上下文均未说明。"
        }
      ]
    }
  ]
}
```

## 来源引文不匹配

错误响应将第二条事实的上下文引文中的“上海”改成“北京”，输入上下文仍为“上海”。

命令：

```bash
python3 -B splitter.py --input examples/input.json --mock-response examples/mock_response_bad_quote.json
```

实际退出码：2。stdout 为空，stderr 输出如下（CLI 测试另有断言）。没有修正错误引文，没有输出部分成功结果。

```json
{
  "error": {
    "code": "quote_not_found",
    "path": "$.facts[1].evidence[1].quote",
    "message": "Quote is not an exact substring of the declared input source."
  }
}
```

## 按需求自检

- Task 1 complete：保存已讨论设计、完整提示词和手写示例；无已有文件可覆盖。
- Task 2 complete：实现独立 API、手写模拟后端、CLI、结构和来源校验。
- CLI 不提供文件写入参数；成功结果仅发到 stdout，错误仅发到 stderr。
- ID、原文由输入快照组装，不依赖后端回显；冲突先报错，不静默纠正。
- 引文校验使用所声明来源的逐字子串匹配，不使用事实文本本身作为引文校验源。
- 本目录之外没有任务写入；临时测试文件在本目录内创建并清理，未生成 __pycache__。

复核方式：作者按代码审查清单自检，未调用其他模型。未发现妨碍本次模拟初版交付的问题。

保留的能力边界：字面引文校验不能证明语义蕴含、完整性、上下文可靠性或现实真实性；占位示例 ID 不能证明真实 Mem0 ID 存在。真实模型接入、Mem0 接入、开发子集与质量对比均未实施。
