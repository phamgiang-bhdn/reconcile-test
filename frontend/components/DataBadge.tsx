import type { UIMapEntry } from "@/lib/uimap";

// Badge dùng chung: chỉ nhận một UIMapEntry, không tự quyết màu/nhãn.
export function DataBadge({ entry }: { entry: UIMapEntry }) {
  return (
    <span className={`badge badge--${entry.variant}`} title={entry.hint}>
      {entry.label}
    </span>
  );
}
