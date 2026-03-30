export type Language = "vi" | "en";

export const DEFAULT_LANGUAGE: Language = "vi";
export const LANGUAGE_STORAGE_KEY = "marketpy_language";

export interface TranslationMessages {
  home: string;
  catalog: string;
  orders: string;
  seller: string;
  login: string;
  register: string;
  logout: string;
  cart: string;
  browseProducts: string;
  searchProducts: string;
  allCategories: string;
  minPrice: string;
  maxPrice: string;
  loadingProducts: string;
  noProducts: string;
  chooseGame: string;
  loadingGames: string;
  loadCatalogError: string;
  noGames: string;
  backToCatalog: string;
  chooseOfferType: string;
  loadingOfferTypes: string;
  noOfferTypes: string;
  gameNotFound: string;
  offerTypeNotFound: string;
  backToOfferTypes: string;
  browseProductsForSelection: string;
  loadProductsError: string;
  email: string;
  password: string;
  confirmPassword: string;
  createAccount: string;
  createAccountTitle: string;
  creatingAccount: string;
  loginTitle: string;
  loggingIn: string;
  dontHaveAccount: string;
  alreadyHaveAccount: string;
  passwordsDoNotMatch: string;
  accountCreated: string;
  registrationFailed: string;
  loggedIn: string;
  loginFailed: string;
  outOfStock: string;
  inStock: (count: number) => string;
}

export const translations: Record<Language, TranslationMessages> = {
  vi: {
    home: "Trang chủ",
    catalog: "Danh mục",
    orders: "Đơn hàng",
    seller: "Người bán",
    login: "Đăng nhập",
    register: "Đăng ký",
    logout: "Đăng xuất",
    cart: "Giỏ hàng",
    browseProducts: "Duyệt sản phẩm",
    searchProducts: "Tìm sản phẩm...",
    allCategories: "Tất cả danh mục",
    minPrice: "Giá từ",
    maxPrice: "Giá đến",
    loadingProducts: "Đang tải sản phẩm...",
    noProducts: "Không tìm thấy sản phẩm.",
    chooseGame: "Chọn một trò chơi để tiếp tục.",
    loadingGames: "Đang tải trò chơi...",
    loadCatalogError: "Không thể tải danh mục.",
    noGames: "Không có trò chơi nào.",
    backToCatalog: "Quay lại danh mục",
    chooseOfferType: "Chọn một loại dịch vụ.",
    loadingOfferTypes: "Đang tải loại dịch vụ...",
    noOfferTypes: "Không có loại dịch vụ nào.",
    gameNotFound: "Không tìm thấy trò chơi.",
    offerTypeNotFound: "Không tìm thấy loại dịch vụ.",
    backToOfferTypes: "Quay lại loại dịch vụ",
    browseProductsForSelection: "Xem sản phẩm cho lựa chọn này.",
    loadProductsError: "Không thể tải sản phẩm.",
    email: "Email",
    password: "Mật khẩu",
    confirmPassword: "Xác nhận mật khẩu",
    createAccount: "Tạo tài khoản",
    createAccountTitle: "Tạo tài khoản",
    creatingAccount: "Đang tạo tài khoản...",
    loginTitle: "Đăng nhập",
    loggingIn: "Đang đăng nhập...",
    dontHaveAccount: "Chưa có tài khoản?",
    alreadyHaveAccount: "Đã có tài khoản?",
    passwordsDoNotMatch: "Mật khẩu không khớp",
    accountCreated: "Tạo tài khoản thành công! Vui lòng đăng nhập.",
    registrationFailed: "Đăng ký thất bại",
    loggedIn: "Đăng nhập thành công!",
    loginFailed: "Đăng nhập thất bại",
    outOfStock: "Hết hàng",
    inStock: (count) => `${count} còn hàng`,
  },
  en: {
    home: "Home",
    catalog: "Catalog",
    orders: "Orders",
    seller: "Seller",
    login: "Login",
    register: "Register",
    logout: "Logout",
    cart: "Cart",
    browseProducts: "Browse Products",
    searchProducts: "Search products...",
    allCategories: "All Categories",
    minPrice: "Min $",
    maxPrice: "Max $",
    loadingProducts: "Loading products...",
    noProducts: "No products found.",
    chooseGame: "Choose a game to continue.",
    loadingGames: "Loading games...",
    loadCatalogError: "Unable to load catalog.",
    noGames: "No games available.",
    backToCatalog: "Back to catalog",
    chooseOfferType: "Choose an offer type.",
    loadingOfferTypes: "Loading offer types...",
    noOfferTypes: "No offer types available.",
    gameNotFound: "Game not found.",
    offerTypeNotFound: "Offer type not found.",
    backToOfferTypes: "Back to offer types",
    browseProductsForSelection: "Browse products for this catalog selection.",
    loadProductsError: "Unable to load products.",
    email: "Email",
    password: "Password",
    confirmPassword: "Confirm Password",
    createAccount: "Create Account",
    createAccountTitle: "Create Account",
    creatingAccount: "Creating account...",
    loginTitle: "Login",
    loggingIn: "Logging in...",
    dontHaveAccount: "Don't have an account?",
    alreadyHaveAccount: "Already have an account?",
    passwordsDoNotMatch: "Passwords do not match",
    accountCreated: "Account created! Please log in.",
    registrationFailed: "Registration failed",
    loggedIn: "Logged in!",
    loginFailed: "Login failed",
    outOfStock: "Out of stock",
    inStock: (count) => `${count} in stock`,
  },
};

export function isLanguage(value: string | null): value is Language {
  return value === "vi" || value === "en";
}
