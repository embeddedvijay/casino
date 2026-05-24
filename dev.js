const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

const root = __dirname;
const frontendNodeModules = path.join(root, 'frontend', 'node_modules');

function run(command, args, options = {}) {
  const child = spawn(command, args, {
    cwd: options.cwd || root,
    stdio: 'inherit',
    shell: process.platform === 'win32',
    env: process.env,
  });

  child.on('exit', (code) => {
    if (code !== 0 && !shuttingDown) {
      console.error(`\n${options.name || command} stopped with code ${code}`);
      stopAll();
    }
  });

  processes.push(child);
  return child;
}

let shuttingDown = false;
const processes = [];

function stopAll() {
  shuttingDown = true;
  for (const child of processes) {
    if (!child.killed) child.kill('SIGTERM');
  }
  process.exit(1);
}

process.on('SIGINT', stopAll);
process.on('SIGTERM', stopAll);

if (!fs.existsSync(frontendNodeModules)) {
  console.log('frontend/node_modules not found. Installing frontend packages first...');
  const installer = spawn('npm', ['install'], {
    cwd: path.join(root, 'frontend'),
    stdio: 'inherit',
    shell: process.platform === 'win32',
  });

  installer.on('exit', (code) => {
    if (code !== 0) process.exit(code);
    startServers();
  });
} else {
  startServers();
}

function startServers() {
  console.log('\nStarting backend on http://localhost:8000');
  run('python3', ['-m', 'uvicorn', 'main:app', '--reload', '--host', '0.0.0.0', '--port', '8000', '--app-dir', 'backend'], { name: 'backend' });

  console.log('Starting frontend on http://localhost:5173\n');
  run('npm', ['run', 'dev', '--prefix', 'frontend'], { name: 'frontend' });
}
