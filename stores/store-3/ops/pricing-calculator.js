#!/usr/bin/env node
/**
 * LinguaFlow — Dropshipping Pricing Calculator
 *
 * Usage: node pricing-calculator.js
 *        node pricing-calculator.js --cost 12 --shipping 3.80 --ad-spend 10
 */

const LINGUAFLOW_SKUS = [
  { sku: 'LFLOW-001', name: 'LinguaFlow Pro Translation Earbuds', supplierCost: 12.00, shippingCost: 3.80, retailPrice: 59.00 },
  { sku: 'LFLOW-CASE-001', name: 'Premium Travel Case', supplierCost: 4.20, shippingCost: 2.50, retailPrice: 29.00 },
  { sku: 'LFLOW-BUNDLE-PROMO', name: 'Earbuds + Free Case Bundle', supplierCost: 16.20, shippingCost: 4.20, retailPrice: 59.00 },
  { sku: 'LFLOW-2PACK', name: 'Family 2-Pack (Bidirectional)', supplierCost: 24.00, shippingCost: 5.50, retailPrice: 99.00 },
];

const COSTS = {
  transactionFeePercent: 2.9,
  transactionFeeFixed: 0.30,
  returnRate: 0.05,
  packagingCost: 0.60,
};

function calc(sku, adSpendPerUnit = 10) {
  const cogs = sku.supplierCost + sku.shippingCost + COSTS.packagingCost;
  const txFee = (sku.retailPrice * COSTS.transactionFeePercent / 100) + COSTS.transactionFeeFixed;
  const returnCost = sku.retailPrice * COSTS.returnRate;
  const grossProfit = sku.retailPrice - cogs;
  const netProfit = sku.retailPrice - cogs - txFee - returnCost - adSpendPerUnit;
  const breakEvenRoas = sku.retailPrice / (sku.retailPrice - cogs - txFee - returnCost);

  return {
    ...sku,
    cogs: cogs.toFixed(2),
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

const adSpend = parseFloat(process.argv[process.argv.indexOf('--ad-spend') + 1] || '10');

console.log('\n╔══════════════════════════════════════════════════╗');
console.log('║      LINGUAFLOW PRICING CALCULATOR — 2026        ║');
console.log('╚══════════════════════════════════════════════════╝\n');

LINGUAFLOW_SKUS.forEach(sku => {
  const r = calc(sku, adSpend);
  console.log(`┌─ ${r.name} (${r.sku})`);
  console.log(`│  Supplier: $${r.supplierCost} + Ship: $${r.shippingCost} = COGS: $${r.cogs}`);
  console.log(`│  Retail: $${r.retailPrice} | Markup: ${r.markup}`);
  console.log(`│  Gross: $${r.grossProfit} (${r.grossMargin})`);
  console.log(`│  Net (after $${adSpend} ads): $${r.netProfit} (${r.netMargin})`);
  console.log(`│  Break-even ROAS: ${r.breakEvenRoas}x`);
  console.log(`│  Suggested 4x: $${r.suggested4x} | 5x: $${r.suggested5x}`);
  console.log('└──────────────────────────────────────────────\n');
});

console.log(`Assumptions: ad spend/unit: $${adSpend} | returns: ${COSTS.returnRate*100}% | tx: ${COSTS.transactionFeePercent}%+$${COSTS.transactionFeeFixed}`);
console.log('\n💡 LinguaFlow has the highest gross margin of all 3 stores (~71%) due to low COGS.');
console.log('   Excellent unit economics for scaling paid ads aggressively.\n');
