# Data Dictionary

| Field | Meaning |
|---|---|
| sku | Unique stock keeping unit / item code |
| category | Raw Material, Packaging or Finished Good |
| uom | Unit of measure such as kg, L, pcs or bottle |
| on_hand | Current available physical quantity in the demo |
| reorder_level | Stock threshold used to flag replenishment risk |
| unit_cost | Standard demo unit cost in INR |
| lead_time_days | Supplier's expected replenishment lead time |
| rating | Demo supplier score |
| qty_per | Component quantity needed per one finished unit |
| gross_requirement | BOM quantity multiplied by planned production quantity |
| net_requirement | Gross requirement less available stock, floored at zero |
| P2P | Procure-to-Pay business process |
| MRP | Material Requirements Planning |
| BOM | Bill of Materials |
| UAT | User Acceptance Testing |
