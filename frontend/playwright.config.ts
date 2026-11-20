import { randomBytes } from "node:crypto";
import { mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { defineConfig, devices } from "@playwright/test";

// The built SPA served by FastAPI, as in use, on its own port and folder, so
// the dev installation's data is never touched. The config also runs in each
// worker: the values are set once and the workers inherit them.
const port = 8767;
const origin = `http://127.0.0.1:${String(port)}`;
process.env.EPISTEME_E2E_TOKEN ??= randomBytes(32).toString("base64url");
process.env.EPISTEME_E2E_HOME ??= mkdtempSync(
  path.join(tmpdir(), "episteme-e2e-"),
);

export default defineConfig({
  testDir: "e2e",
  globalTeardown: "./e2e/teardown.ts",
  forbidOnly: Boolean(process.env.CI),
  use: { baseURL: origin, trace: "retain-on-failure" },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
  webServer: {
    command: "uv run --locked --project ../backend episteme-server",
    url: `${origin}/api/health`,
    reuseExistingServer: false,
    env: {
      EPISTEME_ENV: "dev",
      EPISTEME_HOME: process.env.EPISTEME_E2E_HOME,
      EPISTEME_PORT: String(port),
      EPISTEME_API_TOKEN: process.env.EPISTEME_E2E_TOKEN,
      // One-time links point at the web origin: here, the server itself.
      EPISTEME_DEV_ORIGIN: origin,
    },
  },
});
