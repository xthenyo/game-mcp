import { input, select, confirm } from '@inquirer/prompts';
import chalk from 'chalk';

export async function collectAnswers() {
  const gameName = await input({
    message: 'What is your game\'s name?',
    validate: (v) => v.trim().length > 0 || 'Game name is required',
  });

  const gameCode = await input({
    message: 'Game code (2-4 letter abbreviation)',
    validate: (v) => /^[A-Za-z]{2,4}$/.test(v.trim()) || 'Must be 2-4 letters',
    transformer: (v) => v.toUpperCase(),
  });

  const gameType = await select({
    message: 'What type of game are you making?',
    choices: [
      {
        name: `${chalk.cyan('Web Game')} ${chalk.dim('— HTML/JS/CSS, packageable for Steam via Electron')}`,
        value: 'web',
      },
      {
        name: `${chalk.green('Unity 2D')} ${chalk.dim('— Pixel art, tilemaps, sprites (PixelLab + Aseprite)')}`,
        value: 'unity-2d',
      },
      {
        name: `${chalk.yellow('Unity 3D')} ${chalk.dim('— 3D models, Blender integration')}`,
        value: 'unity-3d',
      },
    ],
  });

  const gitProvider = await select({
    message: 'Git provider',
    choices: [
      { name: 'GitHub', value: 'github' },
      { name: 'GitLab', value: 'gitlab' },
      { name: 'None (local only)', value: 'none' },
    ],
  });

  let gitRemote = '';
  if (gitProvider !== 'none') {
    gitRemote = await input({
      message: `${gitProvider === 'github' ? 'GitHub' : 'GitLab'} repository URL (leave empty to create later)`,
      default: '',
    });
  }

  const platforms = [];
  if (gameType === 'web') {
    platforms.push('web');
    const addSteam = await confirm({ message: 'Package for Steam (via Electron)?', default: false });
    if (addSteam) platforms.push('steam');
  } else {
    const addPC = await confirm({ message: 'Build for PC (Windows/Mac/Linux)?', default: true });
    if (addPC) platforms.push('pc');
    const addIOS = await confirm({ message: 'Build for iOS?', default: false });
    if (addIOS) platforms.push('ios');
    const addAndroid = await confirm({ message: 'Build for Android?', default: false });
    if (addAndroid) platforms.push('android');
  }

  return {
    gameName: gameName.trim(),
    gameCode: gameCode.trim().toUpperCase(),
    gameType,
    gitProvider,
    gitRemote: gitRemote.trim(),
    platforms,
  };
}
