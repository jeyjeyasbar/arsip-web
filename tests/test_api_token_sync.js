const fs = require('fs');
const vm = require('vm');

const script = fs.readFileSync('app/static/js/app.js', 'utf8');

function makeResponse(status, payload) {
  return {
    status,
    ok: status >= 200 && status < 300,
    json: async () => payload,
  };
}

const context = {
  console,
  setTimeout: (fn) => { fn(); return 0; },
  URLSearchParams,
  Headers: class {
    constructor(init = {}) {
      this._map = new Map(Object.entries(init));
    }
    set(key, value) {
      this._map.set(key, value);
    }
    get(key) {
      return this._map.get(key);
    }
  },
  FormData: class {
    constructor() { this._entries = []; }
    append(key, value) { this._entries.push([key, value]); }
  },
  fetch: async (url, options = {}) => {
    if (url === '/api/auth/password') {
      return makeResponse(200, { access_token: 'new-token', user: { id: 1, name: 'Test User' } });
    }
    throw new Error(`Unexpected fetch: ${url}`);
  },
  document: {
    body: { appendChild() {} },
    createElement: () => ({
      className: '',
      textContent: '',
      style: {},
      remove() {},
      onclick: null,
      addEventListener() {},
      setAttribute() {},
      click() {},
    }),
    getElementById: () => ({
      value: '',
      style: { display: '' },
      classList: { toggle() {}, add() {}, remove() {} },
      innerHTML: '',
      src: '',
      textContent: '',
      type: 'text',
      files: [],
      dataset: {},
    }),
    querySelectorAll: () => [],
  },
  navigator: {
    clipboard: { writeText: async () => {} },
  },
  window: {
    addEventListener() {},
  },
};
context.globalThis = context;
vm.runInNewContext(`${script}; globalThis.__setOldToken = () => { accessToken = 'old-token'; }; globalThis.__readAccessToken = () => accessToken; globalThis.__api = api;`, context);

(async () => {
  context.__setOldToken();
  await context.__api('/auth/password', {
    method: 'PUT',
    body: JSON.stringify({ current_password: 'old-pass', new_password: 'new-pass' }),
  });

  const token = context.__readAccessToken();
  if (token !== 'new-token') {
    throw new Error(`Expected accessToken to update to new-token, got ${token}`);
  }

  console.log('api token sync check: ok');
})();
