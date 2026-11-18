# CS 550 / CS 450: Collaborative Supply Chain Information System

![License](https://img.shields.io/badge/course-CS%20550%20Database%20Management-blue)
![Status](https://img.shields.io/badge/deployment-live%20on%20render-success)
![Tests](https://img.shields.io/badge/tests-104%2F104%20passed%20(100%25)-brightgreen)

Comprehensive implementation for the **CS 550 Database Management Project Assignment**, covering **Part 1 (Conceptual EER Design & Normalized DDL)**, **Part 2 (HA3: 13 Analytical SQL Views)**, and **Part 3 (Bonus Option: Cloud-Hosted Interactive Web Management Portal)**.

---

## 🔗 Quick Links

* 🌐 **Live Cloud Portal (Render)**: [https://cs-550-supply-chain.onrender.com/](https://cs-550-supply-chain.onrender.com/)
* 📄 **HA3 Submission File**: [`queries.sql`](./queries.sql)
* 📑 **Part 1 Database Design Report**: [`CS550_Project_HA3_Complete_Solution.md`](./CS550_Project_HA3_Complete_Solution.md)
* 📊 **Extended ER Diagram (Vector SVG)**: [`er_diagram.svg`](./er_diagram.svg) | [Interactive Web Viewer (`er_diagram.html`)](./er_diagram.html)
* 📜 **Part 1 DDL with CHECK Constraints**: [`part1_create_tables.sql`](./part1_create_tables.sql)
* 📝 **Part 3 Bonus Report**: [`Part3_Bonus_Project_Report.md`](./Part3_Bonus_Project_Report.md)
* 🧪 **Offline Automated Test Suite**: [`verify_all_dbs_offline.py`](./verify_all_dbs_offline.py)

---

## 📌 Project Overview & Structure

### Part 1: Conceptual Database Design & Relational Modeling
* **EER Specialization Hierarchies**: Models `BusinessEntities` (disjoint subclasses: `Suppliers`, `Manufacturers`, `Customers`, `Shippers`) and `Items` (overlapping subclasses: `MaterialItems`, `ProductItems`).
* **Integrity & Domain Constraints**: Strict checks including `senderId <> recipientId` (prevents self-shipment), `prodItemId <> matItemId` (prevents recursive BOM loops), discount boundary verification (`amt2 >= amt1`, `disc2 >= disc1`), and non-negativity across weights, prices, setup costs, and quantities.
* **DDL Implementation**: Implemented with primary keys, foreign keys (`ON DELETE CASCADE`), and semantic `CHECK` constraints in [`part1_create_tables.sql`](./part1_create_tables.sql).

---

### Part 2: Database Implementation (HA3 = Project Part 2)
Implements all 13 required analytical SQL views in [`queries.sql`](./queries.sql):

1. **`shippedVsCustDemand`**: Total quantity of items shipped to customers vs. customer demand.
2. **`totalManufItems`**: Total product quantities ordered across all manufacturers.
3. **`matsUsedVsShipped`**: Required raw components ($\sum \text{qty} \times \text{qtyMatPerItem}$) vs. materials delivered to each manufacturer.
4. **`producedVsShipped`**: Products shipped out by manufacturer vs. ordered production volume.
5. **`suppliedVsShipped`**: Items dispatched by suppliers vs. ordered supply volume (`suppliedQty`).
6. **`perSupplierCost`**: Total supply cost evaluating tiered marginal volume discount brackets ($amt_1, disc_1, amt_2, disc_2$).
7. **`perManufCost`**: Manufacturing cost ($\sum \text{setUpCost} + \text{qty} \times \text{prodCostPerUnit}$) discounted on base cost exceeding $amt_1$.
8. **`perShipperCost`**: Route-based aggregation ($\text{totalWeight} \times \text{pricePerLb}$ with tiered discounts and $\max(\text{minPackagePrice}, \text{discCost})$ on active routes).
9. **`totalCostBreakDown`**: Summary breakdown of `(supplyCost, manufCost, shippingCost, totalCost)`.
10. **`customersWithUnsatisfiedDemand`**: Customers with unfulfilled item quantities (`suppliedQty < demandQty`).
11. **`suppliersWithUnsentOrders`**: Suppliers with unfulfilled supply commitments (`shippedQty < suppliedQty`).
12. **`manufsWoutEnoughMats`**: Manufacturers lacking components to fulfill production orders (`shippedQty < requiredQty`).
13. **`manufsWithUnsentOrders`**: Manufacturers whose produced goods are not fully shipped (`shippedOutQty < orderedQty`).

#### Verification Results: 100% Pass Rate (104 / 104 Tests)
Tested across all benchmark databases:
```text
[SAMPLEDB]: 13 / 13 Views PASSED
[DB1]:      13 / 13 Views PASSED
[DB2]:      13 / 13 Views PASSED
[DB3]:      13 / 13 Views PASSED
[DB4]:      13 / 13 Views PASSED
[DB5]:      13 / 13 Views PASSED
[DB6]:      13 / 13 Views PASSED
[DB7]:      13 / 13 Views PASSED
SUMMARY: 104 / 104 View Tests Passed (100.0%)
```

---

### Part 3: Bonus Option (Interactive Web Management Portal)
Live at **[https://cs-550-supply-chain.onrender.com/](https://cs-550-supply-chain.onrender.com/)**:
* **Relational View Query Engine**:
  * Execute Projection ($\Pi$) by selecting column checkboxes.
  * Execute Selection ($\sigma$) using multi-operator filters (`=`, `!=`, `>`, `<`, `>=`, `<=`, `LIKE`) with automated type-casting.
  * Live SQL statement preview and dynamic data table rendering.
* **Database Updates (CRUD)**:
  * Browse and inspect all 12 base relational tables.
  * Schema-validated record insertion (`+ Insert New Record`) and row deletion.
  * Switch and reload benchmark datasets (`sampleDB.json`, `db1.json` - `db7.json`).
* **SQL Console**: Interactive ad-hoc SQL execution tool.

---

## 🚀 How to Run Locally

### 1. Run Automated View Tests
```bash
python3 verify_all_dbs_offline.py
```

### 2. Run the Part 3 Web Portal Locally
```bash
python3 app_part3_web_ui.py
```
Then visit [http://localhost:8080/](http://localhost:8080/) in your browser.

---

## 📂 File Directory

```
├── README.md                               # Project documentation & overview
├── queries.sql                             # HA3 Submission File (13 SQL Views)
├── CS550_Project_HA3_Complete_Solution.md  # Comprehensive Solution Report (Part 1 & 2)
├── Part3_Bonus_Project_Report.md           # Part 3 Bonus Report with Screenshot Guide
├── part1_create_tables.sql                 # Part 1 Conceptual DDL with CHECK constraints
├── er_diagram.svg                          # High-resolution vector Extended ER Diagram
├── er_diagram.html                         # Interactive browser viewer for ER Diagram
├── app_part3_web_ui.py                     # Self-contained web server & UI for Part 3
├── Procfile                                # Deployment instruction for cloud platforms
├── requirements.txt                        # Cloud dependency configuration
├── verify_all_dbs_offline.py               # Local automated test harness for all test DBs
├── HA3 DB_Project_Description_CS550.pdf    # Original course project specification
└── cs_450_550_db_project_template/         # University test harness & benchmark DBs
    ├── solution_sql/                       # Official solution workspace
    └── testDBs/                            # Benchmark databases (sampleDB, db1-db7)
```
