#!/usr/bin/env python3
"""
Offline Test Harness for CS 550 / CS 450 - Project Part 2 (HA3)
Tests queries.sql against all test databases (sampleDB, db1-db7)
using an in-memory SQLite engine without requiring GMU VPN or Oracle credentials.
"""

import sys
import os
import json
import sqlite3

def run_offline_tests():
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Determine base template directory
    if os.path.exists(os.path.join(script_dir, 'cs_450_550_db_project_template')):
        template_dir = os.path.join(script_dir, 'cs_450_550_db_project_template')
    elif os.path.basename(script_dir) == 'solution_sql':
        template_dir = os.path.abspath(os.path.join(script_dir, '..'))
    else:
        template_dir = script_dir

    solution_dir = os.path.join(template_dir, 'solution_sql')
    test_dbs_dir = os.path.join(template_dir, 'testDBs')

    # Look for queries.sql in script_dir or solution_dir
    if os.path.exists(os.path.join(script_dir, 'queries.sql')):
        sql_path = os.path.join(script_dir, 'queries.sql')
    else:
        sql_path = os.path.join(solution_dir, 'queries.sql')

    schema_path = os.path.join(solution_dir, 'create_empty_tables.sql')
    sample_path = os.path.join(test_dbs_dir, 'sampleDB.json')
    sample_ans_path = os.path.join(solution_dir, 'sampleDBanswers.json')
    correct_ans_path = os.path.join(test_dbs_dir, 'correct_answers.json')

    if not os.path.exists(sql_path):
        print(f"Error: {sql_path} not found.")
        sys.exit(1)

    with open(schema_path) as f:
        schema_sql = f.read()

    with open(sql_path) as f:
        queries_sql = f.read()

    with open(sample_ans_path) as f:
        sample_expected = json.load(f)['sampleDB']

    with open(correct_ans_path) as f:
        all_expected = json.load(f)

    view_names = [
        'shippedVsCustDemand', 'totalManufItems', 'matsUsedVsShipped',
        'producedVsShipped', 'suppliedVsShipped', 'perSupplierCost', 'perManufCost',
        'perShipperCost', 'totalCostBreakDown', 'customersWithUnsatisfiedDemand',
        'suppliersWithUnsentOrders', 'manufsWoutEnoughMats', 'manufsWithUnsentOrders'
    ]

    tests = [('sampleDB', sample_path, sample_expected)]
    for i in range(1, 8):
        db_name = f'db{i}'
        tests.append((db_name, os.path.join(test_dbs_dir, f'{db_name}.json'), all_expected[db_name]))

    def norm_val(val):
        if isinstance(val, float):
            return round(val, 2)
        return val

    print("=" * 70)
    print("CS 550 / HA3: Automated Offline Verification for queries.sql")
    print(f"Testing SQL file: {sql_path}")
    print("=" * 70)

    total_views_tested = 0
    total_views_passed = 0

    for db_name, db_file, expected_dict in tests:
        conn = sqlite3.connect(':memory:')
        for stmt in schema_sql.split(';'):
            if stmt.strip():
                conn.execute(stmt.strip())

        with open(db_file) as f:
            db_data = json.load(f)

        for t_name, rows in db_data['tables'].items():
            if not rows:
                continue
            cols = sorted(rows[0].keys())
            col_str = ','.join(cols)
            placeholders = ','.join(['?'] * len(cols))
            sql = f"INSERT INTO {t_name} ({col_str}) VALUES ({placeholders})"
            data = [tuple(r[c] for c in cols) for r in rows]
            conn.executemany(sql, data)

        for stmt in queries_sql.split(';'):
            if stmt.strip():
                conn.execute(stmt.strip())

        passed_views = []
        failed_views = []

        for v in view_names:
            total_views_tested += 1
            cur = conn.cursor()
            cur.execute(f"SELECT * FROM {v}")
            cols = [d[0].upper() for d in cur.description]
            rows = [dict(zip(cols, r)) for r in cur.fetchall()]
            exp = expected_dict[v]

            norm_rows = [{k: norm_val(val) for k, val in r.items()} for r in rows]
            norm_exp = [{k: norm_val(val) for k, val in r.items()} for r in exp]

            exp_c = list(norm_exp)
            match = len(norm_rows) == len(norm_exp)
            if match:
                for r in norm_rows:
                    if r in exp_c:
                        exp_c.remove(r)
                    else:
                        match = False
                        break
            if match:
                passed_views.append(v)
                total_views_passed += 1
            else:
                failed_views.append(v)

        if not failed_views:
            print(f"[{db_name.upper()}]: 13 / 13 Views PASSED")
        else:
            print(f"[{db_name.upper()}]: {len(passed_views)} / 13 Views Passed. Failed: {failed_views}")

    print("=" * 70)
    print(f"SUMMARY: {total_views_passed} / {total_views_tested} View Tests Passed ({(total_views_passed/total_views_tested)*100:.1f}%)")
    print("=" * 70)

if __name__ == '__main__':
    run_offline_tests()
