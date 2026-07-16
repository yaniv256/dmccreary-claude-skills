const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const runtimePath = path.join(
  __dirname,
  '..',
  'assets',
  'docker-python-lab',
  'docker-lab.js'
);

const elements = {};
for (const id of [
  'docker-code-4',
  'docker-output-4',
  'docker-run-4',
  'docker-timing-display',
  'td-roundtrip-overhead',
  'bar-roundtrip-overhead',
  'td-server-overhead',
  'bar-server-overhead',
  'td-startup',
  'bar-startup',
  'td-exec',
  'bar-exec',
  'td-container-overhead',
  'bar-container-overhead',
  'td-total',
  'docker-timing-note',
]) {
  elements[id] = { className: '', disabled: false, style: {}, textContent: '' };
}
elements['docker-code-4'].value = 'print("hello")';

let clock = 0;
const context = {
  console,
  document: {
    readyState: 'loading',
    addEventListener() {},
    getElementById(id) {
      return elements[id] || null;
    },
  },
  fetch: async () => ({
    ok: true,
    json: async () => {
      clock = 110;
      return {
        returncode: 0,
        stdout: 'hello\n',
        stderr: '',
        timing: {
          docker_total_ms: 60,
          server_overhead_ms: 10,
          container_startup_ms: 20,
          python_exec_ms: 30,
        },
      };
    },
  }),
  isFinite,
  performance: { now: () => clock },
};
vm.createContext(context);
vm.runInContext(fs.readFileSync(runtimePath, 'utf8'), context, { filename: runtimePath });

const valid = context._dockerTimingBreakdown(100, {
  docker_total_ms: 60,
  server_overhead_ms: 10,
  container_startup_ms: 20,
  python_exec_ms: 30,
});

assert.equal(JSON.stringify(valid), JSON.stringify([
  { id: 'roundtrip-overhead', ms: 30 },
  { id: 'server-overhead', ms: 10 },
  { id: 'startup', ms: 20 },
  { id: 'exec', ms: 30 },
  { id: 'container-overhead', ms: 10 },
]));

for (const inconsistent of [
  {
    docker_total_ms: 80,
    server_overhead_ms: 30,
    container_startup_ms: 20,
    python_exec_ms: 40,
  },
  {
    docker_total_ms: 60,
    server_overhead_ms: 10,
    container_startup_ms: 40,
    python_exec_ms: 30,
  },
  {
    docker_total_ms: 60,
    server_overhead_ms: 10,
    container_startup_ms: 20,
  },
]) {
  assert.equal(
    context._dockerTimingBreakdown(100, inconsistent).every((phase) => phase.ms === null),
    true
  );
}

(async () => {
  await context.runDockerTimed('4');
  assert.equal(elements['td-total'].textContent, '110.0 ms');
  assert.equal(elements['td-roundtrip-overhead'].textContent, '40.0');
  assert.equal(elements['td-container-overhead'].textContent, '10.0');
  assert.equal(elements['docker-output-4'].textContent, 'hello');
  console.log('Docker Python lab timing contract: OK');
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
