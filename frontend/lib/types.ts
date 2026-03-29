// lib/types.ts
// Shared TypeScript types matching the FastAPI backend schemas.

export interface Category {
  id: number;
  name: string;
}

export interface Product {
  id: number;
  title: string;
  description: string;
  price: number;
  stock: number;
  images: string[];
  seller_id: number;
  category_id: number;
  category: Category;
}

export interface User {
  id: number;
  email: string;
  is_seller: boolean;
}

export interface OrderItem {
  id: number;
  order_id: number;
  product_id: number;
  quantity: number;
  price_at_purchase: number;
  product: Product;
}

export interface Order {
  id: number;
  buyer_id: number;
  total: number;
  status: string;
  payment_method?: string | null;
  payment_provider?: string | null;
  payment_reference?: string | null;
  payment_confirmed_at?: string | null;
  buyer_marked_paid_at?: string | null;
  created_at: string;
  items: OrderItem[];
}
