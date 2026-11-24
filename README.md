# Enterprise ERP Implementation Platform
A portfolio-ready ERP simulation for a manufacturing business, aligned to an ERP Implementation Trainee role.

## Business scenario
A mid-sized manufacturer purchases raw materials from suppliers, receives goods into inventory, plans production using a Bill of Materials (BOM), fulfils customer orders, and monitors operational performance.

## JD alignment
- SCM modules: inventory, procurement, order management and planning
- Manufacturing: BOM, material requirements planning (MRP), production orders and costing
- ERP implementation lifecycle: requirements, configuration, testing, migration, cutover simulation and support logs
- Integration: REST API using FastAPI; CSV/Excel data migration and validation
- Reporting: Streamlit operational dashboard and downloadable reports

## Technology
Python, SQL (SQLite for zero-setup demo), Pandas, Streamlit, FastAPI, Pydantic, Excel/CSV.

## Run locally
```bash
python -m venv .venv
# Windows:
.venv\\Scripts\\activate
# Ubuntu/macOS:
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```
Open the URL printed by Streamlit (usually http://localhost:8501).

## Run the REST API
In a second terminal:
```bash
uvicorn api:app --reload
```
Open http://127.0.0.1:8000/docs for interactive API documentation.

## Demo login
No login is required. This is a local portfolio demo, not a production ERP.

## Included modules
1. Executive dashboard
2. Procurement & supplier management
3. Inventory and goods receipt
4. Sales orders
5. Manufacturing planning (BOM + MRP)
6. Data migration workbench
7. Implementation tracker (requirements, test cases, issues and cutover checklist)

## Demo workflow
1. Open Procurement and create a purchase order.
2. Open Inventory and receive the purchase order to increase on-hand stock.
3. Open Manufacturing Planning and calculate material requirements for a product quantity.
4. Open Sales Orders and review order status.
5. Use Data Migration to upload a CSV with `sku,name,category,uom,on_hand,reorder_level,unit_cost` columns.
6. Open Implementation Tracker to review requirements, UAT cases, issues and cutover readiness.

## Deploy on Render
Create a new **Web Service** from the GitHub repository.
- Build command: `pip install -r requirements.txt`
- Start command for Streamlit: `streamlit run app.py --server.address 0.0.0.0 --server.port $PORT`
- Set environment variable `PYTHON_VERSION` to a supported version such as `3.11.9` if needed.

For API deployment separately, use:
- Start command: `uvicorn api:app --host 0.0.0.0 --port $PORT`

## Important limitations
This is a realistic learning/demo simulation, not a certified Oracle/SAP implementation. It uses SQLite and synthetic data. Do not claim production ERP deployment or real client integration. Extend it with PostgreSQL, authentication, role-based access, audit trails, and a real ERP connector before production use.

## Resume project title
**Enterprise ERP Implementation & Supply Chain Operations Platform**

Suggested resume bullets (edit metrics only after measuring your own run):
- Built an ERP-style application covering procurement, inventory, supplier management, sales orders, BOM-driven material planning and manufacturing costing.
- Implemented SQL-backed business workflows and REST APIs with FastAPI/Pydantic, including purchase-order creation, goods receipt and inventory updates.
- Developed CSV/Excel data migration validation and operational dashboards to track stock risks, procurement spend, order fulfilment and UAT readiness.
