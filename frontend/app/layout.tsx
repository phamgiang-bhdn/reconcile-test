import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Reconciliation Dashboard",
  description: "Đối soát đơn hàng với thanh toán sàn",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="vi">
      <body>{children}</body>
    </html>
  );
}
