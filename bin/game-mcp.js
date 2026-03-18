#!/usr/bin/env node

import { main, mainFromConfig, printHelp } from '../lib/index.js';

const args = process.argv.slice(2);

if (args.includes('--help') || args.includes('-h')) {
  printHelp();
  process.exit(0);
}

const configIdx = args.indexOf('--config');
if (configIdx !== -1) {
  const configPath = args[configIdx + 1];
  if (!configPath) {
    console.error('Error: --config requires a file path argument');
    console.error('Usage: npx game-mcp --config config.json');
    process.exit(1);
  }
  mainFromConfig(configPath).catch((err) => {
    console.error(err.message || err);
    process.exit(1);
  });
} else {
  main().catch((err) => {
    console.error(err.message || err);
    process.exit(1);
  });
}
