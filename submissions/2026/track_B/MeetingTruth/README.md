# MeetingTruth

MeetingTruth 是一个 macOS 端会议事实复核应用。它不把单一路 ASR 转写直接当作会议真相，而是把多路候选转写、会议通知、手写稿、PPT/图片和人工确认组织成证据链，再用 Gemma 4 做冲突发现、证据核验和成果生成。

它解决的问题是：会议纪要里最容易错的人名、金额、时间、项目名和专业术语，往往会被普通“ASR + 总结”流程直接写进最终文档。MeetingTruth 在生成纪要前先找出不一致，标出证据来源，把低置信内容留给人工确认。

## 五步流程

1. 导入会议音频或加载示例数据。
2. 生成或读取多路 ASR 候选转写。
3. 加入会议通知、手写稿、PPT、图片和术语材料。
4. Gemma 4 通过 function calling 调用本地工具，完成候选抽取、冲突检测、证据检索、候选评分、事实裁决和人工确认任务创建。
5. 输出可信转写、冲突卡片、确认事项、纪要、摘要、待办和思维导图。

## Gemma 4 用在哪里

正式演示推荐 `google/gemma-4-12b`。它负责理解长上下文、多路候选差异、工具返回结果和会议成果结构。`google/gemma-4-e4b` 保留为轻量测试或低配机器备用配置。

Gemma 4 通过 OpenAI-compatible `/v1/chat/completions` 接口接入，可使用 LM Studio 或其他兼容服务。

## 多模态用在哪里

截图、白板、手写稿和图片材料会作为原图输入给 Gemma 4，同时 OCR 提供可搜索的文字线索。OCR 用来定位，Gemma 多模态用来复核可见数字、术语、版面和手写痕迹；两者都进入证据链，不会单独覆盖人工确认和最终裁决。

## Function Calling 的作用

MeetingTruth 使用 Gemma native `tool_call`，由 Swift 执行本地工具并回填 `tool_response`。当前真实工具链是：

- `extract_meeting_fact_candidates`
- `filter_reviewable_facts`
- `detect_asr_conflicts`
- `retrieve_supporting_evidence`
- `score_fact_candidates`
- `make_fact_decision`
- `create_human_review_task`

如果 endpoint 不返回原生 `tool_calls`，Swift `autoPipeline` 会按同一工具链自动补全关键步骤；`localRule` 会做基础规则校验，保证演示和新机器测试仍能看到可审计流程。

## 快速运行

一键打包：

```bash
./package-clean-submission.sh
```

构建 App：

```bash
cd source/MeetingTruthMacApp
swift build -c release --product MeetingTruth
```

构建后可运行：

```bash
.build/release/MeetingTruth
```

生成并打开 macOS App：

```bash
./script/build_app.sh --verify
```

## 加载示例

如果新机器还没有下载 ASR 模型，也可以直接打开 App，在「会议整理」中点击「加载示例」。示例数据由 App 内置，包含候选转写、会议通知、手写稿和图片材料，可用于测试 MeetingTruth 的冲突检测、多模态复核、function calling、人工确认和成果生成。

提交包中的 `sample-data/` 只放外部示例说明；App 内置示例数据不依赖额外下载。

Demo 视频位于：

```text
assets/demo-video/演示介绍.mp4
```

## 当前限制

- 本地 ASR 模型权重不随提交包提供，需要在 App 的「模型准备」中下载。
- Gemma 4 复核需要可用的 OpenAI-compatible endpoint。
- 未配置 Developer ID 时只能本机构建运行，不能替代正式签名和公证。
- Intel Mac 可以构建 App，但默认 MLX ASR runtime 主要面向 Apple Silicon。
