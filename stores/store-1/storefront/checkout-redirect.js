/**
 * GlowLab — Add-to-Cart & Checkout Redirect
 * Replace CHECKOUT_URL with your live Stripe Payment Link or Shopify checkout URL
 */

const GLOWLAB_CONFIG = {
  checkoutUrl: 'https://checkout.stripe.com/pay/YOUR_GLOWLAB_PAYMENT_LINK',
  shopifyCheckoutUrl: 'https://glowlab-store.myshopify.com/cart',
  currency: 'USD',
  productId: 'glowlab-pro-led-mask',
  pixelId: 'YOUR_META_PIXEL_ID',
};

function addToCart(options = {}) {
  const {
    quantity = parseInt(document.getElementById('qty')?.textContent || '1', 10),
    hasBundle = document.getElementById('bundle-check')?.checked || false,
    variant = document.querySelector('.variant-btn.selected')?.textContent || 'Pearl White',
  } = options;

  const lineItems = [
    { id: 'glowlab-pro-led-mask', qty: quantity, price: 97, name: 'GlowLab Pro LED Mask' },
  ];
  if (hasBundle) {
    lineItems.push({ id: 'glowlab-radiance-serum', qty: quantity, price: 18, name: 'GlowLab Radiance Serum' });
  }

  const total = lineItems.reduce((sum, item) => sum + item.price * item.qty, 0);

  // Fire Meta/Facebook pixel event
  if (typeof fbq !== 'undefined') {
    fbq('track', 'AddToCart', {
      content_ids: lineItems.map(i => i.id),
      content_type: 'product',
      value: total,
      currency: GLOWLAB_CONFIG.currency,
    });
  }

  // Fire TikTok pixel event
  if (typeof ttq !== 'undefined') {
    ttq.track('AddToCart', {
      value: total,
      currency: GLOWLAB_CONFIG.currency,
    });
  }

  // Build cart parameters
  const params = new URLSearchParams({
    product: GLOWLAB_CONFIG.productId,
    variant: variant,
    qty: quantity,
    bundle: hasBundle ? '1' : '0',
    total: total,
  });

  // Animate button before redirect
  const btn = document.getElementById('atc-button');
  if (btn) {
    const original = btn.textContent;
    btn.textContent = '✓ Added! Redirecting to checkout...';
    btn.style.background = 'linear-gradient(135deg, #27AE60, #1e8449)';
    btn.disabled = true;

    setTimeout(() => {
      window.location.href = `${GLOWLAB_CONFIG.checkoutUrl}?${params.toString()}`;
    }, 900);
  } else {
    window.location.href = `${GLOWLAB_CONFIG.checkoutUrl}?${params.toString()}`;
  }
}

// Sticky ATC bar on mobile scroll
function initStickyBar() {
  if (window.innerWidth > 768) return;
  const bar = document.createElement('div');
  bar.style.cssText = `
    position: fixed; bottom: 0; left: 0; right: 0; z-index: 200;
    background: #2D1B69; padding: 0.9rem 1.25rem;
    display: none; align-items: center; justify-content: space-between;
    box-shadow: 0 -4px 20px rgba(45,27,105,0.3);
  `;
  bar.innerHTML = `
    <span style="color:white;font-weight:700;font-size:1rem;">GlowLab Pro — $97</span>
    <button onclick="addToCart()" style="background:linear-gradient(135deg,#C9956C,#B8845A);color:white;border:none;padding:0.7rem 1.5rem;border-radius:50px;font-weight:700;font-size:0.95rem;cursor:pointer;">Add to Cart →</button>
  `;
  document.body.appendChild(bar);

  const observer = new IntersectionObserver(([entry]) => {
    bar.style.display = entry.isIntersecting ? 'none' : 'flex';
  }, { threshold: 0.1 });

  const atcBtn = document.getElementById('atc-button');
  if (atcBtn) observer.observe(atcBtn);
}

document.addEventListener('DOMContentLoaded', initStickyBar);
