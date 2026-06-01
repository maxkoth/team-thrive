/**
 * LinguaFlow — Add-to-Cart & Checkout Redirect
 * Replace CHECKOUT_URL with live Stripe Payment Link or Shopify checkout URL
 */

const LINGUAFLOW_CONFIG = {
  checkoutUrl: 'https://checkout.stripe.com/pay/YOUR_LINGUAFLOW_PAYMENT_LINK',
  currency: 'USD',
  productId: 'linguaflow-pro-earbuds',
};

function addToCart(options = {}) {
  const {
    quantity = parseInt(document.getElementById('qty')?.textContent || '1', 10),
    color = document.querySelector('.variant-btn.selected')?.textContent || 'Midnight Black',
  } = options;

  const total = 59 * quantity;

  if (typeof fbq !== 'undefined') fbq('track', 'AddToCart', { content_ids: [LINGUAFLOW_CONFIG.productId], value: total, currency: 'USD' });
  if (typeof ttq !== 'undefined') ttq.track('AddToCart', { value: total, currency: 'USD' });

  const params = new URLSearchParams({ product: LINGUAFLOW_CONFIG.productId, color, qty: quantity, total });
  const btn = document.getElementById('atc-button');

  if (btn) {
    btn.textContent = '✓ Added! Heading to checkout...';
    btn.style.background = 'linear-gradient(135deg, #00C17A, #009960)';
    btn.disabled = true;
    setTimeout(() => { window.location.href = `${LINGUAFLOW_CONFIG.checkoutUrl}?${params}`; }, 900);
  } else {
    window.location.href = `${LINGUAFLOW_CONFIG.checkoutUrl}?${params}`;
  }
}

document.addEventListener('DOMContentLoaded', () => {
  if (window.innerWidth > 768) return;
  const bar = document.createElement('div');
  bar.style.cssText = 'position:fixed;bottom:0;left:0;right:0;z-index:200;background:#050F2E;padding:0.9rem 1.25rem;display:none;align-items:center;justify-content:space-between;box-shadow:0 -4px 20px rgba(0,87,255,0.4);';
  bar.innerHTML = `<span style="color:white;font-weight:700;font-family:DM Sans,sans-serif;">LinguaFlow — $59</span><button onclick="addToCart()" style="background:linear-gradient(135deg,#0057FF,#00D4FF);color:white;border:none;padding:0.7rem 1.5rem;border-radius:8px;font-weight:700;cursor:pointer;">Add to Cart →</button>`;
  document.body.appendChild(bar);
  const atcBtn = document.getElementById('atc-button');
  if (atcBtn) new IntersectionObserver(([e]) => { bar.style.display = e.isIntersecting ? 'none' : 'flex'; }, { threshold: 0.1 }).observe(atcBtn);
});
