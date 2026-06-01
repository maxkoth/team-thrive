# GlowLab — Order Fulfillment SOP

**Updated:** June 2026 | **Platform:** Shopify + DSers/AutoDS | **Supplier:** CJ Dropshipping

---

## DAILY FULFILLMENT ROUTINE (Target: <2 hours/day)

### Step 1 — Morning Order Review (9:00 AM)
- [ ] Log into Shopify Admin → Orders
- [ ] Filter: "Unfulfilled" + "Last 24 hours"
- [ ] Flag any orders with:
  - Mismatched billing/shipping addresses (fraud check)
  - PO Box shipping addresses (confirm supplier ships to PO Boxes)
  - International addresses not in approved shipping zones

### Step 2 — Fraud Screening
- [ ] Review Shopify's built-in fraud analysis score
- [ ] Cancel + refund any order with HIGH fraud risk before fulfilling
- [ ] For MEDIUM risk: manually verify with 1 email to customer before shipping

### Step 3 — Push Orders to DSers/AutoDS
- [ ] Open DSers → Orders → "Awaiting Order"
- [ ] Select all verified orders
- [ ] Click "Order Automatically" (confirm supplier is CJ Dropshipping)
- [ ] Verify each order shows "Ordered" status within 5 minutes
- [ ] Screenshot confirmation numbers for records

### Step 4 — Handle Exceptions
- [ ] Orders stuck in "Pending" > 2 hours → contact CJ Dropshipping support via chat
- [ ] Out-of-stock alerts → immediately pause Facebook/TikTok ads for affected variant
- [ ] Price increase alerts → pause ads + recalculate margins before resuming

### Step 5 — Tracking Import
- [ ] DSers auto-imports tracking once CJ ships (usually within 48–72 hours)
- [ ] Verify all orders from 3+ days ago have tracking numbers in Shopify
- [ ] Manually import any missing tracking: Shopify Order → Fulfill → Add Tracking

### Step 6 — Customer Communication
- [ ] Check customer support email (hello@glowlab.com)
- [ ] Respond to all emails within 4 hours (use saved reply templates in Help Desk)
- [ ] WISMO ("Where is my order?") replies: paste tracking link + expected delivery date
- [ ] Escalate damaged/missing item claims to CJ Dropshipping dispute within 7 days of delivery

---

## WEEKLY TASKS (Every Monday)

- [ ] Review refund/return requests — approve within 24 hours, never argue
- [ ] Check supplier inventory levels on CJ Dropshipping — restock alert if <100 units
- [ ] Review delivery times for last week's orders — flag if avg exceeds 14 days
- [ ] Audit negative reviews mentioning shipping — adjust ad messaging if needed
- [ ] Check for new supplier for comparison pricing (AliExpress search: "LED face mask 136 chips")

---

## MONTHLY TASKS (1st of month)

- [ ] Reconcile Shopify payouts vs. DSers/supplier invoices
- [ ] Update supplier-import-template.csv with any price changes
- [ ] Run pricing-calculator.js to verify margins are still healthy
- [ ] A/B test new product photos — request lifestyle shots from UGC creators
- [ ] Review top-converting ad sets and scale winners

---

## ESCALATION CONTACTS

| Issue | Contact | Response Time |
|-------|---------|---------------|
| Out of stock | CJ Dropshipping live chat | <1 hour |
| Tracking not updating | CJ DS dispute portal | 24 hours |
| Customer claims non-delivery | CJ dispute + Shopify dispute | 48 hours |
| Payment processing issue | Stripe Dashboard / Shopify Support | 4 hours |
| Legal/chargeback | [Your lawyer's name] | Same day |

---

## COMMON ISSUES & RESOLUTIONS

**Customer says product arrived damaged:**
1. Ask customer to send photo via email
2. Submit CJ Dropshipping dispute with photo within 7 days
3. Offer immediate free replacement or full refund (don't wait for supplier resolution)
4. CJ typically covers damaged goods — you'll be reimbursed

**Customer wants to return:**
1. Approve all returns within 24 hours — no questions
2. Provide prepaid return label (cost ~$7 — still profitable vs. churn/chargebacks)
3. Once confirmed delivered, issue refund within 24 hours
4. Note: do NOT require customers to return to China supplier — use domestic return address

**Tracking shows delivered but customer says not received:**
1. Ask customer to check with neighbors and building management first
2. If still unresolved after 3 days, reship at no charge
3. Submit CJ Dropshipping claim for lost parcel reimbursement
