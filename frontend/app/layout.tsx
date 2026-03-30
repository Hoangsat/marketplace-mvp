// app/layout.tsx
import type { Metadata } from "next";
import "./globals.css";
import { LanguageProvider } from "@/components/LanguageProvider";
import Navbar from "@/components/Navbar";
import Toast from "@/components/Toast";

export const metadata: Metadata = {
  title: "MarketPy — Simple Marketplace",
  description: "A simple two-sided marketplace for buyers and sellers.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="vi">
      <body className="bg-gray-50 text-gray-900 antialiased">
        <LanguageProvider>
          <Navbar />
          <main className="max-w-6xl mx-auto px-4 py-6">{children}</main>
          <Toast />
        </LanguageProvider>
      </body>
    </html>
  );
}
