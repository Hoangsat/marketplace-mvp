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
  browseProductsLink: string;
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
  nickname: string;
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
  nicknameRequired: string;
  nicknameLengthError: string;
  nicknameInvalidError: string;
  accountCreated: string;
  registrationFailed: string;
  loggedIn: string;
  loginFailed: string;
  cartTitle: string;
  cartEmpty: string;
  remove: string;
  total: string;
  checkout: string;
  each: string;
  pleaseLoginToCheckout: string;
  cartIsEmpty: string;
  nothingToCheckout: string;
  singleSellerCheckoutMessage: string;
  orderPlacedContinuePayment: string;
  checkoutFailed: string;
  manualBankTransferRedirect: string;
  processing: string;
  continueToPayment: string;
  myOrders: string;
  loadingOrders: string;
  noOrdersYet: string;
  completePayment: string;
  paymentEvaluating: string;
  markAsCompleted: string;
  unableToUpdateOrder: string;
  orderPrefix: string;
  productFallback: string;
  loadingPaymentDetails: string;
  orderNotFound: string;
  completePaymentTitle: string;
  bankTransferInstructions: string;
  transferExactAmount: string;
  toFollowingBankAccount: string;
  bankLabel: string;
  accountNameLabel: string;
  accountNumberLabel: string;
  memoLabel: string;
  paymentInstructionsUnavailable: string;
  exactMemoWarning: string;
  paymentSubmitted: string;
  failedToLoadOrder: string;
  failedToSubmit: string;
  paymentConfirmedPreparingOrder: string;
  viewMyOrders: string;
  markedPaidOn: string;
  awaitingManualConfirmation: string;
  returnToOrders: string;
  submitting: string;
  iHavePaid: string;
  loading: string;
  sellerDashboardTitle: string;
  pendingBalanceOnHold: string;
  availableBalance: string;
  payoutRequestTitle: string;
  payoutAmountLabel: string;
  payoutAmountPlaceholder: string;
  requestPayout: string;
  payoutRequestSubmitted: string;
  payoutAmountRequired: string;
  payoutAmountMustBePositive: string;
  payoutRequestFailed: string;
  paidOutBalance: string;
  totalEarnings: string;
  noSellerOrders: string;
  orderStatusLabel: string;
  moneyStatusLabel: string;
  payoutStatusLabel: string;
  sellerAmountLabel: string;
  markAsDelivered: string;
  orderMarkedDelivered: string;
  unableToLoadSellerDashboard: string;
  unableToUpdateOrderStatus: string;
  myProducts: string;
  newProduct: string;
  noSellerProducts: string;
  edit: string;
  delete: string;
  deleteProductConfirm: string;
  productDeleted: string;
  deleteFailed: string;
  viewOrderItems: string;
  salesOrderItems: string;
  quantityShort: string;
  sellerProfileNotFound: string;
  loadSellerProfileError: string;
  productNotFound: string;
  back: string;
  categoryLabel: string;
  platformsLabel: string;
  offerTypesLabel: string;
  productsLabel: string;
  selectedCategoryLabel: string;
  selectedGameLabel: string;
  selectedOfferTypeLabel: string;
  catalogContextPrefilled: string;
  categoryStillRequired: string;
  gamesCategoryName: string;
  categoryAutoAssigned: string;
  categoryFallbackManual: string;
  stockLabel: string;
  quantity: string;
  addToCart: string;
  addedToCart: string;
  createProductTitle: string;
  editProductTitle: string;
  titleLabel: string;
  descriptionLabel: string;
  priceLabel: string;
  stockFieldLabel: string;
  selectCategory: string;
  imagesLabel: string;
  replaceImagesLabel: string;
  replaceImagesHelp: string;
  creating: string;
  saving: string;
  saveChanges: string;
  sellInThisCategory: string;
  cancel: string;
  productCreated: string;
  productUpdated: string;
  createProductFailed: string;
  updateFailed: string;
  noPlatformsAvailableYet: string;
  noOfferTypesAvailableYet: string;
  noProductsFoundYet: string;
  statusPending: string;
  statusPaid: string;
  statusDelivered: string;
  statusCompleted: string;
  statusCancelled: string;
  statusOnHold: string;
  statusAvailable: string;
  statusPaidOut: string;
  statusPendingPayment: string;
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
    browseProductsLink: "Duyệt sản phẩm",
    searchProducts: "Tìm sản phẩm...",
    allCategories: "Tất cả danh mục",
    minPrice: "Giá từ",
    maxPrice: "Giá đến",
    loadingProducts: "Đang tải sản phẩm...",
    noProducts: "Không tìm thấy sản phẩm.",
    chooseGame: "Chọn một danh mục hoặc nền tảng để tiếp tục.",
    loadingGames: "Đang tải danh mục...",
    loadCatalogError: "Không thể tải danh mục.",
    noGames: "Không có danh mục hoặc nền tảng nào.",
    backToCatalog: "Quay lại danh mục",
    chooseOfferType: "Chọn một loại dịch vụ.",
    loadingOfferTypes: "Đang tải loại dịch vụ...",
    noOfferTypes: "Không có loại dịch vụ nào.",
    gameNotFound: "Không tìm thấy nền tảng.",
    offerTypeNotFound: "Không tìm thấy loại dịch vụ.",
    backToOfferTypes: "Quay lại nền tảng",
    browseProductsForSelection: "Xem sản phẩm cho nền tảng và loại dịch vụ này.",
    loadProductsError: "Không thể tải sản phẩm.",
    email: "Email",
    nickname: "Biệt danh",
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
    nicknameRequired: "Vui lòng nhập biệt danh",
    nicknameLengthError: "Biệt danh phải có từ 3 đến 30 ký tự",
    nicknameInvalidError:
      "Biệt danh chỉ được chứa chữ cái, số, dấu gạch dưới, gạch ngang và dấu chấm",
    accountCreated: "Tạo tài khoản thành công! Vui lòng đăng nhập.",
    registrationFailed: "Đăng ký thất bại",
    loggedIn: "Đăng nhập thành công!",
    loginFailed: "Đăng nhập thất bại",
    cartTitle: "Giỏ hàng của bạn",
    cartEmpty: "Giỏ hàng của bạn đang trống.",
    remove: "Xóa",
    total: "Tổng cộng",
    checkout: "Thanh toán",
    each: "mỗi món",
    pleaseLoginToCheckout: "Vui lòng đăng nhập để thanh toán.",
    cartIsEmpty: "Giỏ hàng đang trống.",
    nothingToCheckout: "Không có gì để thanh toán.",
    singleSellerCheckoutMessage:
      "Chi co the thanh toan cac san pham tu cung mot nguoi ban trong mot don hang.",
    orderPlacedContinuePayment:
      "Đã tạo đơn hàng! Vui lòng hoàn tất thanh toán.",
    checkoutFailed: "Thanh toán thất bại",
    manualBankTransferRedirect:
      "Bạn sẽ được chuyển đến trang hướng dẫn chuyển khoản ngân hàng thủ công.",
    processing: "Đang xử lý...",
    continueToPayment: "Tiếp tục thanh toán",
    myOrders: "Đơn hàng của tôi",
    loadingOrders: "Đang tải đơn hàng...",
    noOrdersYet: "Bạn chưa đặt đơn hàng nào.",
    completePayment: "Hoàn tất thanh toán",
    paymentEvaluating: "Thanh toán đang được kiểm tra...",
    markAsCompleted: "Đánh dấu hoàn tất",
    unableToUpdateOrder: "Không thể cập nhật đơn hàng",
    orderPrefix: "Đơn hàng",
    productFallback: "Sản phẩm",
    loadingPaymentDetails: "Đang tải thông tin thanh toán...",
    orderNotFound: "Không tìm thấy đơn hàng.",
    completePaymentTitle: "Hoàn tất thanh toán",
    bankTransferInstructions: "Hướng dẫn chuyển khoản ngân hàng",
    transferExactAmount: "Vui lòng chuyển chính xác",
    toFollowingBankAccount: "đến tài khoản ngân hàng sau:",
    bankLabel: "Ngân hàng",
    accountNameLabel: "Tên tài khoản",
    accountNumberLabel: "Số tài khoản",
    memoLabel: "Nội dung",
    paymentInstructionsUnavailable:
      "Thong tin chuyen khoan hien chua duoc cau hinh. Vui long lien he admin.",
    exactMemoWarning:
      "* Bạn phải nhập đúng nội dung ở trên để chúng tôi nhận diện thanh toán.",
    paymentSubmitted: "Đã gửi xác nhận thanh toán.",
    failedToLoadOrder: "Không thể tải đơn hàng",
    failedToSubmit: "Không thể gửi xác nhận",
    paymentConfirmedPreparingOrder:
      "Thanh toán đã được xác nhận! Chúng tôi đang chuẩn bị đơn hàng của bạn.",
    viewMyOrders: "Xem đơn hàng của tôi",
    markedPaidOn: "Bạn đã đánh dấu đã thanh toán vào",
    awaitingManualConfirmation:
      "Đơn hàng chỉ được chuyển sang đã thanh toán sau khi quản trị viên xác nhận thủ công.",
    returnToOrders: "Quay lại đơn hàng",
    submitting: "Đang gửi...",
    iHavePaid: "Tôi đã thanh toán",
    loading: "Đang tải...",
    sellerDashboardTitle: "Bảng điều khiển người bán",
    pendingBalanceOnHold: "Số dư chờ xử lý (Đang giữ)",
    availableBalance: "Số dư khả dụng",
    payoutRequestTitle: "Yêu cầu rút tiền",
    payoutAmountLabel: "Số tiền rút",
    payoutAmountPlaceholder: "Nhập số tiền muốn rút",
    requestPayout: "Gửi yêu cầu rút tiền",
    payoutRequestSubmitted: "Đã gửi yêu cầu rút tiền",
    payoutAmountRequired: "Vui lòng nhập số tiền rút",
    payoutAmountMustBePositive: "Số tiền rút phải lớn hơn 0",
    payoutRequestFailed: "Không thể gửi yêu cầu rút tiền",
    paidOutBalance: "Đã chi trả",
    totalEarnings: "Tổng thu nhập",
    noSellerOrders: "Chưa có đơn hàng nào cho sản phẩm của bạn.",
    orderStatusLabel: "Trạng thái đơn hàng",
    moneyStatusLabel: "Trạng thái tiền",
    payoutStatusLabel: "Trạng thái thanh toán",
    sellerAmountLabel: "Tiền người bán",
    markAsDelivered: "Đánh dấu đã giao",
    orderMarkedDelivered: "Đơn hàng đã được đánh dấu là đã giao",
    unableToLoadSellerDashboard:
      "Không thể tải bảng điều khiển người bán",
    unableToUpdateOrderStatus: "Không thể cập nhật trạng thái đơn hàng",
    myProducts: "Sản phẩm của tôi",
    newProduct: "+ Sản phẩm mới",
    noSellerProducts: "Bạn chưa đăng bán sản phẩm nào.",
    edit: "Sửa",
    delete: "Xóa",
    deleteProductConfirm: "Xóa sản phẩm này?",
    productDeleted: "Đã xóa sản phẩm",
    deleteFailed: "Xóa thất bại",
    viewOrderItems: "Xem mục đơn hàng cho sản phẩm của tôi",
    salesOrderItems: "Đơn bán (mục đơn hàng)",
    quantityShort: "SL",
    sellerProfileNotFound: "Không tìm thấy người bán.",
    loadSellerProfileError: "Không thể tải trang người bán.",
    productNotFound: "Không tìm thấy sản phẩm.",
    back: "Quay lại",
    categoryLabel: "Danh mục",
    platformsLabel: "Nền tảng",
    offerTypesLabel: "Loại dịch vụ",
    productsLabel: "Sản phẩm",
    selectedCategoryLabel: "Danh mục đã chọn",
    selectedGameLabel: "Nền tảng đã chọn",
    selectedOfferTypeLabel: "Loại dịch vụ đã chọn",
    catalogContextPrefilled: "Ngữ cảnh danh mục đã được điền sẵn từ trang hiện tại.",
    categoryStillRequired: "Bạn vẫn cần chọn danh mục hệ thống hiện tại trước khi đăng bán.",
    gamesCategoryName: "Trò chơi",
    categoryAutoAssigned: "Danh mục của nền tảng đã được gán tự động cho tin đăng này.",
    categoryFallbackManual: "Không thể tự động gán danh mục cho lựa chọn này, vui lòng chọn thủ công.",
    stockLabel: "Tồn kho",
    quantity: "Số lượng",
    addToCart: "Thêm vào giỏ",
    addedToCart: "Đã thêm vào giỏ!",
    createProductTitle: "Tạo sản phẩm",
    editProductTitle: "Chỉnh sửa sản phẩm",
    titleLabel: "Tiêu đề",
    descriptionLabel: "Mô tả",
    priceLabel: "Giá ($)",
    stockFieldLabel: "Kho",
    selectCategory: "Chọn danh mục",
    imagesLabel: "Hình ảnh (tối đa 5, jpg/png, mỗi ảnh tối đa 5MB)",
    replaceImagesLabel: "Thay hình ảnh (tùy chọn)",
    replaceImagesHelp:
      "Tải lên hình ảnh mới sẽ thay thế toàn bộ hình ảnh hiện tại.",
    creating: "Đang tạo...",
    saving: "Đang lưu...",
    saveChanges: "Lưu thay đổi",
    sellInThisCategory: "Bán trong danh mục này",
    cancel: "Hủy",
    productCreated: "Tạo sản phẩm thành công!",
    productUpdated: "Cập nhật sản phẩm thành công!",
    createProductFailed: "Không thể tạo sản phẩm",
    updateFailed: "Cập nhật thất bại",
    noPlatformsAvailableYet: "Chưa có nền tảng nào.",
    noOfferTypesAvailableYet: "Chưa có loại dịch vụ nào.",
    noProductsFoundYet: "Chưa có sản phẩm nào.",
    statusPending: "Chờ thanh toán",
    statusPaid: "Đã thanh toán",
    statusDelivered: "Đã giao",
    statusCompleted: "Hoàn tất",
    statusCancelled: "Đã hủy",
    statusOnHold: "Đang giữ",
    statusAvailable: "Khả dụng",
    statusPaidOut: "Đã chi trả",
    statusPendingPayment: "Chờ thanh toán",
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
    browseProductsLink: "Browse products",
    searchProducts: "Search products...",
    allCategories: "All Categories",
    minPrice: "Min $",
    maxPrice: "Max $",
    loadingProducts: "Loading products...",
    noProducts: "No products found.",
    chooseGame: "Choose a category or platform to continue.",
    loadingGames: "Loading catalog sections...",
    loadCatalogError: "Unable to load catalog.",
    noGames: "No categories or platforms available.",
    backToCatalog: "Back to catalog",
    chooseOfferType: "Choose an offer type.",
    loadingOfferTypes: "Loading offer types...",
    noOfferTypes: "No offer types available.",
    gameNotFound: "Platform not found.",
    offerTypeNotFound: "Offer type not found.",
    backToOfferTypes: "Back to platform",
    browseProductsForSelection: "Browse products for this platform and offer type.",
    loadProductsError: "Unable to load products.",
    email: "Email",
    nickname: "Nickname",
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
    nicknameRequired: "Please enter a nickname",
    nicknameLengthError: "Nickname must be between 3 and 30 characters",
    nicknameInvalidError:
      "Nickname may only contain letters, numbers, underscores, hyphens, and dots",
    accountCreated: "Account created! Please log in.",
    registrationFailed: "Registration failed",
    loggedIn: "Logged in!",
    loginFailed: "Login failed",
    cartTitle: "Your Cart",
    cartEmpty: "Your cart is empty.",
    remove: "Remove",
    total: "Total",
    checkout: "Checkout",
    each: "each",
    pleaseLoginToCheckout: "Please log in to checkout.",
    cartIsEmpty: "Cart is empty.",
    nothingToCheckout: "Nothing to checkout.",
    singleSellerCheckoutMessage:
      "You can only check out products from one seller at a time.",
    orderPlacedContinuePayment:
      "Order placed! Please complete payment.",
    checkoutFailed: "Checkout failed",
    manualBankTransferRedirect:
      "You will be redirected to the manual bank transfer payment page.",
    processing: "Processing...",
    continueToPayment: "Continue to Payment",
    myOrders: "My Orders",
    loadingOrders: "Loading orders...",
    noOrdersYet: "You haven't placed any orders yet.",
    completePayment: "Complete Payment",
    paymentEvaluating: "Payment evaluating...",
    markAsCompleted: "Mark as Completed",
    unableToUpdateOrder: "Unable to update order",
    orderPrefix: "Order",
    productFallback: "Product",
    loadingPaymentDetails: "Loading payment details...",
    orderNotFound: "Order not found.",
    completePaymentTitle: "Complete Payment",
    bankTransferInstructions: "Bank Transfer Instructions",
    transferExactAmount: "Please transfer exactly",
    toFollowingBankAccount: "to the following bank account:",
    bankLabel: "Bank",
    accountNameLabel: "Account Name",
    accountNumberLabel: "Account Number",
    memoLabel: "Memo",
    paymentInstructionsUnavailable:
      "Payment instructions are not configured yet. Please contact support.",
    exactMemoWarning:
      "* Warning: You must include the exact memo above so we can identify your payment.",
    paymentSubmitted: "Payment submitted for confirmation.",
    failedToLoadOrder: "Failed to load order",
    failedToSubmit: "Failed to submit",
    paymentConfirmedPreparingOrder:
      "Payment has been confirmed! We are preparing your order.",
    viewMyOrders: "View My Orders",
    markedPaidOn: "You marked this as paid on",
    awaitingManualConfirmation:
      "Order will be marked paid only after manual confirmation from our admins.",
    returnToOrders: "Return to Orders",
    submitting: "Submitting...",
    iHavePaid: "I have paid",
    loading: "Loading...",
    sellerDashboardTitle: "Seller Dashboard",
    pendingBalanceOnHold: "Pending Balance (On Hold)",
    availableBalance: "Available Balance",
    payoutRequestTitle: "Request Payout",
    payoutAmountLabel: "Payout Amount",
    payoutAmountPlaceholder: "Enter payout amount",
    requestPayout: "Submit Payout Request",
    payoutRequestSubmitted: "Payout request submitted",
    payoutAmountRequired: "Please enter a payout amount",
    payoutAmountMustBePositive: "Payout amount must be greater than 0",
    payoutRequestFailed: "Unable to submit payout request",
    paidOutBalance: "Paid Out",
    totalEarnings: "Total Earnings",
    noSellerOrders: "No orders yet for your products.",
    orderStatusLabel: "Order Status",
    moneyStatusLabel: "Money Status",
    payoutStatusLabel: "Payout Status",
    sellerAmountLabel: "Seller Amount",
    markAsDelivered: "Mark as Delivered",
    orderMarkedDelivered: "Order marked as delivered",
    unableToLoadSellerDashboard: "Unable to load seller dashboard",
    unableToUpdateOrderStatus: "Unable to update order status",
    myProducts: "My Products",
    newProduct: "+ New Product",
    noSellerProducts: "You haven't listed any products yet.",
    edit: "Edit",
    delete: "Delete",
    deleteProductConfirm: "Delete this product?",
    productDeleted: "Product deleted",
    deleteFailed: "Delete failed",
    viewOrderItems: "View order items for my products",
    salesOrderItems: "Sales (Order Items)",
    quantityShort: "qty",
    sellerProfileNotFound: "Seller not found.",
    loadSellerProfileError: "Unable to load seller page.",
    productNotFound: "Product not found.",
    back: "Back",
    categoryLabel: "Category",
    platformsLabel: "Platforms",
    offerTypesLabel: "Offer Types",
    productsLabel: "Products",
    selectedCategoryLabel: "Selected Category",
    selectedGameLabel: "Selected Platform",
    selectedOfferTypeLabel: "Selected Offer Type",
    catalogContextPrefilled: "Catalog context was prefilled from this page.",
    categoryStillRequired: "You still need to choose a category before listing.",
    gamesCategoryName: "Games",
    categoryAutoAssigned: "The platform category was assigned automatically for this listing.",
    categoryFallbackManual: "We couldn't auto-assign a category for this selection, so please choose one manually.",
    stockLabel: "Stock",
    quantity: "Qty",
    addToCart: "Add to Cart",
    addedToCart: "Added to cart!",
    createProductTitle: "Create Product",
    editProductTitle: "Edit Product",
    titleLabel: "Title",
    descriptionLabel: "Description",
    priceLabel: "Price ($)",
    stockFieldLabel: "Stock",
    selectCategory: "Select category",
    imagesLabel: "Images (up to 5, jpg/png, max 5MB each)",
    replaceImagesLabel: "Replace Images (optional)",
    replaceImagesHelp:
      "Uploading new images will replace all existing ones.",
    creating: "Creating...",
    saving: "Saving...",
    saveChanges: "Save Changes",
    sellInThisCategory: "Sell in this category",
    cancel: "Cancel",
    productCreated: "Product created!",
    productUpdated: "Product updated!",
    createProductFailed: "Failed to create product",
    updateFailed: "Update failed",
    noPlatformsAvailableYet: "No platforms available yet",
    noOfferTypesAvailableYet: "No offer types available yet",
    noProductsFoundYet: "No products found yet",
    statusPending: "Pending",
    statusPaid: "Paid",
    statusDelivered: "Delivered",
    statusCompleted: "Completed",
    statusCancelled: "Cancelled",
    statusOnHold: "On Hold",
    statusAvailable: "Available",
    statusPaidOut: "Paid Out",
    statusPendingPayment: "Pending Payment",
    outOfStock: "Out of stock",
    inStock: (count) => `${count} in stock`,
  },
};

function formatFallbackLabel(value: string) {
  return value.replace("_", " ").replace(/\b\w/g, (char) => char.toUpperCase());
}

export function getOrderStatusLabel(
  messages: TranslationMessages,
  status: string
) {
  if (status === "pending") return messages.statusPending;
  if (status === "paid") return messages.statusPaid;
  if (status === "delivered") return messages.statusDelivered;
  if (status === "completed") return messages.statusCompleted;
  if (status === "cancelled") return messages.statusCancelled;
  return formatFallbackLabel(status);
}

export function getMoneyStatusLabel(
  messages: TranslationMessages,
  status: string
) {
  if (status === "on_hold") return messages.statusOnHold;
  if (status === "available") return messages.statusAvailable;
  if (status === "paid_out") return messages.statusPaidOut;
  if (status === "cancelled") return messages.statusCancelled;
  if (status === "pending_payment") return messages.statusPendingPayment;
  return formatFallbackLabel(status);
}

export function isLanguage(value: string | null): value is Language {
  return value === "vi" || value === "en";
}
