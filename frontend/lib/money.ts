const vnd = new Intl.NumberFormat("vi-VN");

export function formatVnd(n: number | null | undefined): string {
  if (n == null) return "—";
  return `${vnd.format(n)} ₫`;
}

export function formatPercent(ratio: number): string {
  return `${(ratio * 100).toFixed(2)}%`;
}
