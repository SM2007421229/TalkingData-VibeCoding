# 简历优化 Agent

一个可运行的 AI Agent 应用：用于分析简历与目标岗位 JD 的匹配度，并在用户确认后生成优化版简历。

## 功能说明

- 支持上传或粘贴简历内容
- 支持输入目标 JD
- 自动分析简历与 JD 的匹配情况，输出：
  - 匹配得分
  - 匹配亮点
  - 主要缺口
  - 可执行的优化建议
- 用户确认后再生成优化版简历
- 支持下载优化简历和完整报告
- 分析结果语言与 JD 语言保持一致（中文 JD 输出中文，英文 JD 输出英文）

## 技术栈

- Python 3.11
- Streamlit（浏览器 Web UI）
- DeepSeek Chat Completions API
- Pydantic（结构化输出校验）
- Docker / Docker Compose

## 项目结构

```text
.
├── app.py
├── src
│   ├── agents
│   │   ├── analyzer.py
│   │   └── rewriter.py
│   ├── llm
│   │   └── client.py
│   ├── config.py
│   ├── exporter.py
│   ├── prompts
│   │   ├── analyze_prompt.txt
│   │   └── rewrite_prompt.txt
│   └── schemas.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

## 环境变量配置

在项目根目录创建 `.env` 文件：

```bash
DEEPSEEK_API_KEY=your_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
MODEL_NAME=deepseek-chat
REQUEST_TIMEOUT=90
```

说明：
- API Key 必须通过环境变量读取。
- 不要在源码中硬编码 API Key。

## 本地运行

```bash
pip install -r requirements.txt
streamlit run app.py
```

访问地址：`http://localhost:8501`

## Docker 运行

### 1）构建镜像

```bash
docker build -t resume-optimizer-agent .
```

### 2）启动容器

```bash
docker run --rm -p 8501:8501 --env-file .env resume-optimizer-agent
```

访问地址：`http://localhost:8501`

## Docker Compose 运行

```bash
docker compose up --build
```

访问地址：`http://localhost:8501`

## 使用步骤

1. 上传简历文件（`.txt/.md/.docx/.pdf`）或直接粘贴简历文本。
2. 粘贴目标岗位 JD。
3. 点击 `Analyze Match` 查看匹配得分、亮点、缺口和建议。
4. 点击 `Confirm and Generate Optimized Resume` 生成优化结果。
5. 下载优化简历或完整分析报告。

## 与评估点对应

- 功能完整可用：已实现从输入到分析、确认、生成、下载的完整闭环。
- Docker 部署顺畅：提供 `Dockerfile`，并附带可选 `docker-compose.yml`。
- README 清晰：包含环境变量、构建、启动、访问与使用说明。
- 代码结构合理：UI、Agent、Prompt、LLM Client、Schema、导出模块分层。
- LLM 交互清楚：结构化分析 + 用户确认后改写。
- 结果有实用价值：输出可执行建议和可直接使用的优化简历。
