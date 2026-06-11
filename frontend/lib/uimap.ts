// Cơ chế khai báo hiển thị cho enum: mỗi giá trị → { label, variant }.
// Component đọc map qua uiOf() → không if/else màu rải rác, không hardcode nhãn.

export type BadgeVariant = "success" | "warning" | "danger" | "neutral" | "info";

export interface UIMapEntry {
  label: string;
  variant: BadgeVariant;
  hint?: string;
}

export type UIMap<K extends string> = Record<K, UIMapEntry>;

/**
 * Tra entry an toàn:
 * - key null/undefined → "—" neutral
 * - key có nhưng CHƯA khai trong map → hiện chính giá trị gốc (neutral), không nuốt thành "—".
 */
export function uiOf<K extends string>(
  map: UIMap<K>,
  key: K | null | undefined,
): UIMapEntry {
  if (key && map[key]) return map[key];
  return { label: key ?? "—", variant: "neutral" };
}
