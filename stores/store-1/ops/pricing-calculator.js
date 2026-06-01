#!/usr/bin/env node
/**
 * GlowLab — Dropshipping Pricing Calculator
 * Calculates retail price, profit margin, and break-even ROAS
 * for all GlowLab SKUs.
 *
 * Usage: node pricing-calculator.js
 *        node pricing-calculator.js --cost 18 --shipping 4.50 --target-margin 70
 */

const GLOWLAB_SKUS = [
  { sku: 'GLAB-LED-001', name: 'GlowLab Pro LED Mask', supplierCost: 18.00, shippingCost: 4.50, retailPrice: 97.00 },
  { sku: 'GLAB-SER-001', name: 'GlowLab Radiance Serum', supplierCost: 5.20, shippingCost: 2.80, retailPrice: 36.00 },
  { sku: 'GLAB-BUNDLE-001', name: 'Mask + Serum Bundle', supplierCost: 23.20, shippingCost: 5.00, retailPrice: 115.00 },
];

const FIXED_COSTS = {
  shopifyMonthly: 39,       // Shopify Basic plan
  transactionFeePercent: 2.9, // Stripe/Shopify Payments
  transactionFeeFixed: 0.30,  // Per transaction
  returnRate: 0.05,           // 5% return assumption
  packagingCost: 0.80,        // Branded packaging inserts
};

function calculateSKU(sku, params = {}) {
  const {
    supplierCost = sku.supplierCost,
    shippingCost = sku.shippingCost,
    retailPrice = sku.retailPrice,
    adSpendPerUnit = 15,
  } = params;

  const totalCogs = supplierCost + shippingCost + FIXED_COSTS.packagingCost;
  const transactionFee = (retailPrice * FIXED_COSTS.transactionFeePercent / 100) + FIXED_COSTS.transactionFeeFixed;
  const returnCostPerUnit = retailPrice * FIXED_COSTS.returnRate;

  const grossProfit = retailPrice - totalCogs;
  const netProfitWithAds = retailPrice - totalCogs - transactionFee - returnCostPerUnit - adSpendPerUnit;
  const grossMarginPercent = (grossProfit / retailPrice) * 100;
  const netMarginPercent = (netProfitWithAds / retailPrice) * 100;
  const markupMultiplier = retailPrice / supplierCost;

  // Break-even ROAS = Revenue / Ad Spend needed to cover all non-ad costs
  const nonAdCostPerUnit = totalCogs + transactionFee + returnCostPerUnit;
  const breakEvenRoas = retailPrice / (retailPrice - nonAdCostPerUnit);

  // Suggested price at target 4x markup
  const suggestedPrice4x = Math.ceil((supplierCost + shippingCost) * 4 / 5) * 5;
  const suggestedPrice5x = Math.ceil((supplierCost + shippingCost) * 5 / 5) * 5;

  return {
    sku: sku.sku,
    name: sku.name,
    supplierCost: supplierCost.toFixed(2),
    shippingCost: shippingCost.toFixed(2),
    totalCogs: totalCogs.toFixed(2),
    retailPrice: retailPrice.toFixed(2),
    grossProfit: grossProfit.toFixed(2),
    netProfitWithAds: netProfitWithAds.toFixed(2),
    grossMarginPercent: grossMarginPercent.toFixed(1) + '%',
    netMarginPercent: netMarginPercent.toFixed(1) + '%',
    markupMultiplier: markupMultiplier.toFixed(1) + 'x',
    breakEvenRoas: breakEvenRoas.toFixed(2),
    suggestedPrice4x,
    suggestedPrice5x,
  };
}

function printTable(results) {
  console.log('\n╔══════════════════════════════════════════════════════════════════╗');
  console.log('║             GLOWLAB PRICING CALCULATOR — 2026                    ║');
  console.log('╚══════════════════════════════════════════════════════════════════╝\n');

  results.forEach(r => {
    console.log(`┌─ ${r.name} (${r.sku})`);
    console.log(`│  Supplier Cost:     $${r.supplierCost}`);
    console.log(`│  Shipping Cost:     $${r.shippingCost}`);
    console.log(`│  Total COGS:        $${r.totalCogs}`);
    console.log(`│  Retail Price:      $${r.retailPrice}`);
    console.log(`│  Markup:            ${r.markupMultiplier}`);
    console.log(`│  ─────────────────────────`);
    console.log(`│  Gross Profit:      $${r.grossProfit} (${r.grossMarginPercent} gross margin)`);
    console.log(`│  Net Profit (w/ads):$${r.netProfitWithAds} (${r.netMarginPercent} net margin)`);
    console.log(`│  Break-even ROAS:   ${r.breakEvenRoas}x`);
    console.log(`│  Suggested 4x:      $${r.suggestedPrice4x}`);
    console.log(`│  Suggested 5x:      $${r.suggestedPrice5x}`);
    console.log('└─────────────────────────────────────────────────\n');
  });

  console.log('ASSUMPTIONS:');
  console.log(`  Ad spend/unit: $15 (adjust with --ad-spend flag)`);
  console.log(`  Return rate: ${FIXED_COSTS.returnRate * 100}%`);
  console.log(`  Transaction fee: ${FIXED_COSTS.transactionFeePercent}% + $${FIXED_COSTS.transactionFeeFixed}`);
  console.log(`  Packaging: $${FIXED_COSTS.packagingCost}/unit\n`);
}

// CLI overrides
const args = process.argv.slice(2);
const getArg = (flag) => {
  const i = args.indexOf(flag);
  return i !== -1 ? parseFloat(args[i + 1]) : null;
};

const customCost = getArg('--cost');
const customShipping = getArg('--shipping');
const customRetail = getArg('--retail');
const customAdSpend = getArg('--ad-spend');

const results = GLOWLAB_SKUS.map(sku => calculateSKU(sku, {
  supplierCost: customCost || sku.supplierCost,
  shippingCost: customShipping || sku.shippingCost,
  retailPrice: customRetail || sku.retailPrice,
  adSpendPerUnit: customAdSpend || 15,
}));

printTable(results);
