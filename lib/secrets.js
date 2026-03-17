import { input, password } from '@inquirer/prompts';
import { createHash } from 'node:crypto';
import chalk from 'chalk';

function hashSecret(value) {
  return createHash('sha256').update(value).digest('hex');
}

export async function collectSecrets(gameType) {
  console.log('');
  console.log(chalk.bold('  API Keys'));
  console.log(chalk.dim('  Stored in .env (gitignored). Hashes saved to .env.hash for integrity.'));
  console.log('');

  const secrets = {};

  // Gemini — all game types use it for research
  const geminiKey = await password({
    message: 'Google Gemini API Key (for research — press Enter to skip)',
    mask: '*',
  });
  if (geminiKey) secrets.GOOGLE_API_KEY = geminiKey;

  // GitHub/GitLab token
  const gitToken = await password({
    message: 'GitHub/GitLab Token (for repo management — press Enter to skip)',
    mask: '*',
  });
  if (gitToken) secrets.GIT_TOKEN = gitToken;

  // Game-type specific secrets
  if (gameType === 'unity-2d') {
    const pixelLabToken = await password({
      message: 'PixelLab API Token (for pixel art generation — press Enter to skip)',
      mask: '*',
    });
    if (pixelLabToken) secrets.PIXELLAB_API_TOKEN = pixelLabToken;
  }

  if (gameType === 'unity-3d') {
    const rodinKey = await password({
      message: 'Rodin API Key (for 3D model generation — press Enter to skip)',
      mask: '*',
    });
    if (rodinKey) secrets.RODIN_API_KEY = rodinKey;
  }

  // Build hashes
  const hashes = {};
  for (const [key, value] of Object.entries(secrets)) {
    hashes[key] = hashSecret(value);
  }

  return { values: secrets, hashes };
}

export function generateEnvFile(secrets) {
  const lines = ['# Game MCP — API Keys (DO NOT COMMIT)', '#'];
  for (const [key, value] of Object.entries(secrets.values)) {
    lines.push(`${key}=${value}`);
  }
  return lines.join('\n') + '\n';
}

export function generateHashFile(secrets) {
  const lines = ['# Game MCP — Secret hashes for integrity verification', '#'];
  for (const [key, hash] of Object.entries(secrets.hashes)) {
    lines.push(`${key}=${hash}`);
  }
  return lines.join('\n') + '\n';
}
