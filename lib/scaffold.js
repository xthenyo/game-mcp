import { mkdirSync, writeFileSync, cpSync, existsSync, readdirSync, statSync, readFileSync, rmSync, renameSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import ora from 'ora';
import { generateEnvFile, generateHashFile } from './secrets.js';

const __dirname = dirname(fileURLToPath(import.meta.url));
const TEMPLATES = join(__dirname, '..', 'templates');

function write(path, content) {
  mkdirSync(dirname(path), { recursive: true });
  writeFileSync(path, content, 'utf-8');
}

function copyDir(src, dest) {
  if (existsSync(src)) {
    cpSync(src, dest, { recursive: true });
  }
}

function replaceVars(content, vars) {
  let result = content;
  for (const [key, value] of Object.entries(vars)) {
    result = result.replaceAll(`{{${key}}}`, value);
  }
  return result;
}

function replaceInDir(dir, vars) {
  const entries = readdirSync(dir);
  for (const entry of entries) {
    const fullPath = join(dir, entry);
    if (entry === '.git' || entry === 'node_modules' || entry === '.uv') continue;
    const stat = statSync(fullPath);
    if (stat.isDirectory()) {
      replaceInDir(fullPath, vars);
    } else if (/\.(md|json|yaml|yml|toml|html|css|js|ts|txt|cfg|py)$/i.test(entry)) {
      const content = readFileSync(fullPath, 'utf-8');
      const replaced = replaceVars(content, vars);
      if (replaced !== content) {
        writeFileSync(fullPath, replaced, 'utf-8');
      }
    }
  }
}

// Optional MCP server definitions
const OPTIONAL_MCPS = {
  sentry: {
    key: 'sentry',
    config: {
      command: 'npx',
      args: ['-y', '@sentry/mcp-server'],
      env: { SENTRY_ACCESS_TOKEN: '${SENTRY_ACCESS_TOKEN}' },
    },
    permission: 'mcp__sentry__*',
  },
  firebase: {
    key: 'firebase',
    config: {
      command: 'npx',
      args: ['-y', 'firebase-tools@latest', 'mcp'],
    },
    permission: 'mcp__firebase__*',
  },
  steam: {
    key: 'steam',
    config: {
      command: 'node',
      args: ['.mcp-tools/steam-mcp/dist/index.js'],
      env: { STEAM_API_KEY: '${STEAM_API_KEY}', STEAM_ID: '${STEAM_ID}' },
    },
    permission: 'mcp__steam__*',
  },
  reaper: {
    key: 'reaper',
    config: {
      command: 'python',
      args: ['-m', 'reaper_mcp', '--mode=osc'],
      cwd: '.mcp-tools/reaper-mcp',
    },
    permission: 'mcp__reaper__*',
  },
  comfyui: {
    key: 'comfyui',
    config: {
      command: 'npx',
      args: ['-y', 'comfyui-mcp'],
    },
    permission: 'mcp__comfyui__*',
  },
};

export async function scaffold(answers, secrets) {
  const slug = answers.gameName.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
  const root = join(process.cwd(), slug);

  if (existsSync(root)) {
    throw new Error(`Directory "${slug}" already exists. Choose a different name or delete it first.`);
  }

  const vars = {
    GAME_NAME: answers.gameName,
    GAME_CODE: answers.gameCode,
    GAME_TYPE: answers.gameType,
    GAME_SLUG: slug,
    PLATFORMS: answers.platforms.join(', '),
  };

  const spinner = ora('Scaffolding project...').start();

  // Create root
  mkdirSync(root, { recursive: true });

  // Copy common templates
  copyDir(join(TEMPLATES, 'common'), root);

  // Copy game-type specific templates (overwrites/merges with common)
  copyDir(join(TEMPLATES, answers.gameType), root);

  // Move template claude/ contents to .claude/ (dot-prefixed)
  const templateClaudeDir = join(root, 'claude');
  const claudeDir = join(root, '.claude');
  if (existsSync(templateClaudeDir)) {
    cpSync(templateClaudeDir, claudeDir, { recursive: true });
    rmSync(templateClaudeDir, { recursive: true, force: true });
  }

  // Rename dotfile templates (can't store dotfiles in npm templates)
  const renames = [
    ['mcp.json', '.mcp.json'],
    ['env.example', '.env.example'],
  ];
  for (const [from, to] of renames) {
    const src = join(root, from);
    const dest = join(root, to);
    if (existsSync(src)) renameSync(src, dest);
  }

  // Inject optional MCP servers into .mcp.json
  const integrations = answers.integrations || [];
  if (integrations.length > 0) {
    injectOptionalMcps(root, integrations);
  }

  // Create .vscode/extensions.json with recommended extensions
  createVscodeExtensions(root, answers.gameType, integrations);

  // Write .env and .env.hash (always create .env so Lead agent doesn't fail on missing file)
  write(join(root, '.env'), generateEnvFile(secrets));
  if (Object.keys(secrets.hashes).length > 0) {
    write(join(root, '.env.hash'), generateHashFile(secrets));
  }

  // Write .gitignore
  write(join(root, '.gitignore'), generateGitignore(answers.gameType));

  // Write project config with variables substituted
  write(join(root, 'game-mcp.json'), JSON.stringify({
    name: answers.gameName,
    code: answers.gameCode,
    type: answers.gameType,
    platforms: answers.platforms,
    integrations,
    version: '1.0.0',
  }, null, 2) + '\n');

  // Replace template variables in all text files
  replaceInDir(root, vars);

  spinner.succeed('Project scaffolded');
}

function injectOptionalMcps(root, integrations) {
  const mcpPath = join(root, '.mcp.json');
  if (!existsSync(mcpPath)) return;

  const mcpConfig = JSON.parse(readFileSync(mcpPath, 'utf-8'));
  if (!mcpConfig.mcpServers) mcpConfig.mcpServers = {};

  for (const integration of integrations) {
    const def = OPTIONAL_MCPS[integration];
    if (def) {
      mcpConfig.mcpServers[def.key] = def.config;
    }
  }

  writeFileSync(mcpPath, JSON.stringify(mcpConfig, null, 2) + '\n', 'utf-8');

  // Also inject permissions into .claude/settings.json
  const settingsPath = join(root, '.claude', 'settings.json');
  if (existsSync(settingsPath)) {
    const settings = JSON.parse(readFileSync(settingsPath, 'utf-8'));
    if (!settings.permissions) settings.permissions = {};
    if (!Array.isArray(settings.permissions.allow)) settings.permissions.allow = [];
    for (const integration of integrations) {
      const def = OPTIONAL_MCPS[integration];
      if (def && !settings.permissions.allow.includes(def.permission)) {
        settings.permissions.allow.push(def.permission);
      }
    }
    writeFileSync(settingsPath, JSON.stringify(settings, null, 2) + '\n', 'utf-8');
  }
}

function createVscodeExtensions(root, gameType, integrations) {
  const recommendations = [
    'pablodelucca.pixel-agents',
    'anthropic.claude-code',
  ];

  if (gameType === 'web') {
    recommendations.push('ritwickdey.liveserver', 'dbaeumer.vscode-eslint');
  }

  if (gameType.startsWith('unity')) {
    recommendations.push(
      'visualstudiotoolsforunity.vstuc',
      'ms-dotnettools.csdevkit',
      'ms-dotnettools.csharp',
    );
  }

  if (gameType === 'unity-3d') {
    recommendations.push('jacqueslucke.blender-development');
  }

  if (integrations.includes('firebase')) {
    recommendations.push('toba.vsfire');
  }

  write(
    join(root, '.vscode', 'extensions.json'),
    JSON.stringify({ recommendations, unwantedRecommendations: [] }, null, 2) + '\n'
  );
}

function generateGitignore(gameType) {
  const common = `# Secrets
.env
.env.local
.env.*.local

# Python
__pycache__/
*.pyc
.venv/
.uv/

# Node
node_modules/
dist/

# OS
.DS_Store
Thumbs.db
*.swp
*~

# IDE
.idea/
*.suo
*.user
*.vs/

# Workflow state (regenerated)
workflow/team-state.json
workflow/.state-*.tmp
workflow/audit-*.jsonl

# Build artifacts
build/
*.log

# MCP tools (installed locally)
.mcp-tools/
`;

  if (gameType === 'web') {
    return common + `
# Web specific
.cache/
.parcel-cache/
`;
  }

  // Unity
  return common + `
# Unity
[Ll]ibrary/
[Tt]emp/
[Oo]bj/
[Bb]uild/
[Bb]uilds/
[Ll]ogs/
[Uu]ser[Ss]ettings/
[Mm]emoryCaptures/
[Rr]ecordings/
Asset[Ss]tore[Tt]ools/

# Unity meta
*.pidb
*.pdb
*.mdb
*.opendb
*.VC.db

# Large assets (track with Git LFS)
*.psd
*.psb
*.tga
*.tif
*.tiff
*.blend1

# Crashlytics
crashlytics-build.properties
sysinfo.txt

# Builds
*.apk
*.aab
*.unitypackage
*.app
`;
}
