const VALID_TYPES = ['web', 'unity-2d', 'unity-3d'];
const VALID_INTEGRATIONS = ['sentry', 'firebase', 'steam', 'reaper', 'comfyui'];
const VALID_GIT_PROVIDERS = ['github', 'gitlab', 'none'];
const VALID_PLATFORMS = ['pc', 'ios', 'android', 'web', 'steam'];

export function validateConfig(config) {
  const errors = [];

  if (!config || typeof config !== 'object') {
    return { valid: false, errors: ['Config must be a JSON object'] };
  }

  // Required fields
  if (!config.gameName || typeof config.gameName !== 'string' || !config.gameName.trim()) {
    errors.push('gameName is required (string)');
  }

  if (!config.gameCode || !/^[A-Za-z]{2,4}$/.test(config.gameCode)) {
    errors.push('gameCode is required (2-4 letters)');
  }

  if (!config.gameType || !VALID_TYPES.includes(config.gameType)) {
    errors.push(`gameType must be one of: ${VALID_TYPES.join(', ')}`);
  }

  // Optional fields — validate if present
  if (config.integrations !== undefined) {
    if (!Array.isArray(config.integrations)) {
      errors.push('integrations must be an array');
    } else {
      for (const i of config.integrations) {
        if (!VALID_INTEGRATIONS.includes(i)) {
          errors.push(`Unknown integration: "${i}". Valid: ${VALID_INTEGRATIONS.join(', ')}`);
        }
      }
    }
  }

  if (config.gitProvider !== undefined && !VALID_GIT_PROVIDERS.includes(config.gitProvider)) {
    errors.push(`gitProvider must be one of: ${VALID_GIT_PROVIDERS.join(', ')}`);
  }

  if (config.platforms !== undefined) {
    if (!Array.isArray(config.platforms)) {
      errors.push('platforms must be an array');
    } else {
      for (const p of config.platforms) {
        if (!VALID_PLATFORMS.includes(p)) {
          errors.push(`Unknown platform: "${p}". Valid: ${VALID_PLATFORMS.join(', ')}`);
        }
      }
    }
  }

  if (config.secrets !== undefined && typeof config.secrets !== 'object') {
    errors.push('secrets must be an object');
  }

  return { valid: errors.length === 0, errors };
}

export function normalizeConfig(config) {
  const gameType = config.gameType;
  return {
    gameName: config.gameName.trim(),
    gameCode: config.gameCode.trim().toUpperCase(),
    gameType,
    integrations: config.integrations || [],
    gitProvider: config.gitProvider || 'none',
    gitRemote: (config.gitRemote || '').trim(),
    platforms: config.platforms || (gameType === 'web' ? ['web'] : ['pc']),
    secrets: config.secrets || {},
  };
}

export { VALID_TYPES, VALID_INTEGRATIONS, VALID_GIT_PROVIDERS, VALID_PLATFORMS };
