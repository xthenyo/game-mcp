import { execSync } from 'node:child_process';
import { existsSync } from 'node:fs';
import ora from 'ora';
import chalk from 'chalk';

function run(cmd, cwd, silent = true) {
  try {
    execSync(cmd, {
      cwd,
      stdio: silent ? 'pipe' : 'inherit',
      timeout: 300000,
    });
    return true;
  } catch {
    return false;
  }
}

function which(name) {
  try {
    execSync(`where ${name}`, { stdio: 'pipe' });
    return true;
  } catch {
    try {
      execSync(`which ${name}`, { stdio: 'pipe' });
      return true;
    } catch {
      return false;
    }
  }
}

export async function installDeps(answers) {
  const projectDir = process.cwd() + '/' + answers.gameName.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
  const integrations = answers.integrations || [];

  console.log('');
  console.log(chalk.bold('  Checking tools...'));
  console.log('');

  // Check required tools
  const checks = [
    { name: 'Python 3.11+', cmd: 'python3', alt: 'python', required: true },
    { name: 'uv (Python package manager)', cmd: 'uv', required: true },
    { name: 'Git', cmd: 'git', required: true },
    { name: 'Gemini CLI', cmd: 'gemini', required: false },
  ];

  if (answers.gameType === 'web') {
    checks.push({ name: 'Node.js', cmd: 'node', required: true });
  }

  if (answers.gameType.startsWith('unity')) {
    checks.push({ name: 'Unity Hub', cmd: 'unityhub', alt: 'Unity Hub', required: false });
  }

  if (answers.gameType === 'unity-2d') {
    checks.push({ name: 'Aseprite', cmd: 'aseprite', required: false });
  }

  if (answers.gameType.startsWith('unity')) {
    checks.push({ name: 'Photoshop (for MCP)', cmd: 'photoshop', required: false });
  }

  if (answers.gameType === 'unity-3d') {
    checks.push({ name: 'Blender', cmd: 'blender', required: false });
  }

  // Optional integration checks
  if (integrations.includes('reaper')) {
    checks.push({ name: 'REAPER (DAW)', cmd: 'reaper', required: false });
  }

  if (integrations.includes('comfyui')) {
    checks.push({ name: 'ComfyUI (local)', cmd: 'comfyui', required: false });
  }

  const missing = [];
  for (const check of checks) {
    const found = which(check.cmd) || (check.alt && which(check.alt));
    const status = found ? chalk.green('found') : check.required ? chalk.red('MISSING') : chalk.yellow('not found (optional)');
    console.log(`  ${found ? '+' : '-'} ${check.name}: ${status}`);
    if (!found && check.required) missing.push(check.name);
  }

  if (missing.length > 0) {
    console.log('');
    console.log(chalk.yellow(`  Warning: Missing required tools: ${missing.join(', ')}`));
    console.log('');
    const installGuide = {
      'Python 3.11+': 'https://python.org/downloads — or: winget install Python.Python.3.12',
      'uv (Python package manager)': 'curl -LsSf https://astral.sh/uv/install.sh | sh — or: pip install uv',
      'Git': 'https://git-scm.com/downloads — or: winget install Git.Git',
      'Node.js': 'https://nodejs.org — or: winget install OpenJS.NodeJS.LTS',
    };
    for (const name of missing) {
      if (installGuide[name]) {
        console.log(chalk.dim(`    ${name}: ${installGuide[name]}`));
      }
    }
  }

  // Install Python deps (MCP server)
  const spinner = ora('Installing Python MCP server dependencies...').start();
  if (existsSync(projectDir + '/pyproject.toml')) {
    const ok = run('uv sync', projectDir);
    if (ok) {
      spinner.succeed('Python MCP server dependencies installed');
    } else {
      spinner.warn('Python deps install failed — run "uv sync" manually in project dir');
    }
  } else {
    spinner.info('No pyproject.toml found, skipping Python deps');
  }

  // Install Node deps if web game
  if (answers.gameType === 'web') {
    const spinner2 = ora('Installing Node.js dependencies...').start();
    if (existsSync(projectDir + '/package.json')) {
      const ok = run('npm install', projectDir);
      if (ok) {
        spinner2.succeed('Node.js dependencies installed');
      } else {
        spinner2.warn('npm install failed — run "npm install" manually');
      }
    } else {
      spinner2.info('No package.json found');
    }
  }

  // Install Steam MCP if selected
  if (integrations.includes('steam')) {
    const spinner5 = ora('Installing Steam MCP server...').start();
    const steamDir = projectDir + '/.mcp-tools/steam-mcp';
    const ok = run('git clone https://github.com/matheusslg/steam-mcp.git .mcp-tools/steam-mcp', projectDir)
      && run('npm install', steamDir)
      && run('npm run build', steamDir);
    if (ok) {
      spinner5.succeed('Steam MCP server installed');
    } else {
      spinner5.warn('Steam MCP install failed — clone and build manually: .mcp-tools/steam-mcp');
    }
  }

  // Install REAPER MCP if selected
  if (integrations.includes('reaper')) {
    const spinner6 = ora('Installing REAPER MCP server...').start();
    const reaperDir = projectDir + '/.mcp-tools/reaper-mcp';
    const ok = run('git clone https://github.com/itsuzef/reaper-mcp.git .mcp-tools/reaper-mcp', projectDir)
      && run('pip install -e .', reaperDir);
    if (ok) {
      spinner6.succeed('REAPER MCP server installed');
    } else {
      spinner6.warn('REAPER MCP install failed — see .mcp-tools/reaper-mcp/README.md');
    }
  }

  // Firebase login reminder
  if (integrations.includes('firebase')) {
    console.log('');
    console.log(chalk.cyan('  Firebase:') + ' Run ' + chalk.bold('npx firebase-tools login') + ' to authenticate');
  }

  // Init git repo
  const spinner3 = ora('Initializing git repository...').start();
  if (!existsSync(projectDir + '/.git')) {
    run('git init', projectDir);
    run('git add -A', projectDir);
    run('git commit -m "Initial commit: game project scaffolded by game-mcp"', projectDir);
    spinner3.succeed('Git repository initialized');
  } else {
    spinner3.info('Git repository already exists');
  }

  // Set up remote if provided
  if (answers.gitRemote) {
    const spinner4 = ora('Setting up git remote...').start();
    const remote = answers.gitRemote.replace(/[;&|`$()]/g, '');
    run(`git remote add origin ${remote}`, projectDir);
    spinner4.succeed(`Remote added: ${remote}`);
  }
}
