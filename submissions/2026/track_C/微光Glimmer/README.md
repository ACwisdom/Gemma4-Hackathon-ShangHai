# 微光 Glimmer

Track: 赛道 C - Edge AI
Team: enactflow
Canonical repository: https://github.com/chenghuzi/glimmer
Model weights: https://huggingface.co/chenghuzi/glimmer-e4b-asd9-gguf
iOS TestFlight: https://testflight.apple.com/join/5S8qS56v
Demo video: 随 hackathon 官方提交表单提供。

<p align="center">
  <a href="https://testflight.apple.com/join/5S8qS56v">
    <img src="source/assets/readme/testflight-qr.png" width="160" alt="Glimmer TestFlight QR code" />
  </a>
</p>
<p align="center">
  <sub>扫码或点击加入微光 Glimmer iOS TestFlight 测试。</sub>
</p>

## Project Summary

微光 Glimmer 是一个基于 Gemma 4 E4B 的端侧多模态行为信号筛查项目。模型针对儿童 ASD 相关可观察行为信号进行任务化微调，在 iPhone 和 macOS 上完成离线多模态推理；用户视频、报告和后续解释对话不会上传到服务器。

项目不提供医学诊断，也不替代医生或专业机构评估。它的目标是把一部分行为观察线索结构化出来，帮助家庭更早意识到某段视频中是否出现了需要进一步关注的信号。

## Why Track C - Edge AI

微光的核心能力发生在端侧：

- Gemma 4 E4B 在 iPhone 和 macOS 本地运行，用视频帧、音频和文本指令完成多模态推理。
- 推理输出被约束为 9-bit behavior code，用于稳定表示 B01-B09 行为信号。
- app 在本地生成报告，并支持围绕同一段视频继续进行解释对话。
- 除首次下载模型权重外，用户视频、音频、报告和聊天内容都留在设备本地。

## Source Snapshot

本提交目录中的 `source/` 是一份便于评审查看的清理版源码快照。项目的原始维护仓库为：

https://github.com/chenghuzi/glimmer

原始仓库包含 iOS/macOS app 构建所需的 vendor runtime artifacts，例如 `.xcframework` 文件。如果本 PR 快照中省略了较大的二进制 runtime 文件，请以 canonical repository 作为完整构建上下文。

## Key Links

- Canonical repository: https://github.com/chenghuzi/glimmer
- GGUF model weights: https://huggingface.co/chenghuzi/glimmer-e4b-asd9-gguf
- iOS TestFlight: https://testflight.apple.com/join/5S8qS56v
- Source snapshot: `source/`
- Main app source: `source/glimmer-ios/`
- Training and evaluation entry points: `source/run_train.py`, `source/eval_gguf_llama_cpp.py`

## Team Contributions

- Idea: [chenghuzi](https://github.com/chenghuzi), [panggungunvibe](https://github.com/panggungunvibe)
- Model training and deployment: [chenghuzi](https://github.com/chenghuzi)
- iOS/macOS app development and design: [chenghuzi](https://github.com/chenghuzi), [zhangdongming0607](https://github.com/orgs/enactflow/people/zhangdongming0607), [ixiongzai](https://github.com/orgs/enactflow/people/ixiongzai)
- Video and report: [chenghuzi](https://github.com/chenghuzi), [panggungunvibe](https://github.com/panggungunvibe), [rongmiao926-hub](https://github.com/orgs/enactflow/people/rongmiao926-hub)
