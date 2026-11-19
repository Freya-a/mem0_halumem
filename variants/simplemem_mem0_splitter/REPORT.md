# 五例试运行记录（连接错误后停止）

试验使用 `qwen-plus-2025-12-01`，五例的旧记忆均来自 HaluMem-Medium 第一行各更新记录的 `original_memories`；精确数据指针在 `run/cases.json`。选择时只取旧记忆；模型输入的 `source_context` 均为 null，没有传入更新后的事实或对话时间。五例来自同一用户，仅用于小规模接口摸底，不代表总体表现。

离线验证：手工响应测试覆盖正常、多段引文、不存在的引文、重复定位、上下文不匹配、指代未决、null 时间、非法 JSON、缺字段和无效 ID；13 项通过。程序检查结构和引文命中，不检查语义蕴含、信息遗漏或幻觉；单元引用命中也不保证足以支持主张。这些离线测试不代表模型输出通过验证。

实际只调用一次，耗时 0.473 秒，状态 `APIConnectionError`；没有原始模型响应，也无法记录实际返回模型。SDK `max_retries=0`，没有后续调用或换模型。调用前保存了输入、提示和请求参数；`run/case_1.json` 保存错误，其他四例未发起请求。网络层诊断没有调用模型：目标域名能解析；HTTP 和 HTTPS 代理 TCP 均报 `ConnectionRefusedError`（errno 111）。这与连接错误相符，但原调用的底层异常链未保存，不能断言因果。诊断见 `run/connectivity_diagnostic.json`。代码已增强，以便未来独立试验记录异常链类型和 errno；这不改变本次记录。

## 逐例

以下为原始旧记忆及预定的审查关注点，不是模型拆分结果。由于没有成功响应，所有子事实、引文及模型未决项均为 **无结果**；逐字检验、粒度、覆盖、无依据内容和语义支持均 **未执行**，人工验收亦未进行。

1. `halumem-1-s4-m1-old1`（一次请求失败）  
   旧记忆：Martin Mark Pets I like Dogs, especially Labradors reason: I love Labradors because they are friendly, loyal, and great companions for outdoor activities like jogging, which helps me stay fit.  
   待审重点：宠物偏好与多个原因、代词及保持健康之间的关系；“I” 的指代没有提供额外上下文。

2. `halumem-1-s9-m2-old0`（未调用）  
   旧记忆：Martin Mark Games I dislike Violent video games reason: I avoid violent video games because they promote aggression, which is contrary to my values of peace and well-being.  
   待审重点：不喜欢与避免、所述原因及价值观的关联；避免把说话人的理由直接提升为客观事实。

3. `halumem-1-s11-m1-old1`（未调用）  
   旧记忆：[Sep 06, 2025, 22:43:36][Persona Memory]Martin Mark Movies I like to watch Documentaries reason: I enjoy documentaries because they are informative and provide real-world insights, which complement my thirst for knowledge.  
   待审重点：记录时间与事实有效时间的区别，以及偏好、原因和知识追求的关系；不能仅因前缀而臆造有效时间。

4. `halumem-1-s16-m3-old0`（未调用）  
   旧记忆：Martin desires to continue contributing to healthcare initiatives even if he retires from his current role.  
   待审重点：保留“desires”和“even if”条件，不能断言已退休或已经继续参与。

5. `halumem-1-s3-m1-old0`（未调用）  
   旧记忆：Martin Mark is considering a career change due to health impacts from his current role.  
   待审重点：保留“considering”和健康影响这一理由，不能断言已经转职或添加具体疾病。

## 下一步

目前只能进入不调用模型的接口格式联调，不能据此认为拆分质量足以进行真实判断器试验。先修复代理或提供可用连接，再在明确授权和独立新试验记录下运行指定模型；对模型返回做逐字程序校验和逐案人工语义审核后，再评估判断器接口。原试验记录保留，不覆盖、不续跑。
