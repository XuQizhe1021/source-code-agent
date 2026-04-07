const state = {
  schema: null,
  apis: [],
  selectedApiId: "",
  runCount: 0
};

const el = {
  serverUrl: document.getElementById("serverUrl"),
  openapiPath: document.getElementById("openapiPath"),
  token: document.getElementById("token"),
  commonHeaders: document.getElementById("commonHeaders"),
  reloadSchema: document.getElementById("reloadSchema"),
  searchKeyword: document.getElementById("searchKeyword"),
  methodFilter: document.getElementById("methodFilter"),
  groupFilter: document.getElementById("groupFilter"),
  checkVisible: document.getElementById("checkVisible"),
  uncheckVisible: document.getElementById("uncheckVisible"),
  runSelected: document.getElementById("runSelected"),
  runCurrent: document.getElementById("runCurrent"),
  resetCurrent: document.getElementById("resetCurrent"),
  clearResults: document.getElementById("clearResults"),
  apiList: document.getElementById("apiList"),
  currentApiMeta: document.getElementById("currentApiMeta"),
  pathParams: document.getElementById("pathParams"),
  queryParams: document.getElementById("queryParams"),
  headerParams: document.getElementById("headerParams"),
  bodyParams: document.getElementById("bodyParams"),
  results: document.getElementById("results"),
  summary: document.getElementById("summary")
};

function normalizeToken(v) {
  if (!v) return "";
  return v.replace(/^Bearer\s+/i, "").trim();
}

function safeParseJson(raw, fallback = {}) {
  try {
    const parsed = JSON.parse(raw || "");
    return parsed ?? fallback;
  } catch {
    return fallback;
  }
}

function escapeHtml(str) {
  return String(str)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

function pretty(v) {
  if (typeof v === "string") return v;
  return JSON.stringify(v, null, 2);
}

function getServerUrl() {
  return el.serverUrl.value.replace(/\/+$/, "");
}

function getOpenapiUrl() {
  const p = el.openapiPath.value.trim();
  if (/^https?:\/\//i.test(p)) return p;
  return `${getServerUrl()}${p.startsWith("/") ? p : `/${p}`}`;
}

function methodClass(method) {
  return `m-${method.toLowerCase()}`;
}

function buildGroup(path) {
  const parts = path.split("/").filter(Boolean);
  if (!parts.length) return "/";
  if (parts.length === 1) return `/${parts[0]}`;
  return `/${parts[0]}/${parts[1]}`;
}

function resolveRef(ref) {
  if (!ref || typeof ref !== "string" || !state.schema) return null;
  const seg = ref.replace(/^#\//, "").split("/");
  let cur = state.schema;
  for (const s of seg) {
    if (!(s in cur)) return null;
    cur = cur[s];
  }
  return cur;
}

function schemaExample(schema) {
  if (!schema) return null;
  if (schema.example !== undefined) return schema.example;
  if (schema.default !== undefined) return schema.default;
  if (schema.$ref) return schemaExample(resolveRef(schema.$ref));
  if (schema.enum?.length) return schema.enum[0];
  if (schema.oneOf?.length) return schemaExample(schema.oneOf[0]);
  if (schema.anyOf?.length) return schemaExample(schema.anyOf[0]);
  if (schema.allOf?.length) {
    return schema.allOf.reduce((acc, s) => {
      const ex = schemaExample(s);
      if (typeof ex === "object" && ex && !Array.isArray(ex)) return { ...acc, ...ex };
      return acc;
    }, {});
  }
  if (schema.type === "string") {
    if (schema.format === "date-time") return new Date().toISOString();
    if (schema.format === "email") return "tester@example.com";
    return "string";
  }
  if (schema.type === "integer" || schema.type === "number") return 1;
  if (schema.type === "boolean") return true;
  if (schema.type === "array") return [schemaExample(schema.items)];
  if (schema.type === "object" || schema.properties) {
    const out = {};
    const props = schema.properties || {};
    for (const key of Object.keys(props)) out[key] = schemaExample(props[key]);
    return out;
  }
  return {};
}

function parseOperation(path, method, operation) {
  const parameters = operation.parameters || [];
  const pathParams = {};
  const queryParams = {};
  const headerParams = {};
  for (const p of parameters) {
    const param = p.$ref ? resolveRef(p.$ref) : p;
    if (!param?.name) continue;
    const ex = schemaExample(param.schema || {}) ?? "";
    if (param.in === "path") pathParams[param.name] = ex || "value";
    if (param.in === "query") queryParams[param.name] = ex ?? "";
    if (param.in === "header") headerParams[param.name] = ex ?? "";
  }
  let bodyType = "";
  let bodyParams = {};
  const reqBody = operation.requestBody?.$ref ? resolveRef(operation.requestBody.$ref) : operation.requestBody;
  const content = reqBody?.content || {};
  const contentTypes = Object.keys(content);
  if (contentTypes.length) {
    bodyType = contentTypes[0];
    const bodySchema = content[bodyType]?.schema || {};
    bodyParams = schemaExample(bodySchema) ?? {};
  }
  const tag = operation.tags?.[0] || buildGroup(path);
  const opId = `${method.toUpperCase()} ${path}`;
  return {
    id: opId,
    method: method.toUpperCase(),
    path,
    summary: operation.summary || operation.description || "",
    group: buildGroup(path),
    tag,
    pathParams,
    queryParams,
    headerParams,
    bodyParams,
    bodyType
  };
}

function buildApiList(schema) {
  const apis = [];
  const methods = ["get", "post", "put", "delete", "patch", "options", "head"];
  for (const path of Object.keys(schema.paths || {})) {
    const obj = schema.paths[path];
    for (const m of methods) {
      if (obj[m]) apis.push(parseOperation(path, m, obj[m]));
    }
  }
  return apis.sort((a, b) => {
    if (a.path !== b.path) return a.path.localeCompare(b.path);
    return a.method.localeCompare(b.method);
  });
}

function renderFilters() {
  const methodSet = [...new Set(state.apis.map(a => a.method))];
  const groupSet = [...new Set(state.apis.map(a => a.group))];
  el.methodFilter.innerHTML = `<option value="">全部方法</option>${methodSet.map(m => `<option value="${m}">${m}</option>`).join("")}`;
  el.groupFilter.innerHTML = `<option value="">全部分组</option>${groupSet.map(g => `<option value="${g}">${g}</option>`).join("")}`;
}

function currentFilters() {
  return {
    keyword: el.searchKeyword.value.trim().toLowerCase(),
    method: el.methodFilter.value,
    group: el.groupFilter.value
  };
}

function filteredApis() {
  const f = currentFilters();
  return state.apis.filter(api => {
    if (f.method && api.method !== f.method) return false;
    if (f.group && api.group !== f.group) return false;
    if (!f.keyword) return true;
    const text = `${api.path} ${api.summary} ${api.tag}`.toLowerCase();
    return text.includes(f.keyword);
  });
}

function renderApiList() {
  const visible = filteredApis();
  if (!visible.length) {
    el.apiList.innerHTML = `<div class="empty">当前筛选条件下无接口</div>`;
    return;
  }
  el.apiList.innerHTML = visible.map(api => {
    const isSelected = state.selectedApiId === api.id;
    return `
      <label class="api-item ${isSelected ? "active" : ""}" data-id="${escapeHtml(api.id)}">
        <div class="line1">
          <input type="checkbox" data-check-id="${escapeHtml(api.id)}" />
          <span class="method ${methodClass(api.method)}">${api.method}</span>
          <span class="path">${escapeHtml(api.path)}</span>
        </div>
        <div class="line2">${escapeHtml(api.summary || api.tag || "无摘要")}</div>
      </label>
    `;
  }).join("");
}

function findApiById(id) {
  return state.apis.find(a => a.id === id) || null;
}

function setCurrentApi(id) {
  state.selectedApiId = id;
  const api = findApiById(id);
  if (!api) return;
  el.currentApiMeta.textContent = `${api.method} ${api.path} | ${api.summary || api.tag || "无摘要"}${api.bodyType ? ` | Body: ${api.bodyType}` : ""}`;
  el.pathParams.value = pretty(api.pathParams || {});
  el.queryParams.value = pretty(api.queryParams || {});
  el.headerParams.value = pretty(api.headerParams || {});
  el.bodyParams.value = pretty(api.bodyParams || {});
  renderApiList();
}

function buildRealPath(path, pathParams) {
  return path.replace(/\{([^}]+)\}/g, (_, key) => encodeURIComponent(pathParams[key] ?? `{${key}}`));
}

function buildQueryString(queryObj) {
  const search = new URLSearchParams();
  for (const k of Object.keys(queryObj || {})) {
    const v = queryObj[k];
    if (v === undefined || v === null || v === "") continue;
    if (Array.isArray(v)) {
      for (const item of v) search.append(k, String(item));
    } else {
      search.append(k, String(v));
    }
  }
  const qs = search.toString();
  return qs ? `?${qs}` : "";
}

function buildFormData(data) {
  const form = new FormData();
  for (const key of Object.keys(data || {})) {
    const v = data[key];
    if (v === undefined || v === null) continue;
    if (Array.isArray(v)) {
      for (const item of v) form.append(key, typeof item === "object" ? JSON.stringify(item) : String(item));
    } else if (typeof v === "object") {
      form.append(key, JSON.stringify(v));
    } else {
      form.append(key, String(v));
    }
  }
  return form;
}

async function sendApi(api, params) {
  const startedAt = performance.now();
  const path = buildRealPath(api.path, params.pathParams);
  const query = buildQueryString(params.queryParams);
  const url = `${getServerUrl()}${path}${query}`;
  const commonHeaders = safeParseJson(el.commonHeaders.value, {});
  const token = normalizeToken(el.token.value);
  const headers = { ...commonHeaders, ...params.headerParams };
  if (token) headers.Authorization = `Bearer ${token}`;
  let body = undefined;
  if (!["GET", "HEAD"].includes(api.method)) {
    if (api.bodyType.includes("multipart/form-data")) {
      body = buildFormData(params.bodyParams);
      delete headers["Content-Type"];
    } else {
      headers["Content-Type"] = api.bodyType || "application/json";
      body = JSON.stringify(params.bodyParams ?? {});
    }
  }
  const response = await fetch(url, {
    method: api.method,
    headers,
    body
  });
  const raw = await response.text();
  let parsed = raw;
  try {
    parsed = JSON.parse(raw);
  } catch {}
  const ms = Math.round(performance.now() - startedAt);
  return {
    ok: response.ok,
    status: response.status,
    ms,
    request: {
      method: api.method,
      url,
      headers,
      body: params.bodyParams
    },
    response: parsed
  };
}

function readEditorParams() {
  return {
    pathParams: safeParseJson(el.pathParams.value, {}),
    queryParams: safeParseJson(el.queryParams.value, {}),
    headerParams: safeParseJson(el.headerParams.value, {}),
    bodyParams: safeParseJson(el.bodyParams.value, {})
  };
}

function addResultCard(title, result) {
  const wrap = document.createElement("details");
  wrap.className = `result ${result.ok ? "pass" : "fail"}`;
  wrap.open = !result.ok;
  wrap.innerHTML = `
    <summary>${result.ok ? "✅" : "❌"} ${escapeHtml(title)} | ${result.ms}ms | HTTP ${result.status}</summary>
    <div class="result-body">
      <div class="actions">
        <button class="delete-btn">删除</button>
      </div>
      <h4>Request</h4>
      <pre>${escapeHtml(pretty(result.request))}</pre>
      <h4>Response</h4>
      <pre>${escapeHtml(pretty(result.response))}</pre>
    </div>
  `;
  wrap.querySelector(".delete-btn").onclick = () => wrap.remove();
  el.results.prepend(wrap);
}

async function runCurrentApi() {
  const api = findApiById(state.selectedApiId);
  if (!api) {
    el.summary.textContent = "请先从左侧选择接口";
    return;
  }
  try {
    const params = readEditorParams();
    const result = await sendApi(api, params);
    addResultCard(`${api.method} ${api.path}`, result);
    state.runCount += 1;
    el.summary.textContent = `第 ${state.runCount} 次执行：当前接口 HTTP ${result.status}`;
  } catch (e) {
    el.summary.textContent = `执行失败：${String(e)}`;
  }
}

function checkedApiIds() {
  return [...el.apiList.querySelectorAll("input[data-check-id]:checked")].map(i => i.dataset.checkId);
}

async function runCheckedApis() {
  const ids = checkedApiIds();
  if (!ids.length) {
    el.summary.textContent = "请先勾选接口";
    return;
  }
  let pass = 0;
  for (const id of ids) {
    const api = findApiById(id);
    if (!api) continue;
    const params = {
      pathParams: api.pathParams || {},
      queryParams: api.queryParams || {},
      headerParams: api.headerParams || {},
      bodyParams: api.bodyParams || {}
    };
    try {
      const result = await sendApi(api, params);
      addResultCard(`${api.method} ${api.path}`, result);
      if (result.ok) pass += 1;
    } catch (e) {
      addResultCard(`${api.method} ${api.path}`, {
        ok: false,
        status: 0,
        ms: 0,
        request: params,
        response: String(e)
      });
    }
  }
  state.runCount += 1;
  el.summary.textContent = `第 ${state.runCount} 次批量执行：通过 ${pass}/${ids.length}`;
}

async function loadSchema() {
  el.summary.textContent = "正在加载接口定义...";
  const resp = await fetch(getOpenapiUrl());
  if (!resp.ok) throw new Error(`OpenAPI加载失败: HTTP ${resp.status}`);
  const schema = await resp.json();
  state.schema = schema;
  state.apis = buildApiList(schema);
  renderFilters();
  renderApiList();
  if (state.apis.length) setCurrentApi(state.apis[0].id);
  el.summary.textContent = `已加载 ${state.apis.length} 个接口`;
}

function bindEvents() {
  el.reloadSchema.onclick = async () => {
    try {
      await loadSchema();
    } catch (e) {
      el.summary.textContent = String(e);
    }
  };
  el.searchKeyword.oninput = renderApiList;
  el.methodFilter.onchange = renderApiList;
  el.groupFilter.onchange = renderApiList;
  el.checkVisible.onclick = () => {
    for (const c of el.apiList.querySelectorAll("input[data-check-id]")) c.checked = true;
  };
  el.uncheckVisible.onclick = () => {
    for (const c of el.apiList.querySelectorAll("input[data-check-id]")) c.checked = false;
  };
  el.runSelected.onclick = runCheckedApis;
  el.runCurrent.onclick = runCurrentApi;
  el.resetCurrent.onclick = () => {
    const api = findApiById(state.selectedApiId);
    if (!api) return;
    setCurrentApi(api.id);
  };
  el.clearResults.onclick = () => {
    el.results.innerHTML = "";
  };
  el.apiList.onclick = (e) => {
    const item = e.target.closest(".api-item");
    if (!item) return;
    if (e.target.matches("input[data-check-id]")) return;
    setCurrentApi(item.dataset.id);
  };
}

bindEvents();
loadSchema().catch(e => {
  el.summary.textContent = `初始化失败：${String(e)}`;
});
