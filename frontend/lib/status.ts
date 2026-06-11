// Khai báo TẬP TRUNG mọi enum hiển thị của app. Thêm trạng thái = thêm 1 dòng ở đây.
import type { UIMap } from "./uimap";
import type { ReconcileStatus } from "./types";

export const RECONCILE_STATUS_UIMAP: UIMap<ReconcileStatus> = {
  matched: { label: "Khớp", variant: "success", hint: "Đơn hoàn tất, đã thu đủ tiền" },
  refunded: { label: "Hoàn tiền", variant: "warning", hint: "Khách trả hàng, tiền về ít/âm" },
  orphan: { label: "Tiền lạ", variant: "danger", hint: "Sàn trả tiền cho đơn không có trong sổ" },
  unsettled: { label: "Chưa thanh toán", variant: "neutral", hint: "Đơn có nhưng sàn chưa trả tiền" },
};

export const RECONCILE_STATUS_ORDER: ReconcileStatus[] = [
  "matched",
  "refunded",
  "orphan",
  "unsettled",
];

export type OrderStatus = "completed" | "cancelled";

export const ORDER_STATUS_UIMAP: UIMap<OrderStatus> = {
  completed: { label: "Hoàn tất", variant: "success" },
  cancelled: { label: "Đã huỷ", variant: "danger" },
};
