import chalk from 'chalk';
import { collectAnswers } from './prompts.js';
import { collectSecrets } from './secrets.js';
import { scaffold } from './scaffold.js';
import { installDeps } from './deps.js';
import { launchTools } from './launcher.js';

export async function main() {
  console.log('');
  console.log(chalk.bold.cyan('  Game MCP') + chalk.dim(' — Multi-Agent Game Development Framework'));
  console.log(chalk.dim('  Powered by Claude Code + MCP'));
  console.log('');

  // Step 1: Collect project info
  const answers = await collectAnswers();

  // Step 2: Collect API secrets
  const secrets = await collectSecrets(answers.gameType);

  // Step 3: Scaffold project
  await scaffold(answers, secrets);

  // Step 4: Install dependencies
  await installDeps(answers);

  // Step 5: Launch tools
  await launchTools(answers);

  console.log('');
  console.log(chalk.bold.green('  Setup complete!'));
  console.log('');
  console.log(chalk.dim('  Next steps:'));
  console.log(`  1. ${chalk.cyan('cd ' + answers.gameName.toLowerCase().replace(/\s+/g, '-'))}`);
  console.log(`  2. Open this folder in ${chalk.cyan('Claude Code')}`);
  console.log(`  3. Type ${chalk.cyan('/lead')} to start designing your game`);
  console.log('');
}
