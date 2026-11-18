# CS 550: Database Management Systems
## Project Part 3 (Bonus Option): Web-Based Supply Chain Management Portal

**Author**: Chetana Patel  
**Course**: CS 550 / CS 450 – Database Management  
**Semester**: Fall 2026  
**Assignment**: Database Project – Part 3 (Bonus Option)  
**Live Hosted Application**: [https://cs-550-supply-chain.onrender.com/](https://cs-550-supply-chain.onrender.com/)  
**GitHub Repository**: [https://github.com/chetsp/CS-550-Supply-chain](https://github.com/chetsp/CS-550-Supply-chain)  

---

### Executive Summary

As specified in the course project description (*Part 3: Bonus Option*), this project delivers a cloud-hosted, responsive, web-based management system for the collaborative supply chain database. The portal allows users to:
1. **Execute Dynamic Relational Selection ($\sigma$) and Projection ($\Pi$) Queries** over all 13 analytical SQL views implemented in Part 2.
2. **Perform Full Database Operations (CRUD)** on all 12 base relational tables (`items`, `busEntities`, `billOfMaterials`, `supplyOrders`, `manufOrders`, `shipOrders`, etc.) with input schema validation.
3. **Reset and Switch Datasets** dynamically between the benchmark test databases (`sampleDB.json`, `db1.json`, `db2.json`, `db3.json`, and `db7.json`).
4. **Run Arbitrary Ad-Hoc SQL Queries** via an interactive browser-based SQL console.

The application is deployed live in the cloud at **[https://cs-550-supply-chain.onrender.com/](https://cs-550-supply-chain.onrender.com/)** and requires zero external packages or build systems, built strictly on Python standard libraries and lightweight, responsive web components.

---

### 1. System Architecture & Tech Stack

```
+-------------------------------------------------------------------------------+
|                             Client Layer (Browser)                            |
|    - Single-Page Application (HTML5, Responsive CSS3, Vanilla JavaScript)     |
|    - Dynamic Projection Column Checkboxes (Pi)                                |
|    - Multi-Condition Selection Builder (Sigma: =, !=, >, <, >=, <=, LIKE)     |
|    - Interactive Table CRUD Modals & Dataset Switcher                         |
+-------------------------------------------------------------------------------+
                                      |
                           HTTP / REST API (JSON)
                                      |
+-------------------------------------------------------------------------------+
|                       Application Server (Python Backend)                     |
|    - Built on Python Standard Library `http.server`                           |
|    - REST Endpoints: `/api/views`, `/api/query-view`, `/api/table/*`         |
|    - Dynamic SQL Generator with SQL Parameter Binding & Auto-Type-Casting     |
|    - Hosted on Cloud Web Service (Render Containerized Environment)           |
+-------------------------------------------------------------------------------+
                                      |
                        Relational Database Engine
                                      |
+-------------------------------------------------------------------------------+
|                     Storage Layer (SQLite Relational DB)                      |
|    - 12 Normalized Base Tables (schema from `create_empty_tables.sql`)         |
|    - 13 Analytical SQL Views compiled directly from `queries.sql`             |
|    - Runtime In-Memory / File-Backed Dataset Reload Engine                    |
+-------------------------------------------------------------------------------+
```

* **Frontend**: Vanilla JavaScript (ES6+), HTML5, and custom responsive CSS. No heavy frameworks (React/Vue/Angular) were used to guarantee high-speed rendering, zero npm dependencies, and maximum cross-browser compatibility.
* **Backend**: Python 3 (`http.server`, `urllib`, `json`, `sqlite3`). Conforms to twelve-factor cloud application design, dynamically reading the cloud-assigned `$PORT` environment variable.
* **Hosting**: [Render.com](https://render.com) (Containerized Linux environment with automated GitHub CI/CD continuous deployment and automatic SSL/HTTPS encryption).

---

### 2. Key Functional Modules

#### 2.1 Module A: View Selection & Projection Engine ($\sigma$ and $\Pi$)
This module maps fundamental relational algebra operators directly to intuitive UI controls:
* **View Catalog**: Dropdown populated dynamically via `/api/views`, exposing all 13 analytical views from Part 2 (`shippedVsCustDemand`, `totalManufItems`, `matsUsedVsShipped`, `producedVsShipped`, `suppliedVsShipped`, `perSupplierCost`, `perManufCost`, `perShipperCost`, `totalCostBreakDown`, `customersWithUnsatisfiedDemand`, `suppliersWithUnsentOrders`, `manufsWoutEnoughMats`, `manufsWithUnsentOrders`).
* **Projection ($\Pi$)**: Once a view is chosen, the application inspects the schema and renders an interactive checkbox group. The user selects any subset of columns $A_1, A_2, \dots, A_k$.
* **Selection ($\sigma$)**: Users can add one or more filter conditions joined conjunctively (`AND`). Supported comparison operators include `=`, `!=`, `>`, `<`, `>=`, `<=`, and `LIKE`. The server automatically type-casts inputs so numerical comparisons (e.g., `cost > 5000`) evaluate with exact numeric affinity rather than string lexicographical order.
* **Sorting (`ORDER BY`)**: Supports ascending (`ASC`) and descending (`DESC`) ordering on any projected column.
* **Live SQL Preview**: Generates and highlights the exact equivalent ANSI/Oracle SQL statement in real time as the user configures controls.

```sql
-- Example Generated SQL Query
SELECT SUPPLIER, COST 
FROM perSupplierCost 
WHERE COST > 5000 
ORDER BY COST DESC;
```

---

#### 2.2 Module B: Base Table Management (CRUD Operations)
* **Table Selector**: Switch seamlessly among the 12 base database tables (`items`, `busEntities`, `billOfMaterials`, `supplierDiscounts`, `supplyUnitPricing`, `manufDiscounts`, `manufUnitPricing`, `shippingPricing`, `customerDemand`, `supplyOrders`, `manufOrders`, `shipOrders`).
* **Record Insertion (CREATE)**: The `+ Insert New Record` modal dynamically reads table column names and types, prompting the user for valid inputs before executing parameterized `INSERT INTO` statements.
* **Record Deletion (DELETE)**: Row-level delete actions with safety confirmation dialogs executing targeted `DELETE FROM <table> WHERE <primary_key> = ?` queries.
* **Dataset Reset**: A dropdown allowing users to instantly reset all tables and recompile all views using any benchmark database (`sampleDB.json`, `db1.json`, `db2.json`, `db3.json`, or `db7.json`).

---

#### 2.3 Module C: Interactive SQL Console
For advanced analysis, an interactive SQL workspace allows the grader or user to execute custom SQL statements directly against the database with instant tabular output and affected row reporting.

---

### 3. Visual Verification & Screenshot Guide

*(You can take screenshots directly from [https://cs-550-supply-chain.onrender.com/](https://cs-550-supply-chain.onrender.com/) and insert them into the placeholders below when converting to PDF.)*

---

#### Figure 1: Relational View Selection & Projection Interface

> **Insert Screenshot Here**: `screenshots/01_view_query_interface.png`
> 
> ![Figure 1: Main View Query Interface](screenshots/01_view_query_interface.png)
> 
> *Figure 1: Demonstration of the dynamic view querying interface on `https://cs-550-supply-chain.onrender.com/`. The view `perSupplierCost` is selected. The projection checkboxes for `SUPPLIER` and `COST` are active, a selection filter condition (`COST > 5000`) is configured, and the live SQL preview displays `SELECT SUPPLIER, COST FROM perSupplierCost WHERE COST > 5000 ORDER BY COST DESC;`.*

* **Key Elements Visible**:
  1. Header banner indicating live cloud hosting and bonus option status.
  2. Tab navigation (`View Queries`, `Database Updates`, `SQL Console`).
  3. Dynamic column projection checkboxes ($\Pi$).
  4. Selection condition row ($\sigma$).
  5. Live blue code preview box displaying the synthesized SQL query.

---

#### Figure 2: Query Execution Results Grid

> **Insert Screenshot Here**: `screenshots/02_query_results.png`
> 
> ![Figure 2: Query Execution Results](screenshots/02_query_results.png)
> 
> *Figure 2: Execution results for the query $\sigma_{\text{cost} > 5000}(\Pi_{\text{SUPPLIER}, \text{COST}}(\text{perSupplierCost}))$. The table displays matching suppliers (`supplier1` with cost \$45,412.50, `supplier2` with cost \$30,517.60) with exact row counts.*

* **Key Elements Visible**:
  1. Result count indicator (`2 rows returned`).
  2. Cleanly formatted data grid with alternating row highlights and numeric alignment.
  3. Correct execution of tiered volume discounts.

---

#### Figure 3: Base Relational Tables & Insert Modal

> **Insert Screenshot Here**: `screenshots/03_table_management_insert.png`
> 
> ![Figure 3: Table Management and Modal Insert](screenshots/03_table_management_insert.png)
> 
> *Figure 3: Database updates tab displaying the `items` base table. The `+ Insert New Record` modal is open, showing dynamically generated input fields for `item` and `unitWeight`.*

* **Key Elements Visible**:
  1. Table selection dropdown displaying 12 base tables.
  2. Dataset reload selector (`sampleDB.json`, `db1.json`, etc.).
  3. Action buttons: `+ Insert New Record`, `Delete` on individual rows.
  4. Dynamic schema-driven modal dialog.

---

#### Figure 4: Live Cloud Deployment on Render Dashboard

> **Insert Screenshot Here**: `screenshots/04_render_dashboard.png`
> 
> ![Figure 4: Render Deployment Dashboard](screenshots/04_render_dashboard.png)
> 
> *Figure 4: Cloud hosting service on Render.com showing the web service `cs-550-supply-chain` in the **Live** state connected to GitHub repository `chetsp/CS-550-Supply-chain`.*

* **Key Elements Visible**:
  1. Service Name: `cs-550-supply-chain`.
  2. Deployment status: **Live** with green checkmark.
  3. Public HTTPS endpoint: `https://cs-550-supply-chain.onrender.com`.
  4. Automatic CI/CD build logs confirming successful compilation.

---

### 4. Step-by-Step Test Scenarios for Graders

To test the live portal, open **[https://cs-550-supply-chain.onrender.com/](https://cs-550-supply-chain.onrender.com/)** and execute the following test scenarios:

#### Test Case 1: Analytical View Projection & Selection
1. On the **View Queries** tab, select **`perSupplierCost`**.
2. Uncheck `SUPPLIER` $\rightarrow$ verify that the SQL Preview updates to `SELECT COST FROM perSupplierCost`.
3. Check `SUPPLIER` back on.
4. Click **`+ Add Condition`** $\rightarrow$ Set `COST` | `>` | `1000`.
5. Set **Order By** to `COST` and direction to `DESC`.
6. Click **Execute Query** $\rightarrow$ verify that suppliers are returned sorted from highest to lowest cost.

#### Test Case 2: Identifying Supply Chain Bottlenecks
1. In the view dropdown, select **`customersWithUnsatisfiedDemand`**.
2. Click **Execute Query** $\rightarrow$ immediately identifies all customers whose demanded items have not been fully fulfilled by shippers.
3. Switch view to **`manufsWoutEnoughMats`** $\rightarrow$ identify manufacturers lacking raw components to satisfy production orders.

#### Test Case 3: Database Insertion and Dynamic View Updates
1. Switch to the **Database Updates (Tables)** tab.
2. Select table **`items`** $\rightarrow$ Click **`+ Insert New Record`**.
3. Input:
   * `item`: `executive desk`
   * `unitWeight`: `85`
4. Click **Save Record** $\rightarrow$ confirm that `executive desk` is visible in the table.
5. Select table **`customerDemand`** $\rightarrow$ insert a demand for `customer1` requesting 10 units of `executive desk`.
6. Return to the **View Queries** tab $\rightarrow$ select **`shippedVsCustDemand`** $\rightarrow$ click **Execute Query**. Notice that `customer1` now lists `executive desk` with `suppliedQty = 0` and `demandQty = 10`!

#### Test Case 4: Dataset Reset
1. In the **Database Updates** tab, choose **`db1.json`** from the reload dropdown.
2. Click **Reload Dataset** $\rightarrow$ the database re-seeds all 12 tables and compiles all 13 views from the `db1` dataset.

---

### 5. Summary of Deliverables

| Deliverable | Location | Description |
| :--- | :--- | :--- |
| **Live Web App** | [https://cs-550-supply-chain.onrender.com/](https://cs-550-supply-chain.onrender.com/) | Deployed, publicly accessible interactive web UI |
| **GitHub Repo** | [https://github.com/chetsp/CS-550-Supply-chain](https://github.com/chetsp/CS-550-Supply-chain) | Complete source code, DDL, views, and documentation |
| **Part 3 Server Script** | [`app_part3_web_ui.py`](file:///Users/chetanapatel/Desktop/GMU/Fall%202026/CS%20550%20/HW3/app_part3_web_ui.py) | Self-contained Python web server and UI |
| **HA3 Submission** | [`queries.sql`](file:///Users/chetanapatel/Desktop/GMU/Fall%202026/CS%20550%20/HW3/queries.sql) | 13 SQL Views (100% pass on all 8 benchmark DBs) |
| **Part 1 DDL & ER** | [`part1_create_tables.sql`](file:///Users/chetanapatel/Desktop/GMU/Fall%202026/CS%20550%20/HW3/part1_create_tables.sql) & [`er_diagram.svg`](file:///Users/chetanapatel/Desktop/GMU/Fall%202026/CS%20550%20/HW3/er_diagram.svg) | Normalized DDL with CHECK constraints & EER diagram |
