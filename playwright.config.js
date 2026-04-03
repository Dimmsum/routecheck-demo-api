// @ts-check
const { defineConfig } = require("@playwright/test");

module.exports = defineConfig({
  testDir: "./tests",
  timeout: 15000,
  // Single worker so shared auth tokens / created IDs are visible across tests
  workers: 1,
  fullyParallel: false,
  reporter: [["list"], ["./tests/summary-reporter.js"]],
  use: {
    baseURL: process.env.BASE_URL || "http://localhost:8001",
  },
});
