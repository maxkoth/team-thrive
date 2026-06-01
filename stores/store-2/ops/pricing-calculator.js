#!/usr/bin/env node
/**
 * SaunaZen — Dropshipping Pricing Calculator
 *
 * Usage: node pricing-calculator.js
 *        node pricing-calculator.js --cost 45 --shipping 8.50 --ad-spend 22
 */

const SAUNAZEN_SKUS = [
  { sku: 'SZEN-BLK-001', name: 'SaunaZen Infrared Blanket', supplierCost: 45.00, shippingCost: 8.50, retailPrice: 169.00 },
  { sku: 'SZEN-BAG-001', name: 'Premium Carry Bag', supplierCost: 8.50, shippingCost: 3.00, retailPrice: 49.00 },
  { sku: 'SZEN-BUNDLE-PROMO', name: 'Blanket + Free Carry Bag Bundle', supplierCost: 53.50, shippingCost: 9.00, retailPrice: 169.00 },
];

const COSTS = {
  transactionFeePercent: 2.9,
  transactionFeeFixed: 0.30,
  returnRate: 0.04,
  packagingCost: 1.20,
};

function calc(sku, { adSpendPerUnit = 22 } = {}) {
  const cogs = sku.supplierCost + sku.shippingCost + COSTS.packagingCost;
  const txFee = (sku.retailPrice * COSTS.transactionFeePercent / 100) + COSTS.transactionFeeFixed;
  const returnCost = sku.retailPrice * COSTS.returnRate;
  const grossProfit = sku.retailPrice - cogs;
  const netProfit = sku.retailPrice - cogs - txFee - returnCost - adSpendPerUnit;
  const breakEvenRoas = sku.retailPrice / (sku.retailPrice - cogs - txFee - returnCost);

  return {
    ...sku,
    cogs: cogs.toFixed(2),
    txFee: txFee.toFixed(2),
    grossProfit: grossProfit.toFixed(2),
    netProfit: netProfit.toFixed(2),
    grossMargin: ((grossProfit / sku.retailPrice) * 100).toFixed(1) + '%',
    netMargin: ((netProfit / sku.retailPrice) * 100).toFixed(1) + '%',
    markup: (sku.retailPrice / sku.supplierCost).toFixed(1) + 'x',
    breakEvenRoas: breakEvenRoas.toFixed(2),
    suggested4x: Math.ceil((sku.supplierCost + sku.shippingCost) * 4 / 5) * 5,
    suggested5x: Math.ceil((sku.supplierCost + sku.shippingCost) * 5 / 5) * 5,
  };
}

const getArg = (flag) => { const i = process.argv.indexOf(flag); return i !== -1 ? parseFloat(process.argv[i + 1]) : null; };
const customAdSpend = getArg('--ad-spend') || 22;

console.log('\n╔══════════════════════════════════════════════════╗');
console.log('║       SAUNAZEN PRICING CALCULATOR — 2026         ║');
console.log('╚══════════════════════════════════════════════════╝\n');

SAUNAZEN_SKUS.forEach(sku => {
  const r = calc(sku, { adSpendPerUnit: customAdSpend });
  console.log(`┌─ ${r.name} (${r.sku})`);
  console.log(`│  Supplier:  $${r.supplierCost} + Shipping: $${r.shippingCost} = COGS: $${r.cogs}`);
  console.log(`│  Retail:    $${r.retailPrice} | Markup: ${r.markup}`);
  console.log(`│  Gross:     $${r.grossProfit} (${r.grossMargin} gross margin)`);
  console.log(`│  Net:       $${r.netProfit} (${r.netMargin} net, after $${customAdSpend} ad spend)`);
  console.log(`│  Break-even ROAS: ${r.breakEvenRoas}x`);
  console.log(`│  Suggested 4x: $${r.suggested4x} | 5x: $${r.suggested5x}`);
  console.log('└──────────────────────────────────────────────\n');
});

console.log(`Assumptions: ad spend/unit: $${customAdSpend} | returns: ${COSTS.returnRate * 100}% | tx fee: ${COSTS.transactionFeePercent}% + $${COSTS.transactionFeeFixed}`);
