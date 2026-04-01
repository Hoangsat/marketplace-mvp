export interface Category {
  id: number;
  name: string;
  slug: string;
  parent_id: number | null;
  is_featured_home: boolean;
  featured_rank: number;
}

export interface CategoryDetail extends Category {}

export interface Platform {
  id: number;
  name: string;
  slug: string;
  display_name_vi: string;
  category_id: number;
}

export interface PlatformDetail extends Platform {
  has_offer_types: boolean;
  offer_types: OfferType[];
}

export interface OfferType {
  id: number;
  name: string;
  slug: string;
  display_name_vi: string;
  platform_id: number;
}

export interface Product {
  id: number;
  title: string;
  description: string;
  price: number;
  stock: number;
  images: string[];
  seller_id: number;
  seller_nickname?: string;
  category_id: number;
  platform_id: number | null;
  offer_type_id: number | null;
  category: Category;
  platform: Platform | null;
  offer_type: OfferType | null;
}

export interface PublicSellerProfile {
  nickname: string;
  products: Product[];
}

export interface PaymentInstructions {
  bank_name: string;
  account_name: string;
  account_number: string;
  note: string;
}

export interface User {
  id: number;
  email: string;
  is_seller: boolean;
  balance_pending?: string;
  balance_available?: string;
}

export interface PayoutRequest {
  id: number;
  amount: string;
  status: string;
  created_at: string;
}

export interface OrderItem {
  id: number;
  order_id: number;
  product_id: number;
  quantity: number;
  price_at_purchase: number;
  product_title: string;
  product_image: string | null;
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
  payment_instructions?: PaymentInstructions | null;
  created_at: string;
  items: OrderItem[];
}

export interface SellerDashboardOrder {
  id: number;
  created_at: string;
  total: string;
  seller_amount: string;
  status: string;
  money_status: string;
  payout_status: string;
}

export interface SellerDashboardData {
  balance_pending: string;
  balance_available: string;
  balance_paid_out: string;
  total_earned: string;
  orders: SellerDashboardOrder[];
}

export interface SellerOrderItem {
  id: number;
  order_id: number;
  product_id: number;
  quantity: number;
  price_at_purchase: number;
  seller_amount: number;
  order_status: string;
  payout_status: string;
  product_title: string;
  product_image: string | null;
  product: Product;
}
