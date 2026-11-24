import streamlit as st
import pandas as pd
import numpy as np
from datetime import date
from db import init_db, query_df, execute, connect

st.set_page_config(page_title="Enterprise ERP Platform", page_icon="🏭", layout="wide")
init_db()

st.title("🏭 Enterprise ERP Implementation Platform")
st.caption("Manufacturing • Supply Chain • Procurement • Inventory • Planning • Integration")
st.sidebar.title("ERP Navigation")
page = st.sidebar.radio("Select module", [
    "Executive Dashboard", "Procurement", "Inventory", "Sales Orders",
    "Manufacturing Planning", "Data Migration", "Implementation Tracker"
])
st.sidebar.info("Portfolio demonstration using synthetic manufacturing data.")

def money(x):
    return f"₹{x:,.2f}"

if page == "Executive Dashboard":
    products = query_df("SELECT * FROM products")
    pos = query_df("SELECT * FROM purchase_orders")
    sales = query_df("SELECT * FROM sales_orders")
    suppliers = query_df("SELECT * FROM suppliers")
    low = products[products.on_hand <= products.reorder_level]
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Active SKUs", len(products))
    c2.metric("Low-stock SKUs", len(low), delta=f"{len(low)} need attention" if len(low) else "Healthy")
    c3.metric("Open purchase orders", int((pos.status=="Open").sum()))
    c4.metric("Open sales orders", int((sales.status=="Open").sum()))
    left,right = st.columns(2)
    with left:
        st.subheader("Inventory position")
        chart = products[["name","on_hand","reorder_level"]].set_index("name")
        st.bar_chart(chart)
    with right:
        st.subheader("Procurement spend by SKU")
        spend = pos.assign(spend=pos.quantity*pos.unit_price).groupby("sku").spend.sum()
        st.bar_chart(spend)
    st.subheader("Stock exception report")
    st.dataframe(low[["sku","name","on_hand","reorder_level","unit_cost"]], use_container_width=True)
    st.subheader("Recent sales orders")
    st.dataframe(sales.sort_values("so_id",ascending=False).head(8), use_container_width=True)

elif page == "Procurement":
    st.header("Procurement & Supplier Management")
    suppliers = query_df("SELECT * FROM suppliers WHERE active=1")
    products = query_df("SELECT * FROM products")
    a,b = st.columns([1,1])
    with a:
        st.subheader("Create purchase order")
        with st.form("new_po"):
            supplier = st.selectbox("Supplier", suppliers.supplier_id, format_func=lambda x: suppliers.loc[suppliers.supplier_id==x,"name"].iloc[0])
            sku = st.selectbox("Material / SKU", products.sku)
            qty = st.number_input("Order quantity", min_value=1.0, value=100.0)
            price = st.number_input("Unit price (₹)", min_value=0.0, value=float(products.loc[products.sku==sku,"unit_cost"].iloc[0]))
            submitted = st.form_submit_button("Create purchase order")
            if submitted:
                po = execute("INSERT INTO purchase_orders(supplier_id,sku,quantity,unit_price,status) VALUES(?,?,?,?,?)",(int(supplier),sku,qty,price,"Open"))
                st.success(f"Purchase order PO-{po:04d} created.")
    with b:
        st.subheader("Supplier scorecard")
        st.dataframe(suppliers[["name","lead_time_days","rating","contact_email"]], use_container_width=True)
    st.subheader("Purchase order register")
    pos = query_df("""SELECT p.po_id,s.name supplier,p.sku,p.quantity,p.unit_price,
                      p.quantity*p.unit_price total,p.status,p.created_at
                      FROM purchase_orders p LEFT JOIN suppliers s ON p.supplier_id=s.supplier_id
                      ORDER BY p.po_id DESC""")
    st.dataframe(pos, use_container_width=True)
    st.download_button("Download PO register CSV", pos.to_csv(index=False), "purchase_orders.csv", "text/csv")

elif page == "Inventory":
    st.header("Inventory & Goods Receipt")
    products = query_df("SELECT * FROM products")
    st.subheader("Current stock")
    st.dataframe(products, use_container_width=True)
    pos = query_df("""SELECT po.po_id, po.sku, pr.name, po.quantity, po.status
                      FROM purchase_orders po JOIN products pr ON pr.sku=po.sku
                      WHERE po.status='Open'""")
    st.subheader("Receive goods against an open PO")
    if pos.empty:
        st.info("No open purchase orders.")
    else:
        with st.form("receive"):
            po_id = st.selectbox("Purchase order", pos.po_id, format_func=lambda x: f"PO-{x:04d} | {pos.loc[pos.po_id==x,'sku'].iloc[0]} | Qty {pos.loc[pos.po_id==x,'quantity'].iloc[0]}")
            max_qty = float(pos.loc[pos.po_id==po_id,"quantity"].iloc[0])
            received = st.number_input("Quantity received", min_value=0.1, max_value=max_qty, value=max_qty)
            go = st.form_submit_button("Post goods receipt")
            if go:
                sku = pos.loc[pos.po_id==po_id,"sku"].iloc[0]
                execute("INSERT INTO goods_receipts(po_id,sku,quantity) VALUES(?,?,?)",(int(po_id),sku,received))
                execute("UPDATE products SET on_hand=on_hand+? WHERE sku=?",(received,sku))
                execute("UPDATE purchase_orders SET status='Received' WHERE po_id=?",(int(po_id),))
                st.success(f"Goods receipt posted. Inventory for {sku} updated.")
                st.rerun()
    st.subheader("Goods receipt history")
    st.dataframe(query_df("SELECT * FROM goods_receipts ORDER BY grn_id DESC"), use_container_width=True)

elif page == "Sales Orders":
    st.header("Sales & Order Management")
    products = query_df("SELECT * FROM products WHERE category='Finished Good'")
    with st.form("new_so"):
        customer = st.text_input("Customer name")
        sku = st.selectbox("Finished product", products.sku)
        qty = st.number_input("Order quantity", min_value=1, value=50)
        due = st.date_input("Requested delivery date", value=date.today())
        submit = st.form_submit_button("Create sales order")
        if submit:
            if customer.strip():
                execute("INSERT INTO sales_orders(customer,sku,quantity,due_date,status) VALUES(?,?,?,?,?)",(customer.strip(),sku,int(qty),str(due),"Open"))
                st.success("Sales order created.")
                st.rerun()
            else:
                st.error("Enter a customer name.")
    orders = query_df("SELECT * FROM sales_orders ORDER BY so_id DESC")
    st.dataframe(orders, use_container_width=True)
    st.download_button("Download sales order report", orders.to_csv(index=False), "sales_orders.csv", "text/csv")

elif page == "Manufacturing Planning":
    st.header("Manufacturing Planning – BOM & MRP")
    products = query_df("SELECT * FROM products WHERE category='Finished Good'")
    sku = st.selectbox("Finished product to manufacture", products.sku, format_func=lambda x: f"{x} – {products.loc[products.sku==x,'name'].iloc[0]}")
    qty = st.number_input("Planned production quantity", min_value=1, value=100)
    bom = query_df("SELECT b.component_sku,p.name,p.uom,b.qty_per,p.on_hand,p.unit_cost FROM bom b JOIN products p ON p.sku=b.component_sku WHERE b.parent_sku=?",(sku,))
    if not bom.empty:
        bom["gross_requirement"] = bom.qty_per * qty
        bom["net_requirement"] = (bom.gross_requirement - bom.on_hand).clip(lower=0)
        bom["estimated_material_cost"] = bom.gross_requirement * bom.unit_cost
        st.subheader("Material requirements plan")
        st.dataframe(bom, use_container_width=True)
        c1,c2 = st.columns(2)
        c1.metric("Components required", len(bom))
        c2.metric("Estimated material cost", money(bom.estimated_material_cost.sum()))
        shortages = bom[bom.net_requirement>0]
        if len(shortages):
            st.warning(f"{len(shortages)} component(s) have a projected shortage. Raise purchase orders before releasing production.")
            st.dataframe(shortages[["component_sku","name","gross_requirement","on_hand","net_requirement"]], use_container_width=True)
        else:
            st.success("Available stock covers the planned material requirement.")
        st.download_button("Download MRP report", bom.to_csv(index=False), "mrp_plan.csv", "text/csv")
    else:
        st.info("No BOM components configured for this product.")

elif page == "Data Migration":
    st.header("Data Migration Workbench")
    st.write("Upload a legacy inventory CSV or Excel file. Required columns: `sku, name, category, uom, on_hand, reorder_level, unit_cost`.")
    uploaded = st.file_uploader("Upload inventory file", type=["csv","xlsx"])
    if uploaded:
        try:
            df = pd.read_csv(uploaded) if uploaded.name.endswith(".csv") else pd.read_excel(uploaded)
            st.subheader("Source preview")
            st.dataframe(df.head(20), use_container_width=True)
            required = ["sku","name","category","uom","on_hand","reorder_level","unit_cost"]
            missing = [c for c in required if c not in df.columns]
            if missing:
                st.error(f"Missing required columns: {', '.join(missing)}")
            else:
                clean = df[required].copy()
                for c in ["on_hand","reorder_level","unit_cost"]:
                    clean[c] = pd.to_numeric(clean[c], errors="coerce")
                valid_mask = clean.notna().all(axis=1) & (clean.sku.astype(str).str.strip()!="") & (clean.name.astype(str).str.strip()!="") & (clean[["on_hand","reorder_level","unit_cost"]]>=0).all(axis=1)
                valid = clean[valid_mask].drop_duplicates(subset=["sku"], keep="last")
                rejected = clean[~valid_mask]
                c1,c2,c3 = st.columns(3)
                c1.metric("Source rows", len(df))
                c2.metric("Valid rows", len(valid))
                c3.metric("Rejected rows", len(df)-len(valid))
                st.subheader("Validated records")
                st.dataframe(valid, use_container_width=True)
                if st.button("Migrate valid records into ERP database"):
                    con = connect()
                    for _,r in valid.iterrows():
                        con.execute("""INSERT INTO products(sku,name,category,uom,on_hand,reorder_level,unit_cost)
                                       VALUES(?,?,?,?,?,?,?) ON CONFLICT(sku) DO UPDATE SET
                                       name=excluded.name,category=excluded.category,uom=excluded.uom,
                                       on_hand=excluded.on_hand,reorder_level=excluded.reorder_level,unit_cost=excluded.unit_cost""",
                                    (str(r.sku),str(r["name"]),str(r.category),str(r.uom),float(r.on_hand),float(r.reorder_level),float(r.unit_cost)))
                    con.commit(); con.close()
                    execute("INSERT INTO migration_log(file_name,rows_total,rows_valid,rows_rejected,details) VALUES(?,?,?,?,?)",
                            (uploaded.name,len(df),len(valid),len(df)-len(valid),"Validated and upserted by SKU"))
                    st.success(f"Migrated {len(valid)} valid records.")
                    st.rerun()
        except Exception as e:
            st.error(f"Could not process file: {e}")
    st.subheader("Migration history")
    st.dataframe(query_df("SELECT * FROM migration_log ORDER BY log_id DESC"), use_container_width=True)

elif page == "Implementation Tracker":
    st.header("ERP Implementation Tracker")
    st.caption("A lightweight simulation of implementation governance and UAT evidence.")
    requirements = pd.DataFrame([
      ["REQ-01","Procurement","Create and track purchase orders","Configured"],
      ["REQ-02","Inventory","Post goods receipts and update stock","Configured"],
      ["REQ-03","Planning","Calculate BOM-based net material requirements","Configured"],
      ["REQ-04","Integration","Validate legacy inventory files before migration","Configured"],
      ["REQ-05","Reporting","Provide operational KPI and exception reports","Configured"],
      ["REQ-06","Security","Role-based access and audit trail","Future enhancement"]
    ],columns=["Requirement ID","Business module","Requirement","Status"])
    st.subheader("Requirements traceability matrix")
    st.dataframe(requirements, use_container_width=True)
    tests = pd.DataFrame([
      ["UAT-01","Create PO with valid supplier and SKU","Purchase order is saved","Pass"],
      ["UAT-02","Receive goods against open PO","Stock quantity increases","Pass"],
      ["UAT-03","Calculate MRP for finished product","Gross and net requirements calculated","Pass"],
      ["UAT-04","Upload file with missing mandatory field","File rejected with validation message","Pass"],
      ["UAT-05","Upload duplicate SKU records","Latest valid record retained","Pass"]
    ],columns=["Test ID","Test scenario","Expected result","Demo status"])
    st.subheader("User acceptance testing (UAT)")
    st.dataframe(tests, use_container_width=True)
    issues = pd.DataFrame([
      ["ISS-01","No role-based access control","Medium","Open","Future release"],
      ["ISS-02","Partial goods receipt handling can be expanded","Low","Open","Enhancement backlog"],
      ["ISS-03","Production order execution is simulated, not shop-floor connected","Medium","Open","Future integration"]
    ],columns=["Issue ID","Description","Priority","Status","Resolution / next step"])
    st.subheader("Issue register")
    st.dataframe(issues, use_container_width=True)
    st.subheader("Cutover readiness checklist")
    for item in ["Master data reviewed","Open purchase orders reconciled","Inventory balances validated","UAT scenarios executed","User training material prepared","Go-live support owner assigned"]:
        st.checkbox(item, key="cutover_"+item)
