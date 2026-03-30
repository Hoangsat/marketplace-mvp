import { Suspense } from "react";
import NewProductPageClient from "./NewProductPageClient";

export default function NewProductPage() {
  return (
    <Suspense fallback={null}>
      <NewProductPageClient />
    </Suspense>
  );
}
