"""Render post-hoc reviews without changing model outputs or production files."""
from collections import Counter
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LABEL = "初步判断，待人工确认"


def read(path):
    return json.loads(path.read_text())


def save(path, value):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def write(path, content):
    if path.exists():
        assert path.read_text() == content, "Existing rendered report differs; do not overwrite."
        return
    with path.open("x", encoding="utf-8") as stream:
        stream.write(content)


def cell(value):
    return str(value).replace("|", "\\|").replace("\n", "<br>")


def descriptions(values):
    return "；".join(x if isinstance(x, str) else json.dumps(x, ensure_ascii=False) for x in values)


def table(headers, rows):
    return "\n".join(["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"] +
                     ["| " + " | ".join(cell(x) for x in row) + " |" for row in rows])


def csvfile(name, rows):
    with (ROOT / name).open("x", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def issue_types(review):
    return sorted({t for f in review["facts"] for t in f["observed_issue_types"]})


def statistics(records):
    issues_case, issues_fact, supports, coverage = Counter(), Counter(), Counter(), Counter()
    for a in records:
        issues_case.update(issue_types(a))
        for f in a["facts"]:
            issues_fact.update(set(f["observed_issue_types"]))
            supports.update(e["assessment"] for e in f["supports"])
        coverage.update(u["status"] for u in a["coverage_units"])
    return {
        "cases": len(records), "facts": sum(len(a["facts"]) for a in records),
        "cases_with_observed_issue": sum(bool(issue_types(a)) for a in records),
        "facts_with_observed_issue": sum(bool(f["observed_issue_types"]) for a in records for f in a["facts"]),
        "cases_with_specific_uncertainty": sum(bool(a.get("uncertainties")) or any(f.get("uncertainties") for f in a["facts"]) for a in records),
        "issue_types_case_counts": dict(sorted(issues_case.items())),
        "issue_types_fact_counts": dict(sorted(issues_fact.items())),
        "supports_assessments": dict(supports), "coverage_unit_assessments": dict(coverage),
        "all_semantic_reviews_await_human": True,
    }


def main():
    selection = read(ROOT / "selection.json")["cases"]
    cases = []
    for group in range(1, 4):
        data = read(ROOT / "reviews" / f"paired_group_{group:02d}.json")
        assert data["review_label"] == LABEL
        cases.extend(data["cases"])
    cases.sort(key=lambda c: c["case_id"])
    assert [c["case_id"] for c in cases] == [c["case_id"] for c in selection]
    case_rows, fact_rows, support_rows, coverage_rows = [], [], [], []
    for case, chosen in zip(cases, selection):
        cid = case["case_id"]
        contents = ["# " + cid, "", "**" + LABEL + "**。程序检查与语义初审分别记录，未改模型输出。", "",
                    "memory_id：`" + chosen["memory_id"] + "`", "", "选择理由：" + chosen["selection_reason"], "",
                    "更新前快照：`" + chosen["snapshot_source"] + "#" + chosen["snapshot_json_pointer"] + "`", "",
                    "完整旧上下文与来源见 [CASE_CATALOG](../CASE_CATALOG.md#" + cid + ") 和 [输入](../inputs/" + cid + ".json)。", "",
                    "旧记忆原文：", "", "```text", chosen["memory_text"], "```", ""]
        for version in ("v3", "v4"):
            review = case["versions"][version]
            directory = ROOT / "runs" / cid / version
            program = read(directory / "program_checks.json")
            raw = read(directory / "raw_content.txt")
            facts = raw["facts"]
            assert len(review["facts"]) == len(facts)
            assert review["program_status"] == program["program_status"]
            quotes = [e for f in program["facts"] for e in f["evidence_checks"]]
            case_rows.append({
                "case_id": cid, "cohort": chosen["cohort"], "version": version, "memory_id": chosen["memory_id"],
                "program_status": program["program_status"], "fact_count": len(facts),
                "quotes_passed": sum(e["exact_substring"] for e in quotes), "quotes_total": len(quotes),
                "observed_issue_types": ";".join(issue_types(review)),
                "has_specific_uncertainty": bool(review.get("uncertainties")) or any(f.get("uncertainties") for f in review["facts"]),
                "summary": review["summary"], "review_label": LABEL,
            })
            contents += ["## " + version, "", "程序：" + program["program_status"] + "；候选事实 " + str(len(facts)) +
                         " 条；逐字引文 " + str(sum(e["exact_substring"] for e in quotes)) + "/" + str(len(quotes)) + "。", "",
                         "[原始响应](../runs/" + cid + "/" + version + "/raw_content.txt) · [实际提示词](../runs/" + cid + "/" + version +
                         "/prompt.txt) · [逐项程序检查](../runs/" + cid + "/" + version + "/program_checks.json)", "", review["summary"], ""]
            for fact, fr, pc in zip(facts, review["facts"], program["facts"]):
                assert fact["fact_index"] == fr["fact_index"]
                assert len(fr["supports"]) == len(fact["evidence"])
                assert [e["evidence_index"] for e in fr["supports"]] == list(range(len(fact["evidence"])))
                fact_rows.append({
                    "case_id": cid, "cohort": chosen["cohort"], "version": version, "fact_index": fact["fact_index"],
                    "program_status": program["program_status"], "memory_evidence_passed": pc["memory_id_and_quote_check"],
                    "old_memory": chosen["memory_text"], "raw_subfact": fact["raw_subfact"],
                    "contextualized_subfact": fact["contextualized_subfact"], "observed_issue_types": ";".join(fr["observed_issue_types"]),
                    "fidelity_review": fr["fidelity_review"], "uncertainties": json.dumps(fr["uncertainties"], ensure_ascii=False),
                    "model_pending_confirmations": json.dumps(fact["pending_confirmations"], ensure_ascii=False), "review_label": LABEL,
                })
                contents += ["### 事实 " + str(fact["fact_index"]), "", "raw：", "", "```text", fact["raw_subfact"], "```", "",
                             "contextualized：", "", "```text", fact["contextualized_subfact"], "```", "",
                             "程序：编号=" + str(pc["consecutive_index"]) + "；事实 ID=" + str(pc["source_memory_id_match"]) +
                             "；memory 引文=" + str(pc["memory_id_and_quote_check"]) + "；全部逐字引文=" + str(pc["all_quotes_match"]) + "。", "",
                             fr["fidelity_review"], "", "观察到的问题：" + ("、".join(fr["observed_issue_types"]) or "未观察到明确问题") + "。", ""]
                for finding in fr["findings"]:
                    contents += ["- " + finding["type"] + "：输入 `" + finding["input_span"] + "`；输出 `" + finding["output_span"] + "`。" + finding["reason"], ""]
                for eindex, (evidence, er) in enumerate(zip(fact["evidence"], fr["supports"])):
                    support_rows.append({
                        "case_id": cid, "version": version, "fact_index": fact["fact_index"], "evidence_index": eindex,
                        **evidence, "assessment": er["assessment"], "issue_types": ";".join(er["issue_types"]), "reason": er["reason"], "review_label": LABEL,
                    })
                    contents += ["引文 " + str(eindex) + "：`" + evidence["source_type"] + "/" + evidence["source_id"] + "`", "",
                                 "```text", evidence["quote"], "```", "", "supports 原文：", "", "```text", evidence["supports"], "```", "",
                                 "支持范围初审：" + er["assessment"] + "。" + er["reason"], ""]
                contents += ["模型 pending_confirmations（原样保留）：", "", "```json", json.dumps(fact["pending_confirmations"], ensure_ascii=False, indent=2), "```", "",
                             "初审待确认：" + (descriptions(fr["uncertainties"]) or "本条未另列具体未决项，仍待人工复核") + "。", ""]
            contents += ["覆盖与拆分粒度：", "", table(["信息点", "输入原文", "raw/补充事实序号", "初审", "理由"],
                          [[u["unit"], u["input_span"], str(u["raw_fact_indices"]) + "/" + str(u["contextualized_fact_indices"]), u["status"], u["reason"]] for u in review["coverage_units"]]),
                         "", review["granularity_observation"], "", "案例未决项：" + (descriptions(review["uncertainties"]) or "无另列具体未决项，仍待人工确认") + "。", ""]
            for u in review["coverage_units"]:
                coverage_rows.append({"case_id": cid, "version": version, **{k: json.dumps(v, ensure_ascii=False) if isinstance(v, list) else v for k, v in u.items()}, "review_label": LABEL})
        contents += ["## 配对比较", ""]
        for key, title in (("improvements", "改善"), ("persistent", "持续问题/相同观察"), ("regressions", "本轮新增问题"), ("uncertainties", "配对解释限制")):
            contents += [title + "：", ""] + (["- " + x for x in case["comparison"][key]] or ["未观察到明确项。"] ) + [""]
        write(ROOT / "reviews" / (cid + ".md"), "\n".join(contents))
    summary = {"review_label": LABEL, "versions": {}, "cohorts": {}, "not_a_gold_error_rate": True,
               "paired_comparisons": [{"case_id": c["case_id"], **c["comparison"]} for c in cases]}
    for version in ("v3", "v4"):
        summary["versions"][version] = statistics([c["versions"][version] for c in cases])
    for cohort in ("regression_7", "new_compound_4"):
        ids = {c["case_id"] for c in selection if c["cohort"] == cohort}
        summary["cohorts"][cohort] = {version: statistics([c["versions"][version] for c in cases if c["case_id"] in ids]) for version in ("v3", "v4")}
    save(ROOT / "semantic_reviews.json", {"review_label": LABEL, "cases": cases})
    save(ROOT / "semantic_summary.json", summary)
    csvfile("case_review.csv", case_rows)
    csvfile("fact_review.csv", fact_rows)
    csvfile("supports_review.csv", support_rows)
    csvfile("coverage_review.csv", coverage_rows)
    program = read(ROOT / "program_summary.json")["versions"]
    contents = ["# v3 / v4 真实旧记忆配对测试", "", "**" + LABEL + "。全部语义复核由 AI 完成，未经过人工最终确认。**", "",
                "使用相同输入对现有7条案例和新增4条复合记忆各测试 v3/v4 一次。旧7条是提示词调整所依据的回归样本，新增4条是不同旧记忆探针；不能将回归改善当独立泛化结果。", "",
                "v4 只调整 raw 来源边界、单条 supports 的支持范围及正文与待确认一致性；未修改解析器/校验器/输出结构。v3 默认 DESIGN.md 保留，v4 见 [新版本](../../prompt_versions/v4_boundaries_20261104/CHANGELOG.md)。", "",
                "运行：qwen-plus；两版本各11次，共22次真实请求；每版本/案例1次；SDK重试0，HTTP自动跳转false；response_format=json_object，timeout=180秒；显式 generation_parameters={}。温度、token上限、seed、具体模型修订和服务端路由未能确认。版本按案例交错并轮换先后，实际顺序见 [调用记录](batch_attempt.json) 和 [完成记录](batch_completion.json)。同输入、同显式参数不能保证服务端确定性，单轮差异仅为观察。", "",
                "程序检查：", "", table(["版本", "案例通过", "接受事实", "逐字引文", "memory 引文事实"],
                 [[v, str(program[v]["program_passed"]) + "/" + str(program[v]["case_count"]), program[v]["accepted_facts"],
                   str(program[v]["literal_quotes_passed"]) + "/" + str(program[v]["literal_quotes_total"]), program[v]["facts_with_memory_passed"]] for v in ("v3", "v4")]), "",
                "上述仅检查格式、ID、来源编号及引文逐字匹配。supports 语义、覆盖和身份归属由下述初审检查，不能由程序通过推出正确。失败候选应保留 raw_content、失败状态和诊断，禁止自动补引文、改标或写成通过结果。", "",
                "逐案例结果（类型计数有重叠）：", "", table(["案例/明细", "队列", "v3事实/问题", "v4事实/问题"],
                 [["[" + c["case_id"] + "](reviews/" + c["case_id"] + ".md)", s["cohort"],
                   str(len(c["versions"]["v3"]["facts"])) + " / " + ("、".join(issue_types(c["versions"]["v3"])) or "未观察到明确项"),
                   str(len(c["versions"]["v4"]["facts"])) + " / " + ("、".join(issue_types(c["versions"]["v4"])) or "未观察到明确项")] for c, s in zip(cases, selection)]), "",
                "语义问题类型按案例统计（非人工错误率；同一案例可多类型）：", ""]
    types = sorted({t for v in summary["versions"].values() for t in v["issue_types_case_counts"]})
    contents += [table(["类型", "v3", "v4"], [[t, summary["versions"]["v3"]["issue_types_case_counts"].get(t, 0), summary["versions"]["v4"]["issue_types_case_counts"].get(t, 0)] for t in types]), "",
                 "按队列区分：", "", table(["队列", "版本", "观察到问题案例", "有具体未决案例", "事实数"],
                  [[cohort, v, x["cases_with_observed_issue"], x["cases_with_specific_uncertainty"], x["facts"]] for cohort, versions in summary["cohorts"].items() for v, x in versions.items()]), "",
                 "全部22份输出及每条事实均待人工确认；有具体未决项的案例另列，不等于错误。partial supports 不自动记错；单条事实合并多个已覆盖信息点也不自动记遗漏。复合覆盖的逐信息点判断见 [coverage_review.csv](coverage_review.csv)。", "",
                 "[输入、上下文与来源](CASE_CATALOG.md) · [selection.json](selection.json) · [历史来源核验](source_provenance.json) · [程序细项](program_summary.json) · [逐事实表](fact_review.csv) · [逐引文支持表](supports_review.csv) · [语义汇总](semantic_summary.json) · [综合判断与下一步建议](ASSESSMENT.md)", "",
                 "本轮未调用 Mem0、不写知识库、不执行新旧事实关系判断或完整开发子集；未把新证据、标注或初审结果写入模型输入，未改写任何模型响应。保留 v1/v2/v3 和全部历史文件，最终完整性核验见 final_verification.json。", ""]
    write(ROOT / "COMPARISON_REPORT.md", "\n".join(contents))
    print(json.dumps(summary["versions"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
