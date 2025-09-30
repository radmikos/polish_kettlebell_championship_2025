#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

const projectName = process.argv[2];
if (!projectName) {
  console.error('[sync-shared-styles] Missing project name argument.');
  process.exit(1);
}

const frontendRoot = path.resolve(__dirname, '..');
const repoRoot = path.resolve(frontendRoot, '..');
const projectDir = path.resolve(frontendRoot, projectName);
const sharedTokensPath = path.resolve(repoRoot, 'shared', 'styles', 'tokens.css');
const targetDir = path.resolve(projectDir, 'src', 'styles');
const targetFile = path.resolve(targetDir, 'tokens.css');

if (!fs.existsSync(projectDir)) {
  console.error(`[sync-shared-styles] Project directory not found: ${projectDir}`);
  process.exit(1);
}

if (!fs.existsSync(sharedTokensPath)) {
  console.error(`[sync-shared-styles] Shared tokens file missing: ${sharedTokensPath}`);
  process.exit(1);
}

fs.mkdirSync(targetDir, { recursive: true });
fs.copyFileSync(sharedTokensPath, targetFile);

console.log(`[sync-shared-styles] Copied tokens.css to ${path.relative(repoRoot, targetFile)}`);
