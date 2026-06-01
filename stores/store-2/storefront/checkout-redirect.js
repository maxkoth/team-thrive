/**
 * SaunaZen — Add-to-Cart & Checkout Redirect
 * Replace CHECKOUT_URL with your live Stripe Payment Link or Shopify checkout URL
 */

const SAUNAZEN_CONFIG = {
  checkoutUrl: 'https://checkout.stripe.com/pay/YOUR_SAUNAZEN_PAYMENT_LINK',
  currency: 'USD',
  productId: 'saunazen-signature-blanket',
  pixelId: 'YOUR_META_PIXEL_ID',
};

function addToCart(options = {}) {
  const {
    quantity = parseInt(document.getElementById('qty')?.textContent || '1', 10),
    color = document.getElementById('selected-color')?.textContent?.replace('Selected: ', '') || 'Forest Green',
  } = options;

  const total = 169 * quantity;

  if (typeof fbq !== 'undefined') {
    fbq('track', 'AddToCart', { content_ids: [SAUNAZEN_CONFIG.productId], value: total, currency: SAUNAZEN_CONFIG.currency });
  }
  if (typeof ttq !== 'undefined') {
    ttq.track('AddToCart', { value: total, currency: SAUNAZEN_CONFIG.currency });
  }

  const params = new URLSearchParams({ product: SAUNAZEN_CONFIG.productId, color, qty: quantity, total });
  const btn = document.getElementById('atc-button');

  if (btn) {
    btn.textContent = '✓ Added! Taking you to checkout...';
    btn.style.background = '#2E7D52';
    btn.disabled = true;
    setTimeout(() => { window.location.href = `${SAUNAZEN_CONFIG.checkoutUrl}?${params}`; }, 900);
  } else {
    window.location.href = `${SAUNAZEN_CONFIG.checkoutUrl}?${params}`;
  }
}

// Mobile sticky bar
document.addEventListener('DOMContentLoaded', () => {
  if (window.innerWidth > 768) return;
  const bar = document.createElement('div');
  bar.style.cssText = 'position:fixed;bottom:0;left:0;right:0;z-index:200;background:#1B3A2D;padding:0.9rem 1.25rem;display:none;align-items:center;justify-content:space-between;box-shadow:0 -4px 20px rgba(27,58,45,0.4);';
  bar.innerHTML = `<span style="color:white;font-family:'Inter',sans-serif;font-weight:700;">SaunaZen — $169</span><button onclick="addToCart()" style="background:linear-gradient(135deg,#C8A951,#AA8C3A);color:#1B3A2D;border:none;padding:0.7rem 1.5rem;border-radius:4px;font-family:'Inter',sans-serif;font-weight:700;cursor:pointer;">Add to Cart</button>`;
  document.body.appendChild(bar);
  const atcBtn = document.getElementById('atc-button');
  if (atcBtn) {
    new IntersectionObserver(([e]) => { bar.style.display = e.isIntersecting ? 'none' : 'flex'; }, { threshold: 0.1 }).observe(atcBtn);
  }
});
