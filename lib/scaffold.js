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

export async function scaffold(answers, secrets) {
  const slug = answers.gameName.toLowerCase().replace(/\s+/g, '-');
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

  // Rename mcp.json to .mcp.json (dot-prefixed, can't store dotfiles in templates)
  const mcpJson = join(root, 'mcp.json');
  const dotMcpJson = join(root, '.mcp.json');
  if (existsSync(mcpJson)) {
    renameSync(mcpJson, dotMcpJson);
  }

  // Write .env and .env.hash
  if (Object.keys(secrets.values).length > 0) {
    write(join(root, '.env'), generateEnvFile(secrets));
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
    version: '1.0.0',
  }, null, 2) + '\n');

  // Replace template variables in all text files
  replaceInDir(root, vars);

  spinner.succeed('Project scaffolded');
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
