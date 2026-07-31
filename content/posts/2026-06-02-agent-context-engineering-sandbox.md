---
title: "Agent 学习路线：Context 工程、数据库和沙盒"
date: 2026-06-02T16:00:00+08:00
draft: false
tags: ["Agent", "Context 工程", "数据库", "Sandbox"]
categories: ["AI 工程"]
summary: "今天重新梳理了 Agent 领域接下来要抓的重点：面试知识是一部分，但真正值得继续深入的是 context 工程、数据库和沙盒。"
---

今天觉得 Agent 领域最重点的知识，其实也不算重点。因为这些知识其实只是为了面向面试、找工作用的，真正开发的时候未必直接用得上。

不过我觉得数据库是下一个重点，因为大模型里面的 memory 本质上就是 context，而 context 工程其实是跟数据库紧密结合的。这些内容本质上也都是后端的东西。

所以今天最重点的东西，其实就是 context 工程，尤其是 **OpenViking + SeekDB** 这一块。

下一个重点是沙盒，也就是 sandbox。这里可以重点关注 **Firecracker**，以及 SDK 层面的 **E2B**。
