import { readFileSync, unlinkSync } from 'node:fs';
import { createHash } from 'node:crypto';
import chalk from 'chalk';
import { collectAnswers } from './prompts.js';
import { collectSecrets } from './secrets.js';
import { scaffold } from './scaffold.js';
import { installDeps } from './deps.js';
import { launchTools } from './launcher.js';
import { validateConfig, normalizeConfig } from './validate.js';

function hashSecret(value) {
  return createHash('sha256').update(value).digest('hex');
}

// Interactive mode — terminal users
export async function main() {
  console.log('');
  console.log(chalk.bold.cyan('  Game MCP') + chalk.dim(' — Multi-Agent Game Development Framework'));
  console.log(chalk.dim('  Powered by Claude Code + MCP'));
  console.log('');

  // Step 1: Collect project info
  const answers = await collectAnswers();

  // Step 2: Collect API secrets
  const secrets = await collectSecrets(answers.gameType, answers.integrations);

  // Step 3: Scaffold project
  await scaffold(answers, secrets);

  // Step 4: Install dependencies
  await installDeps(answers);

  // Step 5: Launch tools
  await launchTools(answers);

  printNextSteps(answers);
}

// Non-interactive mode — Claude Code Desktop / CI
export async function mainFromConfig(configPath) {
  console.log('');
  console.log(chalk.bold.cyan('  Game MCP') + chalk.dim(' — Non-Interactive Setup'));
  console.log('');

  // Read and validate config
  let raw;
  try {
    raw = JSON.parse(readFileSync(configPath, 'utf-8'));
  } catch (err) {
    console.error(chalk.red(`  Failed to read config: ${err.message}`));
    process.exit(1);
  }

  const { valid, errors } = validateConfig(raw);
  if (!valid) {
    console.error(chalk.red('  Config validation failed:'));
    for (const e of errors) {
      console.error(chalk.red(`    - ${e}`));
    }
    process.exit(1);
  }

  const config = normalizeConfig(raw);

  // Build answers object (same shape as interactive mode)
  const answers = {
    gameName: config.gameName,
    gameCode: config.gameCode,
    gameType: config.gameType,
    integrations: config.integrations,
    gitProvider: config.gitProvider,
    gitRemote: config.gitRemote,
    platforms: config.platforms,
  };

  // Build secrets object
  const secretValues = config.secrets;
  const hashes = {};
  for (const [key, value] of Object.entries(secretValues)) {
    if (value) hashes[key] = hashSecret(value);
  }
  const secrets = { values: secretValues, hashes };

  console.log(chalk.dim(`  Game: ${answers.gameName} (${answers.gameCode})`));
  console.log(chalk.dim(`  Type: ${answers.gameType}`));
  if (answers.integrations.length > 0) {
    console.log(chalk.dim(`  Integrations: ${answers.integrations.join(', ')}`));
  }
  console.log('');

  // Run setup pipeline
  await scaffold(answers, secrets);
  await installDeps(answers);
  await launchTools(answers);

  // Clean up config file (may contain secrets)
  try {
    unlinkSync(configPath);
    console.log(chalk.dim('  Config file cleaned up (contained secrets)'));
  } catch {
    // ignore — file may have been in a temp dir
  }

  printNextSteps(answers);
}

function printNextSteps(answers) {
  const slug = answers.gameName.toLowerCase().replace(/\s+/g, '-');
  console.log('');
  console.log(chalk.bold.green('  Setup complete!'));
  console.log('');
  console.log(chalk.dim('  Next steps:'));
  console.log(`  1. ${chalk.cyan('cd ' + slug)}`);
  console.log(`  2. Open this folder in ${chalk.cyan('VS Code')}`);
  console.log(`  3. Open ${chalk.cyan('Claude Code')} terminal`);
  console.log(`  4. Type ${chalk.cyan('/lead')} to start your virtual game dev office`);
  console.log('');
}

// Help text — designed to be readable by both humans and Claude Code
export function printHelp() {
  console.log(`
${chalk.bold.cyan('game-mcp')} — Multi-Agent Game Development Framework

${chalk.bold('USAGE:')}
  npx game-mcp                  Interactive setup (terminal)
  npx game-mcp --config FILE    Non-interactive setup from JSON config
  npx game-mcp --help           Show this help

${chalk.bold('INTERACTIVE MODE:')}
  Asks questions in the terminal. For humans using a terminal directly.

${chalk.bold('NON-INTERACTIVE MODE (for Claude Code Desktop):')}
  Create a JSON config file and pass it with --config.
  The config file is deleted after setup (it may contain API keys).

${chalk.bold('CONFIG FILE FORMAT:')}
  {
    "gameName": "My Game",              ${chalk.dim('// required — your game\'s name')}
    "gameCode": "MG",                   ${chalk.dim('// required — 2-4 letter abbreviation')}
    "gameType": "web",                  ${chalk.dim('// required — web | unity-2d | unity-3d')}
    "integrations": ["sentry"],         ${chalk.dim('// optional — sentry, firebase, steam, reaper, comfyui')}
    "gitProvider": "github",            ${chalk.dim('// optional — github | gitlab | none (default: none)')}
    "gitRemote": "",                    ${chalk.dim('// optional — repository URL')}
    "platforms": ["pc"],                ${chalk.dim('// optional — pc, ios, android, web, steam')}
    "secrets": {                        ${chalk.dim('// optional — API keys')}
      "GOOGLE_API_KEY": "...",          ${chalk.dim('// Gemini CLI (research)')}
      "GIT_TOKEN": "...",               ${chalk.dim('// GitHub/GitLab token')}
      "PIXELLAB_API_TOKEN": "...",      ${chalk.dim('// PixelLab (unity-2d only)')}
      "RODIN_API_KEY": "...",           ${chalk.dim('// Rodin (unity-3d only)')}
      "SENTRY_ACCESS_TOKEN": "...",     ${chalk.dim('// if sentry integration selected')}
      "STEAM_API_KEY": "...",           ${chalk.dim('// if steam integration selected')}
      "STEAM_ID": "..."                 ${chalk.dim('// if steam integration selected')}
    }
  }

${chalk.bold('FOR CLAUDE CODE AGENTS:')}
  When a user asks you to set up a game project using game-mcp:
  1. Ask the user: game name, type (web/unity-2d/unity-3d), any integrations
  2. Ask for API keys they have (all are optional, can be added later)
  3. Write a config JSON file to a temp location
  4. Run: npx game-mcp --config /path/to/config.json
  5. The config file is auto-deleted after setup
  6. cd into the project directory
  7. Run /lead to start the virtual game dev office

${chalk.bold('GAME TYPES:')}
  ${chalk.cyan('web')}       Single HTML file game (Canvas API, packageable for Steam via Electron)
  ${chalk.green('unity-2d')}  Unity 2D with pixel art pipeline (PixelLab, Aseprite, Photoshop MCP)
  ${chalk.yellow('unity-3d')}  Unity 3D with 3D pipeline (Blender MCP, Photoshop MCP)

${chalk.bold('WHAT GETS CREATED:')}
  - Project folder with game template code
  - .claude/ directory with agent commands (lead, engineer, artist, audio, designer, qa, story)
  - .mcp.json with MCP server configurations
  - Python MCP task management server (game-mcp-team)
  - Game Bible document structure (13 sections)
  - Workflow state management system
  - .env file with your API keys (gitignored)
  - .vscode/extensions.json with recommended extensions

${chalk.bold('AFTER SETUP:')}
  Type /lead in Claude Code to activate the team lead agent.
  Lead verifies MCP connections, sets up the virtual office, and guides you.
`);
}
