import { exec, execSync } from 'node:child_process';
import { existsSync } from 'node:fs';
import { platform, homedir } from 'node:os';
import { join } from 'node:path';
import chalk from 'chalk';

// Known install paths per platform
const APP_PATHS = {
  'Unity Hub': {
    win32: [
      join(process.env.PROGRAMFILES || 'C:\\Program Files', 'Unity Hub', 'Unity Hub.exe'),
      join(process.env['PROGRAMFILES(X86)'] || 'C:\\Program Files (x86)', 'Unity Hub', 'Unity Hub.exe'),
      join(homedir(), 'AppData', 'Local', 'Programs', 'Unity Hub', 'Unity Hub.exe'),
    ],
    darwin: ['/Applications/Unity Hub.app'],
    linux: ['/usr/bin/unityhub', '/opt/unityhub/unityhub'],
  },
  blender: {
    win32: [
      join(process.env.PROGRAMFILES || 'C:\\Program Files', 'Blender Foundation', 'Blender 4.3', 'blender.exe'),
      join(process.env.PROGRAMFILES || 'C:\\Program Files', 'Blender Foundation', 'Blender 4.2', 'blender.exe'),
      join(process.env.PROGRAMFILES || 'C:\\Program Files', 'Blender Foundation', 'Blender 4.1', 'blender.exe'),
      join(process.env.PROGRAMFILES || 'C:\\Program Files', 'Blender Foundation', 'Blender 4.0', 'blender.exe'),
      join(process.env.PROGRAMFILES || 'C:\\Program Files', 'Blender Foundation', 'Blender 3.6', 'blender.exe'),
    ],
    darwin: ['/Applications/Blender.app'],
    linux: ['/usr/bin/blender', '/snap/bin/blender'],
  },
  reaper: {
    win32: [
      join(process.env.PROGRAMFILES || 'C:\\Program Files', 'REAPER (x64)', 'reaper.exe'),
      join(process.env.PROGRAMFILES || 'C:\\Program Files', 'REAPER', 'reaper.exe'),
      join(process.env['PROGRAMFILES(X86)'] || 'C:\\Program Files (x86)', 'REAPER', 'reaper.exe'),
    ],
    darwin: ['/Applications/REAPER.app'],
    linux: ['/usr/bin/reaper', '/opt/REAPER/reaper'],
  },
};

function findApp(name) {
  const os = platform();
  const paths = APP_PATHS[name]?.[os] || [];

  // First try PATH
  try {
    const cmd = os === 'win32' ? `where ${name}` : `which ${name}`;
    const result = execSync(cmd, { stdio: 'pipe', encoding: 'utf-8' }).trim();
    if (result) return result.split('\n')[0].trim();
  } catch {
    // not on PATH
  }

  // Then try known install locations
  for (const p of paths) {
    if (existsSync(p)) return p;
  }

  return null;
}

function openApp(name) {
  const os = platform();
  const appPath = findApp(name);

  if (!appPath) return false;

  try {
    if (os === 'win32') {
      exec(`start "" "${appPath}"`);
    } else if (os === 'darwin') {
      exec(`open -a "${appPath}"`);
    } else {
      exec(`"${appPath}"`);
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
  const projectDir = process.cwd() + '/' + answers.gameName.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
  const integrations = answers.integrations || [];

  console.log('');
  console.log(chalk.bold('  Launching tools...'));
  console.log('');

  if (answers.gameType === 'web') {
    const indexPath = projectDir + '/src/index.html';
    console.log(`  Opening ${chalk.cyan('index.html')} in browser...`);
    openUrl(indexPath);
  }

  if (answers.gameType === 'unity-2d' || answers.gameType === 'unity-3d') {
    const launched = openApp('Unity Hub');
    if (launched) {
      console.log(`  ${chalk.green('+')} ${chalk.cyan('Unity Hub')} opened — add project: ${chalk.dim(projectDir)}`);
    } else {
      console.log(`  ${chalk.yellow('-')} ${chalk.cyan('Unity Hub')} not found — install from ${chalk.dim('https://unity.com/download')}`);
      console.log(`    Then open it and add project folder: ${chalk.dim(projectDir)}`);
    }
  }

  if (answers.gameType === 'unity-3d') {
    const launched = openApp('blender');
    if (launched) {
      console.log(`  ${chalk.green('+')} ${chalk.cyan('Blender')} opened`);
    } else {
      console.log(`  ${chalk.yellow('-')} ${chalk.cyan('Blender')} not found — install from ${chalk.dim('https://blender.org/download')}`);
    }
  }

  if (integrations.includes('reaper')) {
    const launched = openApp('reaper');
    if (launched) {
      console.log(`  ${chalk.green('+')} ${chalk.cyan('REAPER')} opened — enable OSC mode for MCP`);
    } else {
      console.log(`  ${chalk.yellow('-')} ${chalk.cyan('REAPER')} not found — install from ${chalk.dim('https://reaper.fm/download')}`);
    }
  }

  if (integrations.includes('comfyui')) {
    console.log(`  ${chalk.dim('i')} ${chalk.cyan('ComfyUI:')} start it at ${chalk.cyan('http://localhost:8188')} before using AI art tools`);
  }
}
