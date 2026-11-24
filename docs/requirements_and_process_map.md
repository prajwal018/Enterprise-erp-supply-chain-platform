# Requirements and Process Map

## Scope
A teaching/demo ERP implementation for a small manufacturing organization.

## Business processes
### Procure-to-Pay (P2P)
Supplier selection → Purchase order → Goods receipt → Inventory update → (invoice matching is a future enhancement).

### Plan-to-Produce
Sales demand / production plan → BOM explosion → gross material requirement → on-hand stock offset → net requirement / shortage identification.

### Order Management
Customer order capture → order register → due-date and status visibility.

## Core data entities
- Supplier: supplier master, lead time, rating, contact.
- Product: SKU master, category, unit of measure, stock, reorder level and unit cost.
- Purchase Order: supplier, SKU, quantity, price and status.
- Goods Receipt: PO reference, received SKU and quantity.
- Sales Order: customer, finished SKU, quantity, due date and status.
- BOM: parent finished good, component SKU and quantity per finished unit.

## Assumptions
- Demo currency is INR.
- Data is synthetic and intended for demonstration.
- One PO is closed on its first goods receipt in this version.
- MRP calculates material needs for a single planned batch and does not yet model safety stock, scheduled receipts or lead-time offsets.
