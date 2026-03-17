import { exec } from 'node:child_process';
import { platform } from 'node:os';
import chalk from 'chalk';

function openApp(cmd) {
  const os = platform();
  try {
    if (os === 'win32') {
      exec(`start "" "${cmd}"`);
    } else if (os === 'darwin') {
      exec(`open -a "${cmd}"`);
    } else {
      exec(cmd);
    }
    return true;
  } catch {
    return false;
  }
}

function openUrl(url) {
  const os = platform();
  try {
    if (os === 'win32') {
      exec(`start "" "${url}"`);
    } else if (os === 'darwin') {
      exec(`open "${url}"`);
    } else {
      exec(`xdg-open "${url}"`);
    }
    return true;
  } catch {
    return false;
  }
}

export async function launchTools(answers) {
  const projectDir = process.cwd() + '/' + answers.gameName.toLowerCase().replace(/\s+/g, '-');
  const integrations = answers.integrations || [];

  console.log('');
  console.log(chalk.bold('  Launching tools...'));
  console.log('');

  if (answers.gameType === 'web') {
    const indexPath = projectDir + '/src/index.html';
    console.log(`  Opening ${chalk.cyan(indexPath)} in browser...`);
    openUrl(indexPath);
  }

  if (answers.gameType === 'unity-2d' || answers.gameType === 'unity-3d') {
    console.log(`  ${chalk.cyan('Unity:')} Open Unity Hub and add project folder: ${chalk.dim(projectDir)}`);
    openApp('Unity Hub');
  }

  if (answers.gameType === 'unity-3d') {
    console.log(`  ${chalk.cyan('Blender:')} Opening Blender...`);
    openApp('blender');
  }

  if (integrations.includes('reaper')) {
    console.log(`  ${chalk.magenta('REAPER:')} Opening REAPER DAW...`);
    openApp('reaper');
  }

  if (integrations.includes('comfyui')) {
    console.log(`  ${chalk.green('ComfyUI:')} Make sure ComfyUI is running at ${chalk.cyan('http://localhost:8000')}`);
  }
}
