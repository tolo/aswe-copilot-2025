![Let's build agentically!](assets/lets-build-agentically.jpg?raw=true)


# Agentic Software Engineering with Copilot Workshop 2025

## Prerequisites

- **GitHub account** and **GitHub Copilot** subscription
- **VS Code** with GitHub Copilot extension
- **Docker Desktop** or equivalent, for local Dev Container support
    - Alternative: Use **GitHub Codespaces**


## Getting Started

### 1. Configure VS Code
<img src="https://code.visualstudio.com/assets/docs/copilot/setup/setup-copilot-sign-in.png" width="300" alt="GitHub Copilot sign in">

- Ensure that you are logged in to your GitHub account in VS Code.
    - Read more: [Sign in to GitHub in VS Code](https://code.visualstudio.com/docs/editor/github#_sign-in-to-github)
    - And even more: [Set up Copilot in VS Code](https://code.visualstudio.com/docs/copilot/setup#_set-up-copilot-in-vs-code)
- Ensure that the [GitHub Copilot extension](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot) is installed and enabled in VS Code.
- Install the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) in VS Code.


### 2. Fork the Repository 
<img src="assets/fork.png" height="30"/>

### 3. Use Dev Container

#### Clone Project in VS Code
- Open VS Code
- Open Command Palette (`Cmd+Shift+P` or `Ctrl+Shift+P`)
- Type "Git: Clone" and select it<br/>
    <img src="assets/vscode-clone.png" height="300"/><br/>

#### Open Project in Dev Container
- When prompted by VS Code, click "Reopen in Container"<br/>
    <img src="assets/reopen-in-container.jpg" height="150"/><br/>
- If not prompted, open the Command Palette (`Cmd+Shift+P` or `Ctrl+Shift+P`), type "Dev Containers: Reopen in Container", and select it.<br/>
- Let VS Code build and start the Dev Container. _This may take several minutes on first run._

### 3 (Alternative): Use GitHub Codespaces
- Click "Code" and then "Create codespace on main" in the GitHub UI<br/>
    <img src="assets/code.png" height="30"/><br/>
    <img src="assets/codespacer.png" height="30"/>
    <br/>
- Let GitHub set up the Codespace. _This may take several minutes on first run._

### 4. Set Up Environment Variables
After project has finished loading in Dev Container or Codespace:
- Create a copy of the `.env.example` file and name it `.env`
- Add the Gemini API key to the `.env` file: **This key will be shared during the workshop** 
    ```
    GEMINI_API_KEY=your_gemini_api_key_here
    ```


## Overview of Exercises

| Exercise | Focus |
|----------|-------|
| [1. Copilot Fundamentals](docs/exercises/exercise-1-copilot-fundamentals.md) | Modes, commands, custom instructions, codebase exploration |
| [2. Bug Hunt](docs/exercises/exercise-2-bug-hunt.md) | Fix 4 planted bugs with Agent Mode |
| [3. Tool Building](docs/exercises/exercise-3-tool-building.md) | Build CLI tool, custom agents & commands |
| [4a. Cloud Feature](docs/exercises/exercise-4a-cloud-feature.md) | Copilot coding agent via GitHub Issues |
| [4b. Local Feature](docs/exercises/exercise-4b-local-feature.md) | Plan → Implement → Verify workflow |
| [5. Spec-Driven Development](docs/exercises/exercise-5-spec-driven-development.md) | GitHub Spec Kit workflow |
| [6. AI Feature Integration](docs/exercises/exercise-6-ai-feature-integration.md) | Spec Kit + OpenAI integration |
| [7. Alternative Stack](docs/exercises/exercise-7-alternative-stack.md) | Rebuild todo app in different stack (optional) |


### Todo App Commands Reference

<img src="assets/todo-app.jpg" height="600"/><br/>

The simple Todo App used in the exercises is located in the `todo-app/` folder. You can use the commands below to run and test the app. 
The app runs at http://localhost:8000 by default.

```bash
cd todo-app

## Install dependencies
uv sync

# Start app
uv run uvicorn app.main:app --reload

# Start app on custom port
uv run uvicorn app.main:app --reload --port 3000

# Run tests
uv run pytest tests/ -v
```


## Useful Links

### GitHub Copilot
https://docs.github.com/en/copilot/how-tos/configure-personal-settings/configure-in-ide

- [GitHub Copilot in VS Code cheat sheet](https://code.visualstudio.com/docs/copilot/reference/copilot-vscode-features)
- [GitHub Copilot Chat Cookbook](https://docs.github.com/copilot/tutorials/copilot-chat-cookbook)

#### Specific topics
- [Custom Instructions](https://docs.github.com/en/copilot/customizing-copilot/adding-repository-custom-instructions-for-github-copilot)
- [Chat Checkpoints](https://code.visualstudio.com/docs/copilot/chat/chat-checkpoints)
- [GitHub Custom Agents Configuration](https://docs.github.com/en/copilot/reference/custom-agents-configuration)
- [Copilot Chat Cookbook](https://docs.github.com/en/copilot/tutorials/copilot-chat-cookbook)
- [About Copilot Coding Agent](https://docs.github.com/en/copilot/concepts/agents/coding-agent/about-coding-agent)

#### Customizing Copilot
- [GitHub Customization Library](https://docs.github.com/en/copilot/tutorials/customization-library)
- [Awesome Copilot](https://github.com/github/awesome-copilot)


### Prompt/Context Engineering Guides
- [GitHub Copilot Prompt Engineering Guide](https://docs.github.com/en/copilot/concepts/prompting/prompt-engineering)
- [Claude - Best Practices for Prompt Engineering](https://www.claude.com/blog/best-practices-for-prompt-engineering)
- [Anthropic - Effective Context Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [GPT-5 Prompting Guide](https://cookbook.openai.com/examples/gpt-5/gpt-5_prompting_guide)


### Dev Containers
- [Dev Containers](https://containers.dev)
- [Dev Containers Features](https://containers.dev/features)
- [VS Code - Developing inside a Container](https://code.visualstudio.com/docs/devcontainers/containers)
- [JetBrains - Connect to Dev Container](https://www.jetbrains.com/help/idea/connect-to-devcontainer.html)


### Useful Tools
- [GitHub Spec Kit](https://github.com/github/spec-kit)
- [Gitingest](https://gitingest.com/)
- [The /llms.txt file](https://llmstxt.org)


### Useful MCP servers
- [Fetch - Downloading web content as markdown](https://github.com/modelcontextprotocol/servers/tree/main/src/fetch)
- [Context 7 - Documentation lookup](https://github.com/upstash/context7)
- [Ref.tools - Documentation lookup](https://ref.tools/)
- [Chrome DevTools MCP](https://github.com/ChromeDevTools/chrome-devtools-mcp)
- [Playwright MCP](https://github.com/microsoft/playwright-mcp)
- [Sequential Thinking](https://github.com/modelcontextprotocol/servers/tree/main/src/sequentialthinking)


### Interesting Readings / Viewing
- [Simon Willison - The Lethal Trifecta](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/)
- [YouTube - The Message Every Engineer Needs to Hear](https://www.youtube.com/watch?v=XKCBcScElBg)
- More coming soon...
