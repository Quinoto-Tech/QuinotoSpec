import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const MARKER = "<quinotospec-bootstrap>";

function findRoot(location) {
  const candidates = [
    path.join(location.directory, ".opencode"),
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

let cachedBootstrap = null;
function getBootstrap(root) {
  if (cachedBootstrap === null) {
    cachedBootstrap = loadBootstrap(root);
  }
  return cachedBootstrap;
}

function makeHook(bootstrap) {
  return (event) => {
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