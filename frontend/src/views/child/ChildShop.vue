<template>
  <div class="shop-page">
    <div class="balance-bar">
      <span class="balance-label">我的积分</span>
      <span class="balance-value">
        <span class="balance-star">★</span>{{ balance }}
      </span>
    </div>

    <div v-if="loading" class="loading-state">
      <span class="loading-emoji">⏳</span>
      <p>加载中...</p>
    </div>

    <div v-else-if="products.length === 0" class="empty-state">
      <span class="empty-emoji">🏪</span>
      <p>商店暂无商品</p>
    </div>

    <div v-else class="products-grid">
      <div v-for="product in products" :key="product.id" class="product-card">
        <div class="product-image-wrap">
          <img
            v-if="product.imageUrl"
            :src="product.imageUrl"
            :alt="product.productName"
            class="product-image"
          />
          <div v-else class="product-image-placeholder">🎁</div>
        </div>
        <div class="product-info">
          <h3 class="product-name">{{ product.productName }}</h3>
          <div class="product-meta">
            <span class="product-price">
              <span class="price-star">★</span>{{ product.requiredPoints }}
            </span>
            <span class="product-stock">库存 {{ product.stock }}</span>
          </div>
        </div>
        <button
          class="redeem-btn"
          :disabled="isRedeemDisabled(product) || redeemingId === product.id"
          @click="openConfirm(product)"
        >
          <span v-if="product.isSoldOut">库存不足</span>
          <span v-else-if="balance < product.requiredPoints">积分不足</span>
          <span v-else-if="redeemingId === product.id">兑换中...</span>
          <span v-else>兑换</span>
        </button>
      </div>
    </div>

    <!-- Confirmation Modal -->
    <div v-if="confirmProduct" class="modal-overlay">
      <div class="modal-card">
        <div class="modal-icon">🛍️</div>
        <h3 class="modal-title">确认兑换</h3>
        <p class="modal-text">
          确定用 <span class="modal-points">{{ confirmProduct.requiredPoints }}</span> 积分兑换
          <span class="modal-name">{{ confirmProduct.productName }}</span>？
        </p>
        <div class="modal-actions">
          <button class="modal-btn cancel" @click="closeConfirm">取消</button>
          <button
            class="modal-btn confirm"
            :disabled="redeemingId === confirmProduct.id"
            @click="handleRedeem(confirmProduct.id)"
          >
            {{ redeemingId === confirmProduct.id ? '兑换中...' : '确认兑换' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getProducts, redeemProduct, getBalance } from '../../api/child'

const products = ref([])
const balance = ref(0)
const loading = ref(false)
const confirmProduct = ref(null)
const redeemingId = ref(null)

function isRedeemDisabled(product) {
  return product.isSoldOut || balance.value < product.requiredPoints
}

async function fetchProducts() {
  loading.value = true
  try {
    const res = await getProducts()
    products.value = res.data
  } catch (e) {
    /* interceptor shows toast */
  } finally {
    loading.value = false
  }
}

async function fetchBalance() {
  try {
    const res = await getBalance()
    balance.value = res.data.balance
  } catch (e) {
    /* interceptor shows toast */
  }
}

function openConfirm(product) {
  confirmProduct.value = product
}

function closeConfirm() {
  confirmProduct.value = null
}

async function handleRedeem(productId) {
  redeemingId.value = productId
  try {
    const res = await redeemProduct(productId)
    const data = res.data
    balance.value = data.currentBalance
    const product = products.value.find((p) => p.id === productId)
    if (product) {
      product.stock = data.stockAfter
      if (data.stockAfter === 0) {
        product.isSoldOut = true
      }
    }
    closeConfirm()
    window.dispatchEvent(new CustomEvent('balance-update'))
    window.dispatchEvent(new CustomEvent('toast', { detail: `🎉 兑换成功！获得 ${data.productName}` }))
  } catch (e) {
    /* interceptor shows toast */
  } finally {
    redeemingId.value = null
  }
}

onMounted(() => {
  fetchProducts()
  fetchBalance()
})
</script>

<style scoped>
.shop-page {
  padding: 16px;
}

.balance-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
  margin-bottom: 20px;
  border-radius: 20px;
  background: linear-gradient(135deg, #FF6B9D, #C77DFF);
  box-shadow: 0 4px 16px rgba(199, 125, 255, 0.3);
}

.balance-label {
  font-size: 16px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
}

.balance-value {
  font-size: 26px;
  font-weight: 800;
  color: #fff;
}

.balance-star {
  color: #FFD700;
  margin-right: 4px;
}

.loading-state,
.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #999;
}

.loading-emoji,
.empty-emoji {
  font-size: 48px;
  display: block;
  margin-bottom: 12px;
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 14px;
}

.product-card {
  display: flex;
  flex-direction: column;
  border-radius: 20px;
  background: #fff;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
  transition: transform 0.15s, box-shadow 0.15s;
}

.product-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}

.product-image-wrap {
  width: 100%;
  aspect-ratio: 1;
  background: linear-gradient(135deg, #FFF0F5, #F3E8FF);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.product-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.product-image-placeholder {
  font-size: 48px;
}

.product-info {
  padding: 12px 14px 8px;
  flex: 1;
}

.product-name {
  font-size: 15px;
  font-weight: 600;
  color: #333;
  margin-bottom: 6px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.product-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.product-price {
  display: flex;
  align-items: center;
  gap: 2px;
  font-size: 17px;
  font-weight: 800;
  color: #FF6B9D;
}

.price-star {
  color: #FFD700;
  font-size: 14px;
}

.product-stock {
  font-size: 12px;
  color: #aaa;
}

.redeem-btn {
  margin: 8px 14px 14px;
  padding: 10px 0;
  border-radius: 14px;
  font-size: 15px;
  font-weight: 600;
  color: #fff;
  background: linear-gradient(135deg, #FF6B9D, #C77DFF);
  box-shadow: 0 4px 12px rgba(255, 107, 157, 0.3);
  transition: transform 0.15s;
}

.redeem-btn:not(:disabled):active {
  transform: scale(0.95);
}

.redeem-btn:disabled {
  background: #e0e0e0;
  color: #999;
  box-shadow: none;
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
  padding: 20px;
}

.modal-card {
  width: 100%;
  max-width: 320px;
  background: #fff;
  border-radius: 24px;
  padding: 32px 28px 24px;
  text-align: center;
  animation: modal-pop 0.25s ease;
}

@keyframes modal-pop {
  from {
    transform: scale(0.85);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}

.modal-icon {
  font-size: 44px;
  margin-bottom: 8px;
}

.modal-title {
  font-size: 20px;
  font-weight: 700;
  color: #333;
  margin-bottom: 12px;
}

.modal-text {
  font-size: 16px;
  color: #666;
  line-height: 1.6;
  margin-bottom: 24px;
}

.modal-points {
  font-weight: 800;
  color: #FF6B9D;
}

.modal-name {
  font-weight: 700;
  color: #333;
}

.modal-actions {
  display: flex;
  gap: 12px;
}

.modal-btn {
  flex: 1;
  padding: 14px 0;
  border-radius: 16px;
  font-size: 16px;
  font-weight: 600;
  transition: transform 0.15s;
}

.modal-btn.cancel {
  background: #f0f0f0;
  color: #666;
}

.modal-btn.confirm {
  background: linear-gradient(135deg, #FF6B9D, #C77DFF);
  color: #fff;
  box-shadow: 0 4px 12px rgba(255, 107, 157, 0.3);
}

.modal-btn:not(:disabled):active {
  transform: scale(0.95);
}

.modal-btn:disabled {
  opacity: 0.6;
}

@media (min-width: 768px) {
  .products-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (min-width: 1024px) {
  .products-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}
</style>
