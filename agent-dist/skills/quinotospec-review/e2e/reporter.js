import fs from "node:fs";
import path from "node:path";

export default class QuinotoSpecReporter {
  constructor(options = {}) {
    const base = process.env.QS_OUTPUT_DIR || "test-results";
    this.outputFile = options.outputFile || path.join(base, "playwright-tests.json");
    this.tests = [];
  }

  onTestEnd(test, result) {
    this.tests.push({
      title: test.title,
      status: result.status,
      duration_ms: result.duration,
      errors: (result.errors || []).map((error) => error.message || String(error)),
    });
  }

  onEnd(result) {
    fs.mkdirSync(path.dirname(this.outputFile), { recursive: true });
    fs.writeFileSync(
      this.outputFile,
      JSON.stringify({ status: result.status, tests: this.tests }, null, 2) + "\n",
      "utf-8",
    );
  }
}
