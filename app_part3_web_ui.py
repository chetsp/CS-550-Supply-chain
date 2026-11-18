#!/usr/bin/env python3
"""
CS 550 / CS 450: Database Management Project Assignment - Part 3 (Bonus Option)
Web-Based UI for Database Updates and View Selection/Projection Queries

Self-contained web server using Python's standard library http.server + sqlite3.
No external dependencies required (zero npm / zero pip install).
"""

import os
import sys
import json
import sqlite3
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'cs_450_550_db_project_template')
SOLUTION_DIR = os.path.join(TEMPLATE_DIR, 'solution_sql')
TEST_DBS_DIR = os.path.join(TEMPLATE_DIR, 'testDBs')

DB_PATH = os.path.join(BASE_DIR, 'supply_chain_part3.db')

ORDERED_TABLES = [
    "items", "busEntities", "billOfMaterials", "supplierDiscounts",
    "supplyUnitPricing", "manufDiscounts", "manufUnitPricing",
    "shippingPricing", "customerDemand", "supplyOrders", "manufOrders", "shipOrders"
]

ORDERED_VIEWS = [
    'shippedVsCustDemand', 'totalManufItems', 'matsUsedVsShipped',
    'producedVsShipped', 'suppliedVsShipped', 'perSupplierCost', 'perManufCost',
    'perShipperCost', 'totalCostBreakDown', 'customersWithUnsatisfiedDemand',
    'suppliersWithUnsentOrders', 'manufsWoutEnoughMats', 'manufsWithUnsentOrders'
]

def init_database(db_source='sampleDB.json'):
    """Initializes the database schema and loads initial data and views."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Drop existing views and tables
    for v in ORDERED_VIEWS:
        cur.execute(f"DROP VIEW IF EXISTS {v}")
    for t in reversed(ORDERED_TABLES):
        cur.execute(f"DROP TABLE IF EXISTS {t}")
    conn.commit()

    # Load schema
    schema_file = os.path.join(SOLUTION_DIR, 'create_empty_tables.sql')
    with open(schema_file, 'r') as f:
        schema_sql = f.read()
    for stmt in schema_sql.split(';'):
        stmt = stmt.strip()
        if stmt:
            cur.execute(stmt)
    conn.commit()

    # Load data from testDBs
    data_file = os.path.join(TEST_DBS_DIR, db_source)
    if os.path.exists(data_file):
        with open(data_file, 'r') as f:
            db_json = json.load(f)
        for t_name, rows in db_json.get('tables', {}).items():
            if rows:
                cols = sorted(rows[0].keys())
                col_str = ','.join(cols)
                placeholders = ','.join(['?'] * len(cols))
                sql = f"INSERT INTO {t_name} ({col_str}) VALUES ({placeholders})"
                data = [tuple(r.get(c) for c in cols) for r in rows]
                cur.executemany(sql, data)
        conn.commit()

    # Compile the 13 views from queries.sql
    queries_file = os.path.join(BASE_DIR, 'queries.sql')
    if not os.path.exists(queries_file):
        queries_file = os.path.join(SOLUTION_DIR, 'queries.sql')
    with open(queries_file, 'r') as f:
        queries_sql = f.read()
    for stmt in queries_sql.split(';'):
        stmt = stmt.strip()
        if stmt:
            cur.execute(stmt)
    conn.commit()
    conn.close()
    print(f"Database initialized successfully with {db_source}")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# HTML + CSS + JS single-page web UI
HTML_UI = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>CS 550 Supply Chain Management System (Part 3 Bonus UI)</title>
  <style>
    :root {
      --primary: #0f172a;
      --accent: #2563eb;
      --accent-hover: #1d4ed8;
      --bg: #f8fafc;
      --card-bg: #ffffff;
      --border: #e2e8f0;
      --text: #1e293b;
      --text-muted: #64748b;
      --success: #16a34a;
      --danger: #dc2626;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.5;
      padding: 24px;
    }
    header {
      background: var(--primary);
      color: white;
      padding: 20px 28px;
      border-radius: 12px;
      margin-bottom: 24px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
    }
    header h1 { font-size: 22px; font-weight: 700; }
    header p { color: #94a3b8; font-size: 13px; }
    .badge-bonus {
      background: #f59e0b;
      color: #78350f;
      font-size: 11px;
      font-weight: 700;
      padding: 4px 10px;
      border-radius: 6px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }
    .tabs {
      display: flex;
      gap: 12px;
      margin-bottom: 20px;
      border-bottom: 2px solid var(--border);
      padding-bottom: 8px;
    }
    .tab-btn {
      background: none;
      border: none;
      font-size: 15px;
      font-weight: 600;
      color: var(--text-muted);
      padding: 8px 16px;
      cursor: pointer;
      border-radius: 8px;
      transition: all 0.2s;
    }
    .tab-btn.active {
      background: var(--accent);
      color: white;
    }
    .panel { display: none; }
    .panel.active { display: block; }
    .card {
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 20px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.03);
      margin-bottom: 20px;
    }
    .card-title {
      font-size: 16px;
      font-weight: 700;
      margin-bottom: 14px;
      color: var(--primary);
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .controls-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 14px;
      align-items: end;
      margin-bottom: 16px;
    }
    label {
      display: block;
      font-size: 12px;
      font-weight: 600;
      margin-bottom: 6px;
      color: var(--text-muted);
      text-transform: uppercase;
    }
    select, input, button {
      width: 100%;
      padding: 9px 12px;
      border: 1px solid var(--border);
      border-radius: 6px;
      font-size: 14px;
      background: white;
      color: var(--text);
    }
    select:focus, input:focus {
      outline: none;
      border-color: var(--accent);
      box-shadow: 0 0 0 2px rgba(37,99,235,0.15);
    }
    .btn {
      background: var(--accent);
      color: white;
      font-weight: 600;
      border: none;
      cursor: pointer;
      transition: background 0.15s ease;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
    }
    .btn:hover { background: var(--accent-hover); }
    .btn-sm { padding: 6px 12px; font-size: 12px; width: auto; }
    .btn-success { background: var(--success); }
    .btn-success:hover { background: #15803d; }
    .btn-danger { background: var(--danger); }
    .btn-danger:hover { background: #b91c1c; }
    .btn-secondary { background: #64748b; }
    .btn-secondary:hover { background: #475569; }
    
    .checkbox-group {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      padding: 10px;
      background: var(--bg);
      border: 1px solid var(--border);
      border-radius: 6px;
      margin-bottom: 14px;
      max-height: 120px;
      overflow-y: auto;
    }
    .checkbox-item {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 13px;
      font-weight: 500;
    }
    .checkbox-item input { width: auto; margin: 0; }

    .filter-row {
      display: grid;
      grid-template-columns: 2fr 1fr 2fr auto;
      gap: 8px;
      margin-bottom: 8px;
      align-items: center;
    }

    .table-container {
      overflow-x: auto;
      border: 1px solid var(--border);
      border-radius: 8px;
      background: white;
      max-height: 480px;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
      text-align: left;
    }
    th {
      background: #f1f5f9;
      color: var(--primary);
      font-weight: 700;
      padding: 10px 14px;
      position: sticky;
      top: 0;
      border-bottom: 2px solid var(--border);
      z-index: 1;
    }
    td {
      padding: 8px 14px;
      border-bottom: 1px solid var(--border);
    }
    tr:nth-child(even) { background: #f8fafc; }
    tr:hover { background: #f1f5f9; }
    
    .sql-preview {
      background: #0f172a;
      color: #38bdf8;
      font-family: monospace;
      padding: 12px 16px;
      border-radius: 6px;
      font-size: 13px;
      margin-bottom: 16px;
      overflow-x: auto;
    }

    .status-bar {
      margin-top: 10px;
      font-size: 12px;
      color: var(--text-muted);
      display: flex;
      justify-content: space-between;
    }

    /* Modal */
    .modal {
      display: none;
      position: fixed;
      top: 0; left: 0; width: 100%; height: 100%;
      background: rgba(15, 23, 42, 0.6);
      z-index: 999;
      justify-content: center;
      align-items: center;
    }
    .modal.active { display: flex; }
    .modal-content {
      background: white;
      padding: 24px;
      border-radius: 12px;
      width: 500px;
      max-width: 90%;
      max-height: 85vh;
      overflow-y: auto;
      box-shadow: 0 10px 25px rgba(0,0,0,0.2);
    }
    .modal-title { font-size: 18px; font-weight: 700; margin-bottom: 16px; }
    .modal-footer { display: flex; justify-content: flex-end; gap: 10px; margin-top: 18px; }
  </style>
</head>
<body>

  <header>
    <div>
      <h1>CS 550 Collaborative Supply Chain Portal</h1>
      <p>Part 3 Bonus Option: Interactive DB Updates &amp; Relational View Projection/Selection Engine</p>
    </div>
    <span class="badge-bonus">&#9733; Part 3 Bonus UI Active</span>
  </header>

  <div class="tabs">
    <button class="tab-btn active" onclick="switchTab('query-tab')">&#128269; View Queries (Selection &amp; Projection)</button>
    <button class="tab-btn" onclick="switchTab('update-tab')">&#9998; Database Updates (Tables)</button>
    <button class="tab-btn" onclick="switchTab('raw-tab')">&#9881; SQL Console</button>
  </div>

  <!-- TAB 1: VIEW QUERIES (PROJECTION & SELECTION) -->
  <div id="query-tab" class="panel active">
    <div class="card">
      <div class="card-title">
        <span>Query Formulation: 13 SQL Analytics Views</span>
        <button class="btn btn-sm btn-secondary" onclick="resetForm()">Reset Query</button>
      </div>

      <div class="controls-grid">
        <div>
          <label>1. Select View</label>
          <select id="viewSelect" onchange="loadViewMetadata()">
            <option value="">-- Choose View --</option>
          </select>
        </div>

        <div>
          <label>Order By Column</label>
          <select id="orderSelect">
            <option value="">-- Default --</option>
          </select>
        </div>

        <div>
          <label>Order Direction</label>
          <select id="orderDir">
            <option value="ASC">Ascending (ASC)</option>
            <option value="DESC">Descending (DESC)</option>
          </select>
        </div>

        <div>
          <button class="btn" onclick="runViewQuery()">&#9654; Execute Query</button>
        </div>
      </div>

      <!-- Projection Columns -->
      <div>
        <label>2. Projection: Select Columns (&Pi;)</label>
        <div id="projectionBoxes" class="checkbox-group">
          <span style="color: var(--text-muted); font-size: 12px;">Select a view above to view its schema columns.</span>
        </div>
      </div>

      <!-- Selection Filters -->
      <div>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
          <label style="margin: 0;">3. Selection: Filter Conditions (&sigma;)</label>
          <button class="btn btn-sm btn-secondary" onclick="addFilterRow()">+ Add Condition</button>
        </div>
        <div id="filterContainer"></div>
      </div>

      <!-- SQL Preview -->
      <label>Constructed SQL Statement</label>
      <div id="sqlPreview" class="sql-preview">SELECT * FROM [Select a view];</div>

      <!-- Result Table -->
      <div class="card-title" style="margin-top: 20px;">
        <span>Query Execution Results</span>
        <span id="resultCount" style="font-size: 13px; color: var(--text-muted);">0 rows</span>
      </div>
      <div class="table-container">
        <table id="resultsTable">
          <thead><tr><th>No query executed yet.</th></tr></thead>
          <tbody></tbody>
        </table>
      </div>
    </div>
  </div>

  <!-- TAB 2: DB UPDATES (TABLES) -->
  <div id="update-tab" class="panel">
    <div class="card">
      <div class="card-title">
        <span>Base Relational Tables Management</span>
        <div style="display: flex; gap: 8px;">
          <button class="btn btn-sm btn-success" onclick="openInsertModal()">+ Insert New Record</button>
          <select id="datasetSelect" style="width: auto; padding: 4px 8px; font-size: 12px;">
            <option value="sampleDB.json">Reset to sampleDB.json</option>
            <option value="db1.json">Reset to db1.json</option>
            <option value="db2.json">Reset to db2.json</option>
            <option value="db3.json">Reset to db3.json</option>
            <option value="db7.json">Reset to db7.json</option>
          </select>
          <button class="btn btn-sm btn-danger" onclick="resetDatabase()">Reload Dataset</button>
        </div>
      </div>

      <div class="controls-grid" style="grid-template-columns: 1fr auto;">
        <div>
          <label>Select Table to Inspect / Edit</label>
          <select id="tableSelect" onchange="loadTableData()"></select>
        </div>
        <div>
          <button class="btn btn-secondary" onclick="loadTableData()">&#8635; Refresh Table</button>
        </div>
      </div>

      <div class="table-container">
        <table id="baseTable">
          <thead><tr><th>Select a table above</th></tr></thead>
          <tbody></tbody>
        </table>
      </div>
      <div class="status-bar">
        <span id="tableStatus">0 records</span>
        <span>Supports INSERT, UPDATE, and DELETE operations</span>
      </div>
    </div>
  </div>

  <!-- TAB 3: RAW SQL CONSOLE -->
  <div id="raw-tab" class="panel">
    <div class="card">
      <div class="card-title">SQL Command &amp; Query Console</div>
      <label>Enter SQL Query (SELECT, INSERT, UPDATE, DELETE)</label>
      <textarea id="rawSql" rows="4" style="width: 100%; padding: 12px; font-family: monospace; border: 1px solid var(--border); border-radius: 6px; margin-bottom: 12px;">SELECT * FROM perSupplierCost WHERE cost > 1000 ORDER BY cost DESC;</textarea>
      <button class="btn" style="width: 200px;" onclick="runRawSql()">&#9654; Execute SQL</button>

      <div class="card-title" style="margin-top: 24px;">Output</div>
      <div class="table-container">
        <table id="rawTable">
          <thead><tr><th>Results will appear here</th></tr></thead>
          <tbody></tbody>
        </table>
      </div>
    </div>
  </div>

  <!-- INSERT MODAL -->
  <div id="insertModal" class="modal">
    <div class="modal-content">
      <div class="modal-title" id="insertModalTitle">Insert Record</div>
      <form id="insertForm"></form>
      <div class="modal-footer">
        <button class="btn btn-secondary btn-sm" onclick="closeInsertModal()">Cancel</button>
        <button class="btn btn-success btn-sm" onclick="submitInsert()">Save Record</button>
      </div>
    </div>
  </div>

  <script>
    let viewCatalog = {};
    let currentTableCols = [];

    async function init() {
      // Load views
      const vRes = await fetch('/api/views');
      viewCatalog = await vRes.json();
      const vSel = document.getElementById('viewSelect');
      vSel.innerHTML = '<option value="">-- Choose View --</option>';
      for (const vName in viewCatalog) {
        const opt = document.createElement('option');
        opt.value = vName;
        opt.textContent = vName;
        vSel.appendChild(opt);
      }

      // Load tables
      const tRes = await fetch('/api/tables');
      const tables = await tRes.json();
      const tSel = document.getElementById('tableSelect');
      tSel.innerHTML = '';
      tables.forEach(t => {
        const opt = document.createElement('option');
        opt.value = t;
        opt.textContent = t;
        tSel.appendChild(opt);
      });
      loadTableData();
    }

    function switchTab(tabId) {
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
      event.target.classList.add('active');
      document.getElementById(tabId).classList.add('active');
    }

    function loadViewMetadata() {
      const viewName = document.getElementById('viewSelect').value;
      const boxContainer = document.getElementById('projectionBoxes');
      const orderSel = document.getElementById('orderSelect');
      boxContainer.innerHTML = '';
      orderSel.innerHTML = '<option value="">-- Default --</option>';
      document.getElementById('filterContainer').innerHTML = '';

      if (!viewName || !viewCatalog[viewName]) {
        boxContainer.innerHTML = '<span style="color: var(--text-muted); font-size: 12px;">Select a view above.</span>';
        updateSqlPreview();
        return;
      }

      const cols = viewCatalog[viewName];
      cols.forEach(c => {
        // Projection Checkbox
        const div = document.createElement('div');
        div.className = 'checkbox-item';
        div.innerHTML = `<input type="checkbox" id="col_${c}" value="${c}" checked onchange="updateSqlPreview()"> <label for="col_${c}" style="text-transform:none; margin:0;">${c}</label>`;
        boxContainer.appendChild(div);

        // Order by option
        const opt = document.createElement('option');
        opt.value = c;
        opt.textContent = c;
        orderSel.appendChild(opt);
      });

      updateSqlPreview();
    }

    function addFilterRow() {
      const viewName = document.getElementById('viewSelect').value;
      if (!viewName) { alert('Please select a view first.'); return; }
      const cols = viewCatalog[viewName] || [];

      const fContainer = document.getElementById('filterContainer');
      const row = document.createElement('div');
      row.className = 'filter-row';

      let colOptions = cols.map(c => `<option value="${c}">${c}</option>`).join('');
      row.innerHTML = `
        <select class="f-col" onchange="updateSqlPreview()">${colOptions}</select>
        <select class="f-op" onchange="updateSqlPreview()">
          <option value="=">=</option>
          <option value="!=">!=</option>
          <option value=">">&gt;</option>
          <option value="<">&lt;</option>
          <option value=">=">&gt;=</option>
          <option value="<=">&lt;=</option>
          <option value="LIKE">LIKE</option>
        </select>
        <input type="text" class="f-val" placeholder="Value..." oninput="updateSqlPreview()">
        <button class="btn btn-danger btn-sm" onclick="this.parentElement.remove(); updateSqlPreview();">&times;</button>
      `;
      fContainer.appendChild(row);
      updateSqlPreview();
    }

    function buildQueryPayload() {
      const viewName = document.getElementById('viewSelect').value;
      if (!viewName) return null;

      const checkedCols = Array.from(document.querySelectorAll('#projectionBoxes input:checked')).map(i => i.value);
      const filterRows = Array.from(document.querySelectorAll('.filter-row'));
      const conditions = [];

      filterRows.forEach(r => {
        const col = r.querySelector('.f-col').value;
        const op = r.querySelector('.f-op').value;
        const val = r.querySelector('.f-val').value.trim();
        if (val !== '') {
          conditions.push({ col, op, val });
        }
      });

      const orderBy = document.getElementById('orderSelect').value;
      const orderDir = document.getElementById('orderDir').value;

      return { viewName, projection: checkedCols, conditions, orderBy, orderDir };
    }

    function updateSqlPreview() {
      const p = buildQueryPayload();
      const el = document.getElementById('sqlPreview');
      if (!p) { el.textContent = 'SELECT * FROM [Select a view];'; return; }

      const cols = p.projection.length > 0 ? p.projection.join(', ') : '*';
      let sql = `SELECT ${cols} FROM ${p.viewName}`;

      if (p.conditions.length > 0) {
        const condStrs = p.conditions.map(c => {
          const val = isNaN(c.val) ? `'${c.val}'` : c.val;
          return `${c.col} ${c.op} ${val}`;
        });
        sql += ` WHERE ` + condStrs.join(' AND ');
      }

      if (p.orderBy) {
        sql += ` ORDER BY ${p.orderBy} ${p.orderDir}`;
      }
      el.textContent = sql + ';';
    }

    async function runViewQuery() {
      const payload = buildQueryPayload();
      if (!payload) { alert('Please select a view.'); return; }

      const res = await fetch('/api/query-view', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      renderTable('resultsTable', data.columns, data.rows);
      document.getElementById('resultCount').textContent = `${data.rows.length} rows returned`;
    }

    function renderTable(tableId, columns, rows) {
      const table = document.getElementById(tableId);
      if (!columns || columns.length === 0) {
        table.innerHTML = '<thead><tr><th>No records found</th></tr></thead><tbody></tbody>';
        return;
      }
      let html = '<thead><tr>' + columns.map(c => `<th>${c}</th>`).join('') + '</tr></thead><tbody>';
      rows.forEach(r => {
        html += '<tr>' + columns.map(c => `<td>${r[c] !== null ? r[c] : '<i style="color:#94a3b8">null</i>'}</td>`).join('') + '</tr>';
      });
      html += '</tbody>';
      table.innerHTML = html;
    }

    async function loadTableData() {
      const t = document.getElementById('tableSelect').value;
      if (!t) return;
      const res = await fetch(`/api/table/${t}`);
      const data = await res.json();
      currentTableCols = data.columns;

      const table = document.getElementById('baseTable');
      let html = '<thead><tr>' + data.columns.map(c => `<th>${c}</th>`).join('') + '<th>Actions</th></tr></thead><tbody>';
      data.rows.forEach(r => {
        const rowJson = encodeURIComponent(JSON.stringify(r));
        html += '<tr>' + data.columns.map(c => `<td>${r[c] !== null ? r[c] : ''}</td>`).join('') +
          `<td><button class="btn btn-sm btn-danger" onclick="deleteRow('${t}', '${rowJson}')">Delete</button></td></tr>`;
      });
      html += '</tbody>';
      table.innerHTML = html;
      document.getElementById('tableStatus').textContent = `${data.rows.length} records in table "${t}"`;
    }

    function openInsertModal() {
      const t = document.getElementById('tableSelect').value;
      document.getElementById('insertModalTitle').textContent = `Insert Record into ${t}`;
      const form = document.getElementById('insertForm');
      form.innerHTML = '';
      currentTableCols.forEach(c => {
        const div = document.createElement('div');
        div.style.marginBottom = '10px';
        div.innerHTML = `<label>${c}</label><input type="text" name="${c}" required>`;
        form.appendChild(div);
      });
      document.getElementById('insertModal').classList.add('active');
    }

    function closeInsertModal() {
      document.getElementById('insertModal').classList.remove('active');
    }

    async function submitInsert() {
      const t = document.getElementById('tableSelect').value;
      const form = document.getElementById('insertForm');
      const formData = new FormData(form);
      const row = {};
      formData.forEach((val, key) => { row[key] = isNaN(val) || val === '' ? val : Number(val); });

      const res = await fetch(`/api/table/${t}/insert`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(row)
      });
      const resp = await res.json();
      if (resp.success) {
        closeInsertModal();
        loadTableData();
      } else {
        alert('Insert Error: ' + resp.error);
      }
    }

    async function deleteRow(table, rowJson) {
      if (!confirm('Are you sure you want to delete this record?')) return;
      const row = JSON.parse(decodeURIComponent(rowJson));
      const res = await fetch(`/api/table/${table}/delete`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(row)
      });
      const resp = await res.json();
      if (resp.success) {
        loadTableData();
      } else {
        alert('Delete Error: ' + resp.error);
      }
    }

    async function resetDatabase() {
      const ds = document.getElementById('datasetSelect').value;
      if (!confirm(`Reload database with ${ds}? Current changes will be overwritten.`)) return;
      const res = await fetch('/api/reset-db', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ dataset: ds })
      });
      const data = await res.json();
      if (data.success) {
        alert(`Database reloaded with ${ds}!`);
        loadTableData();
      }
    }

    async function runRawSql() {
      const sql = document.getElementById('rawSql').value.trim();
      const res = await fetch('/api/raw-query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sql })
      });
      const data = await res.json();
      if (data.error) {
        alert('SQL Error: ' + data.error);
      } else {
        renderTable('rawTable', data.columns, data.rows);
      }
    }

    function resetForm() {
      document.getElementById('viewSelect').value = '';
      loadViewMetadata();
    }

    window.onload = init;
  </script>
</body>
</html>
"""

class SupplyChainRequestHandler(BaseHTTPRequestHandler):
    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def do_GET(self):
        url = urllib.parse.urlparse(self.path)
        path = url.path

        if path == '/' or path == '/index.html':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(HTML_UI.encode('utf-8'))
            return

        if path == '/api/tables':
            self._send_json(ORDERED_TABLES)
            return

        if path == '/api/views':
            conn = get_connection()
            cur = conn.cursor()
            view_meta = {}
            for v in ORDERED_VIEWS:
                try:
                    cur.execute(f"SELECT * FROM {v} LIMIT 0")
                    view_meta[v] = [d[0] for d in cur.description]
                except Exception as e:
                    view_meta[v] = []
            conn.close()
            self._send_json(view_meta)
            return

        if path.startswith('/api/table/'):
            table_name = path.split('/')[-1]
            if table_name not in ORDERED_TABLES:
                self._send_json({"error": "Invalid table"}, status=400)
                return
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(f"SELECT * FROM {table_name}")
            cols = [d[0] for d in cur.description]
            rows = [dict(r) for r in cur.fetchall()]
            conn.close()
            self._send_json({"columns": cols, "rows": rows})
            return

        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        url = urllib.parse.urlparse(self.path)
        path = url.path
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length).decode('utf-8') if length > 0 else '{}'
        data = json.loads(body) if body else {}

        if path == '/api/query-view':
            view_name = data.get('viewName')
            if view_name not in ORDERED_VIEWS:
                self._send_json({"error": "Invalid view"}, status=400)
                return

            projection = data.get('projection', [])
            conditions = data.get('conditions', [])
            order_by = data.get('orderBy', '')
            order_dir = data.get('orderDir', 'ASC')

            proj_cols = ', '.join(projection) if projection else '*'
            sql = f"SELECT {proj_cols} FROM {view_name}"
            params = []

            if conditions:
                where_clauses = []
                for c in conditions:
                    col = c.get('col')
                    op = c.get('op', '=')
                    val = c.get('val')
                    if isinstance(val, str):
                        try:
                            if '.' in val:
                                val = float(val)
                            else:
                                val = int(val)
                        except ValueError:
                            pass
                    where_clauses.append(f"{col} {op} ?")
                    params.append(val)
                sql += " WHERE " + " AND ".join(where_clauses)

            if order_by:
                sql += f" ORDER BY {order_by} {order_dir}"

            conn = get_connection()
            cur = conn.cursor()
            try:
                cur.execute(sql, params)
                cols = [d[0] for d in cur.description]
                rows = [dict(r) for r in cur.fetchall()]
                self._send_json({"columns": cols, "rows": rows, "sql": sql})
            except Exception as e:
                self._send_json({"error": str(e)}, status=500)
            finally:
                conn.close()
            return

        if path.startswith('/api/table/') and path.endswith('/insert'):
            table_name = path.split('/')[-2]
            if table_name not in ORDERED_TABLES:
                self._send_json({"error": "Invalid table"}, status=400)
                return
            conn = get_connection()
            cur = conn.cursor()
            cols = list(data.keys())
            placeholders = ', '.join(['?'] * len(cols))
            sql = f"INSERT INTO {table_name} ({', '.join(cols)}) VALUES ({placeholders})"
            try:
                cur.execute(sql, list(data.values()))
                conn.commit()
                self._send_json({"success": True})
            except Exception as e:
                self._send_json({"success": False, "error": str(e)})
            finally:
                conn.close()
            return

        if path.startswith('/api/table/') and path.endswith('/delete'):
            table_name = path.split('/')[-2]
            if table_name not in ORDERED_TABLES:
                self._send_json({"error": "Invalid table"}, status=400)
                return
            conn = get_connection()
            cur = conn.cursor()
            where_clauses = [f"{k} = ?" for k in data.keys()]
            sql = f"DELETE FROM {table_name} WHERE {' AND '.join(where_clauses)}"
            try:
                cur.execute(sql, list(data.values()))
                conn.commit()
                self._send_json({"success": True})
            except Exception as e:
                self._send_json({"success": False, "error": str(e)})
            finally:
                conn.close()
            return

        if path == '/api/reset-db':
            dataset = data.get('dataset', 'sampleDB.json')
            init_database(dataset)
            self._send_json({"success": True, "dataset": dataset})
            return

        if path == '/api/raw-query':
            sql = data.get('sql', '').strip()
            conn = get_connection()
            cur = conn.cursor()
            try:
                cur.execute(sql)
                if sql.upper().startswith('SELECT'):
                    cols = [d[0] for d in cur.description]
                    rows = [dict(r) for r in cur.fetchall()]
                    self._send_json({"columns": cols, "rows": rows})
                else:
                    conn.commit()
                    self._send_json({"columns": ["Status"], "rows": [{"Status": f"Success. Rows affected: {cur.rowcount}"}]})
            except Exception as e:
                self._send_json({"error": str(e)})
            finally:
                conn.close()
            return

        self.send_response(404)
        self.end_headers()

def run_server(port=8080):
    init_database('sampleDB.json')
    server_address = ('', port)
    httpd = HTTPServer(server_address, SupplyChainRequestHandler)
    print(f"\n" + "=" * 70)
    print(f"CS 550 Supply Chain Management System - Part 3 Bonus UI Server")
    print(f"=" * 70)
    print(f"Server running at: http://localhost:{port}/")
    print(f"Open http://localhost:{port}/ in your web browser.")
    print(f"Press Ctrl+C to stop the server.")
    print("=" * 70 + "\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
        httpd.server_close()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    run_server(port)
