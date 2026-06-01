# Claude Code Website Builder Setup

One command to turn Claude Code into a professional website building machine.

## What It Installs

| Tool | What It Does |
|------|-------------|
| **Framer Motion** | Smooth animations for React |
| **UI/UX Pro Max** | Claude skill for world-class UI design |
| **Prompt Engineering** | Claude skill for writing, refining, and debugging prompts |
| **Magic MCP (21st.dev)** | Instant access to 21st.dev's component library inside Claude Code |

## One-Line Setup

```bash
curl -fsSL https://raw.githubusercontent.com/ralphwestworld/claude-website-setup/main/setup.sh | bash
```

With your 21st.dev API key:

```bash
curl -fsSL https://raw.githubusercontent.com/ralphwestworld/claude-website-setup/main/setup.sh | MAGIC_API_KEY=your_key_here bash
```

Get your free API key at [21st.dev](https://21st.dev) → Settings → API Keys

## Manual Run

```bash
git clone https://github.com/ralphwestworld/claude-website-setup
cd claude-website-setup
bash setup.sh your_21st_api_key
```

## After Setup

Open Claude Code in your project and say:

> "Build me a landing page with smooth scroll animations and a hero section"

Claude will automatically use Framer Motion for animations, pull production-ready components from 21st.dev, and apply professional UI/UX standards throughout.

The Prompt Engineering skill also kicks in whenever you ask Claude to write or improve a prompt — for example:

> "Improve this prompt so the model stops ignoring my formatting instructions"
