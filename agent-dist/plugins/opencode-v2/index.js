import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const MARKER = "<quinotospec-bootstrap>";

function findRoot(location) {
  const localCandidate =
    location && typeof location.directory === "string" && location.directory
      ? path.join(location.directory, ".opencode")
      : null;
  const candidates = [
    ...(localCandidate ? [localCandidate] : []),
    path.resolve(__dirname, "../.."),
    path.resolve(__dirname, "../../.."),
  ];
  for (const candidate of candidates) {
    if (fs.existsSync(path.join(candidate, "skills")) || fs.existsSync(path.join(candidate, "bootstrap"))) {
      return path.resolve(candidate);
    }
  }
  return path.resolve(__dirname, "../..");
}

function loadBootstrap(root) {
  const file = path.join(root, "bootstrap", "quinotospec-bootstrap.md");
  if (!fs.existsSync(file)) {
    return "# QuinotoSpec\n\nAplica Proposal First y valida el contrato antes de modificar artefactos.";
  }
  const raw = fs.readFileSync(file, "utf8");
  const match = raw.match(/^---\s*\r?\n[\s\S]*?\r?\n---\s*\r?\n/);
  return (match ? raw.slice(match[0].length) : raw).trim();
}

const bootstrapCache = new Map();
function getBootstrap(root) {
  if (!bootstrapCache.has(root)) {
    bootstrapCache.set(root, loadBootstrap(root));
  }
  return bootstrapCache.get(root);
}

function makeHook(bootstrap) {
  return (event) => {
    if (!event || !Array.isArray(event.system)) {
      return;
    }
    const alreadyInjected = event.system.some((entry) => {
      if (typeof entry === "string") {
        return entry.includes(MARKER);
      }
      return Boolean(entry && typeof entry.text === "string" && entry.text.includes(MARKER));
    });
    if (alreadyInjected) {
      return;
    }
    event.system.push({ type: "text", text: `${MARKER}\n${bootstrap}\n</quinotospec-bootstrap>` });
  };
}

export default {
  id: "quinotospec",
  async setup(ctx) {
    const root = findRoot(ctx.location);
    const bootstrap = getBootstrap(root);
    const hook = makeHook(bootstrap);

    await ctx.session.hook("context", hook);
    await ctx.session.hook("compaction", hook);

    if (ctx.options?.verbose === true) {
      console.log(`[quinotospec] loaded for OpenCode ${ctx.app.version} at ${root}`);
    }
  },
};