from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from db import init_db, query_df, execute

app = FastAPI(title="Enterprise ERP Integration API", version="1.0.0",
              description="Demo REST API for products, suppliers, purchase orders and inventory.")
init_db()

class PurchaseOrderIn(BaseModel):
    supplier_id: int = Field(gt=0)
    sku: str
    quantity: float = Field(gt=0)
    unit_price: float = Field(ge=0)

class GoodsReceiptIn(BaseModel):
    quantity: float = Field(gt=0)

@app.get("/health")
def health():
    return {"status":"ok","service":"enterprise-erp-demo"}

@app.get("/products")
def products():
    return query_df("SELECT * FROM products").to_dict(orient="records")

@app.get("/suppliers")
def suppliers():
    return query_df("SELECT * FROM suppliers WHERE active=1").to_dict(orient="records")

@app.get("/purchase-orders")
def purchase_orders():
    return query_df("SELECT * FROM purchase_orders ORDER BY po_id DESC").to_dict(orient="records")

@app.post("/purchase-orders", status_code=201)
def create_purchase_order(payload: PurchaseOrderIn):
    supplier = query_df("SELECT supplier_id FROM suppliers WHERE supplier_id=? AND active=1",(payload.supplier_id,))
    product = query_df("SELECT sku FROM products WHERE sku=?",(payload.sku,))
    if supplier.empty:
        raise HTTPException(404,"Active supplier not found")
    if product.empty:
        raise HTTPException(404,"SKU not found")
    po_id = execute("INSERT INTO purchase_orders(supplier_id,sku,quantity,unit_price,status) VALUES(?,?,?,?,?)",
                    (payload.supplier_id,payload.sku,payload.quantity,payload.unit_price,"Open"))
    return {"po_id":po_id,"status":"Open"}

@app.post("/purchase-orders/{po_id}/receive")
def receive_purchase_order(po_id: int, payload: GoodsReceiptIn):
    po = query_df("SELECT * FROM purchase_orders WHERE po_id=? AND status='Open'",(po_id,))
    if po.empty:
        raise HTTPException(404,"Open purchase order not found")
    if payload.quantity > float(po.iloc[0].quantity):
        raise HTTPException(400,"Receipt quantity cannot exceed the open PO quantity in this demo")
    execute("INSERT INTO goods_receipts(po_id,sku,quantity) VALUES(?,?,?)",(po_id,po.iloc[0].sku,payload.quantity))
    execute("UPDATE products SET on_hand=on_hand+? WHERE sku=?",(payload.quantity,po.iloc[0].sku))
    execute("UPDATE purchase_orders SET status='Received' WHERE po_id=?",(po_id,))
    return {"po_id":po_id,"sku":po.iloc[0].sku,"received_quantity":payload.quantity,"inventory_updated":True}
