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

  console.log('');
  console.log(chalk.bold('  Launching tools...'));
  console.log('');

  if (answers.gameType === 'web') {
    // Open project folder in default browser via file
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
}
