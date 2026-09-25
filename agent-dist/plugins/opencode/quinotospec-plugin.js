const fs = require("node:fs");
const path = require("node:path");

const MARKER = "<quinotospec-bootstrap>";
const TOOL_ALIASES = Object.freeze({ TodoWrite: "todowrite", Task: "task" });
let cachedBootstrap = null;

function unique(values) {
  return [...new Set(values.filter(Boolean))];
}

function findRoot(context) {
  const candidates = [
    context.configDir,
    context.directory ? path.join(context.directory, ".opencode") : undefined,
    context.worktree ? path.join(context.worktree, ".opencode") : undefined,
    path.resolve(__dirname, ".."),
    path.resolve(__dirname, "../.."),
  ].filter(Boolean);
  for (const candidate of candidates) {
    if (fs.existsSync(path.join(candidate, "skills")) || fs.existsSync(path.join(candidate, "bootstrap"))) {
      return path.resolve(candidate);
    }
  }
  return path.resolve(__dirname, "..");
}

function bootstrapPath(context) {
  const root = findRoot(context);
  return path.join(root, "bootstrap", "quinotospec-bootstrap.md");
}

function loadBootstrap(context) {
  if (cachedBootstrap !== null) return cachedBootstrap;
  const file = bootstrapPath(context);
  if (!fs.existsSync(file)) {
    cachedBootstrap = "# QuinotoSpec\n\nAplica Proposal First y valida el contrato antes de modificar artefactos.";
    return cachedBootstrap;
  }
  const raw = fs.readFileSync(file, "utf8");
  const match = raw.match(/^---\s*\r?\n[\s\S]*?\r?\n---\s*\r?\n/);
  cachedBootstrap = (match ? raw.slice(match[0].length) : raw).trim();
  return cachedBootstrap;
}

function messageText(message) {
  if (!message) return "";
  if (typeof message.content === "string") return message.content;
  if (!Array.isArray(message.content)) return "";
  return message.content.map((part) => (typeof part === "string" ? part : part && part.text ? part.text : "")).join("\n");
}

function prependMessage(message, content) {
  const prefix = `${MARKER}\n${content}\n</quinotospec-bootstrap>\n\n`;
  if (typeof message.content === "string" || message.content === undefined) {
    message.content = prefix + (message.content || "");
    return;
  }
  if (Array.isArray(message.content)) {
    message.content.unshift({ type: "text", text: prefix });
  }
}

function injectMessages(input, output) {
  const target = output || {};
  const messages = Array.isArray(target.messages) ? target.messages : Array.isArray(input && input.messages) ? input.messages : [];
  const firstUser = messages.find((message) => message && message.role === "user");
  if (!firstUser || messageText(firstUser).includes(MARKER)) return;
  prependMessage(firstUser, loadBootstrap({}));
}

function injectSystem(input, output) {
  const target = output || {};
  const context = loadBootstrap({});
  if (typeof target.system === "string" && !target.system.includes(MARKER)) {
    target.system = `${MARKER}\n${context}\n</quinotospec-bootstrap>\n\n${target.system}`;
  } else if (Array.isArray(target.context) && !target.context.some((item) => typeof item === "string" && item.includes(MARKER))) {
    target.context.unshift(`${MARKER}\n${context}\n</quinotospec-bootstrap>`);
  }
}

async function QuinotoSpecBootstrapPlugin(context = {}) {
  const root = findRoot(context);
  const file = bootstrapPath(context);
  const workflowDir = fs.existsSync(path.join(root, "commands")) ? path.join(root, "commands") : path.join(root, "workflows");
  return {
    toolAliases: TOOL_ALIASES,
    config(config) {
      const live = config || {};
      live.instructions = unique([
        ...(Array.isArray(live.instructions) ? live.instructions : []),
        file,
        path.join(root, "rules"),
        workflowDir,
        path.join(root, "agents"),
      ]);
      live.skills = live.skills || {};
      live.skills.paths = unique([...(live.skills.paths || []), path.join(root, "skills")]);
      live.tools = live.tools || {};
      live.tools.todowrite = live.tools.todowrite !== false;
      live.tools.task = live.tools.task !== false;
      return live;
    },
    "experimental.chat.messages.transform": async (input, output) => {
      injectMessages(input, output);
    },
    "experimental.chat.system.transform": async (input, output) => {
      injectSystem(input, output);
    },
  };
}

module.exports = QuinotoSpecBootstrapPlugin;
module.exports.default = QuinotoSpecBootstrapPlugin;
module.exports.QuinotoSpecBootstrapPlugin = QuinotoSpecBootstrapPlugin;
