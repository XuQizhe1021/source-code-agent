const state = {
  token: "",
  graphId: "",
  session: "",
  runCount: 0
};

const tests = [
  { id: "providers", label: "GET /models/providers", run: testProviders },
  { id: "modules", label: "GET /models/providers/modules", run: testProviderModules },
  { id: "auth", label: "POST /auth/register + /auth/login", run: testAuthFlow },
  { id: "graphsList", label: "GET /graphs/ (需登录)", run: testGraphList },
  { id: "graphCreate", label: "POST /graphs/ (需登录)", run: testCreateGraph },
  { id: "neo4jTest", label: "POST /graphs/{id}/neo4j-test", run: testNeo4j },
  { id: "upload", label: "POST /graphs/{id}/files/upload (MinIO)", run: testUploadFile },
  { id: "filesList", label: "GET /graphs/{id}/files", run: testGraphFiles }
];

const el = {
  baseUrl: document.getElementById("baseUrl"),
  usernamePrefix: document.getElementById("usernamePrefix"),
  password: document.getElementById("password"),
  testList: document.getElementById("testList"),
  runSelected: document.getElementById("runSelected"),
  checkAll: document.getElementById("checkAll"),
  uncheckAll: document.getElementById("uncheckAll"),
  clearResults: document.getElementById("clearResults"),
  results: document.getElementById("results"),
  summary: document.getElementById("summary")
};

function baseUrl() {
  return el.baseUrl.value.replace(/\/+$/, "");
}

function nowSeed() {
  return `${Date.now()}_${Math.floor(Math.random() * 10000)}`;
}

function pretty(v) {
  return typeof v === "string" ? v : JSON.stringify(v, null, 2);
}

function renderTests() {
  el.testList.innerHTML = "";
  for (const t of tests) {
    const box = document.createElement("label");
    box.className = "test-item";
    box.innerHTML = `<input type="checkbox" data-id="${t.id}" checked /> ${t.label}`;
    el.testList.appendChild(box);
  }
}

function selectedTests() {
  const checked = [...el.testList.querySelectorAll("input[type=checkbox]:checked")].map(i => i.dataset.id);
  return tests.filter(t => checked.includes(t.id));
}

function addResult(item) {
  const wrap = document.createElement("details");
  wrap.className = `result ${item.ok ? "pass" : "fail"}`;
  wrap.open = !item.ok;
  wrap.innerHTML = `
    <summary>${item.ok ? "✅" : "❌"} ${item.name} | ${item.ms}ms | HTTP ${item.status ?? "-"}</summary>
    <div class="result-body">
      <div class="actions"><button class="delete-btn">删除</button></div>
      <pre>${escapeHtml(pretty(item.body))}</pre>
    </div>
  `;
  wrap.querySelector(".delete-btn").onclick = () => wrap.remove();
  el.results.prepend(wrap);
}

function escapeHtml(str) {
  return str
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

async function request(method, path, body = null, withAuth = false, isForm = false) {
  const headers = {};
  if (!isForm) headers["Content-Type"] = "application/json";
  if (withAuth && state.token) headers["Authorization"] = `Bearer ${state.token}`;
  const resp = await fetch(`${baseUrl()}${path}`, {
    method,
    headers,
    body: body ? (isForm ? body : JSON.stringify(body)) : undefined
  });
  const text = await resp.text();
  let parsed = text;
  try { parsed = JSON.parse(text); } catch {}
  return { status: resp.status, body: parsed };
}

async function ensureAuth() {
  if (state.token) return;
  await testAuthFlow();
}

async function ensureGraph() {
  if (state.graphId) return;
  await ensureAuth();
  await testCreateGraph();
}

async function testProviders() {
  return request("GET", "/models/providers");
}

async function testProviderModules() {
  return request("GET", "/models/providers/modules");
}

async function testAuthFlow() {
  const username = `${el.usernamePrefix.value || "testapi_user"}_${nowSeed()}`;
  const password = el.password.value || "TestApiPass123!";
  const register = await request("POST", "/auth/register", {
    username,
    password,
    name: "TestApi User",
    email: `${username}@example.com`,
    role: "admin"
  });
  const login = await request("POST", "/auth/login", {
    username,
    password,
    remember: false
  });
  if (login.status === 200 && login.body?.data?.token) {
    state.token = login.body.data.token;
    state.session = nowSeed();
  }
  return { status: login.status, body: { register, login } };
}

async function testGraphList() {
  await ensureAuth();
  return request("GET", "/graphs/", null, true);
}

async function testCreateGraph() {
  await ensureAuth();
  const ret = await request("POST", "/graphs/", {
    name: `testapi_graph_${nowSeed()}`,
    description: "testapi auto create",
    config: { from: "testapi" }
  }, true);
  if (ret.status === 200 && ret.body?.data?.id) state.graphId = ret.body.data.id;
  return ret;
}

async function testNeo4j() {
  await ensureGraph();
  return request("POST", `/graphs/${state.graphId}/neo4j-test`, null, true);
}

async function testUploadFile() {
  await ensureGraph();
  const form = new FormData();
  const blob = new Blob([`hello from testapi ${new Date().toISOString()}`], { type: "text/plain" });
  form.append("files", blob, "testapi_example.txt");
  return request("POST", `/graphs/${state.graphId}/files/upload`, form, true, true);
}

async function testGraphFiles() {
  await ensureGraph();
  return request("GET", `/graphs/${state.graphId}/files`, null, true);
}

async function runOne(test) {
  const begin = performance.now();
  try {
    const ret = await test.run();
    const ms = Math.round(performance.now() - begin);
    const status = ret?.status ?? 0;
    addResult({ name: test.label, ok: status >= 200 && status < 300, status, body: ret?.body ?? ret, ms });
    return status >= 200 && status < 300;
  } catch (e) {
    const ms = Math.round(performance.now() - begin);
    addResult({ name: test.label, ok: false, status: 0, body: String(e), ms });
    return false;
  }
}

async function runSelected() {
  const picked = selectedTests();
  if (!picked.length) return;
  state.runCount += 1;
  let pass = 0;
  for (const t of picked) {
    const ok = await runOne(t);
    if (ok) pass += 1;
  }
  el.summary.textContent = `第 ${state.runCount} 次执行：通过 ${pass}/${picked.length}，当前 graphId=${state.graphId || "-"}`;
}

el.runSelected.onclick = runSelected;
el.checkAll.onclick = () => [...el.testList.querySelectorAll("input")].forEach(i => i.checked = true);
el.uncheckAll.onclick = () => [...el.testList.querySelectorAll("input")].forEach(i => i.checked = false);
el.clearResults.onclick = () => { el.results.innerHTML = ""; };

renderTests();
