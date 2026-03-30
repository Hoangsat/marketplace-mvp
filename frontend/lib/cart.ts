// lib/cart.ts
// Cart stored in localStorage as an array of CartItem.

export interface CartItem {
  product_id: number;
  title: string;
  price: number;
  quantity: number;
  image: string | null;
  seller_id?: number;
}

const KEY = "cart";

export function getCart(): CartItem[] {
  if (typeof window === "undefined") return [];
  try {
    return JSON.parse(localStorage.getItem(KEY) ?? "[]");
  } catch {
    return [];
  }
}

function saveCart(cart: CartItem[]): void {
  localStorage.setItem(KEY, JSON.stringify(cart));
}

export function addToCart(item: Omit<CartItem, "quantity">, qty = 1): void {
  const cart = getCart();
  const existing = cart.find((c) => c.product_id === item.product_id);
  if (existing) {
    existing.quantity += qty;
  } else {
    cart.push({ ...item, quantity: qty });
  }
  saveCart(cart);
}

export function updateQuantity(product_id: number, quantity: number): void {
  const cart = getCart().map((c) =>
    c.product_id === product_id ? { ...c, quantity } : c
  );
  saveCart(cart);
}

export function removeFromCart(product_id: number): void {
  saveCart(getCart().filter((c) => c.product_id !== product_id));
}

export function clearCart(): void {
  localStorage.removeItem(KEY);
}

export function cartTotal(cart: CartItem[]): number {
  return cart.reduce((sum, c) => sum + c.price * c.quantity, 0);
}

export function hasMultipleCartSellers(cart: CartItem[]): boolean {
  const sellerIds = new Set(
    cart
      .map((item) => item.seller_id)
      .filter((sellerId): sellerId is number => typeof sellerId === "number")
  );
  return sellerIds.size > 1;
}
