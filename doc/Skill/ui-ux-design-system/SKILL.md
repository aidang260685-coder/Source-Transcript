---
name: "ui-ux-design-system"
description: "Bộ chuẩn quy tắc thiết kế UI/UX toàn diện: Figma Design Tokens, 8pt Grid, Typography Montserrat, Layout dàn trang (Header, Main, Footer, Print A4), Accessibility WCAG 2.1 AA, Hợp đồng giao tiếp Frontend ↔ Backend, và bộ công cụ bắt lỗi tự động trên UI, API và DevTools (F12)."
---

# KTT UI/UX Design System & Fullstack Quality Assurance

Tài liệu này định nghĩa hệ thống chuẩn thiết kế giao diện người dùng (UI/UX Design System) và bộ quy tắc kiến trúc từ **Senior Frontend UI/UX Architect đến Backend Engineer**. Hệ thống này đảm bảo tính nhất quán thị giác 100% với Figma, trải nghiệm người dùng tối ưu, khả năng truy cập (Accessibility WCAG 2.1 AA), chuẩn in ấn xuất bản A4, và kiểm thử tự động bắt lỗi từ UI, DevTools (F12) đến API hợp đồng backend.

---

## 1. Triết Lý Thiết Kế & Nguyên Tắc Nền Tảng (Core Principles)

1. **Atomic Design System**:
   * **Atoms (Nguyên tử)**: Màu sắc (Tokens), Typography, Spacing, Icons, Buttons, Badges, Input fields.
   * **Molecules (Phân tử)**: Form Field (Label + Input + Error), Search Bar, User Avatar Dropdown.
   * **Organisms (Sinh vật)**: Header + Sticky Nav, Sidebar Navigation, Data Table, Card Grid, Footer.
   * **Templates (Khung dàn trang)**: Khung Meeting Note A4, Khung Dashboard, Khung Detail Page.
   * **Pages (Trang thực tế)**: Trang hoàn chỉnh có dữ liệu thực tế từ API.

2. **Hệ Lưới 8pt Grid System (Figma Auto-Layout Harmony)**:
   * Mọi khoảng cách lề (margin), đệm (padding), khoảng cách giữa các phần tử (gap) và kích thước chiều cao (height) đều là bội số của **8px** (với 4px làm bước vi mô micro-spacing).
   * Thang đo: `4px, 8px, 12px, 16px, 20px, 24px, 32px, 40px, 48px, 64px`.

3. **Tiêu Chuẩn Truy Cập & Khả Năng Đọc (WCAG 2.1 AA Compliance)**:
   * **Contrast Ratio (Độ tương phản)**: Tối thiểu **4.5:1** cho văn bản thường (< 18pt hoặc < 14pt bold) và **3:1** cho văn bản kích thước lớn / UI components.
   * **Focus States**: Mọi phần tử tương tác (button, input, link) phải có `outline` hoặc `box-shadow` rõ ràng khi focus qua phím Tab (`:focus-visible`).
   * **Touch Target**: Kích thước vùng bấm tối thiểu **44px × 44px** trên thiết bị cảm ứng.
   * **Screen Reader**: Sử dụng HTML5 Semantic tags (`<header>`, `<nav>`, `<main>`, `<footer>`, `<article>`) kèm thuộc tính `aria-label`, `aria-expanded`, `role`.

4. **In Ấn & Xuất Bản PDF A4 (Print-Ready CSS Paged Media)**:
   * Thiết kế dàn trang tài liệu nội bộ (Biên bản họp, Báo cáo BSC/KPI) phải hỗ trợ hoàn hảo chế độ in `@media print`:
     * Khổ giấy: Chuẩn `A4` (`210mm × 297mm`).
     * Lề in an toàn: `15mm 15mm 20mm 15mm`.
     * Phân trang: Điều khiển ngắt trang chính xác qua `.page-break` (`break-before: page;`) và chống cắt xén nội dung qua `.avoid-break` (`break-inside: avoid;`).

---

## 2. Hệ Thống Design Tokens (Figma Mapping)

Bộ Design Tokens được quản lý tập trung tại [assets/design_tokens.json](file:///d:/IT%20KTT/ProjectDEV/Source-Transcript/doc/Skill/ui-ux-design-system/assets/design_tokens.json) và ánh xạ thành CSS Custom Properties tại [assets/design_tokens.css](file:///d:/IT%20KTT/ProjectDEV/Source-Transcript/doc/Skill/ui-ux-design-system/assets/design_tokens.css).

### 2.1. Typography Standard (Font Chữ & Phân Cấp)
* **Font gia đình chủ đạo**: **`Montserrat`** (theo chuẩn mực văn bản của Kiên Thành Tín).
  * Stack chuẩn: `'Montserrat', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif`.
  * Fallback Code: `'JetBrains Mono', 'Fira Code', 'Courier New', monospace`.
* **Thang kích thước & Trọng lượng**:

| Token | Kích Thước (rem / px) | Line Height | Font Weight | Mục Đích Sử Dụng |
|---|---|---|---|---|
| `--ktt-text-xs` | `0.75rem` (12px) | 1.25 | 500 / 600 | Badges, Helper text, Citations (`data-ref`), Timestamps |
| `--ktt-text-sm` | `0.875rem` (14px) | 1.375 | 400 / 500 | Table cells, Secondary body, Form labels, Footnotes |
| `--ktt-text-base` | `1.00rem` (16px) | 1.50 | 400 (Regular) | Nội dung đoạn văn chính (Body copy), Button text |
| `--ktt-text-lg` | `1.125rem` (18px) | 1.50 | 500 (Medium) | Đoạn mở đầu (Lead paragraph), Subtitle |
| `--ktt-text-xl` | `1.25rem` (20px) | 1.375 | 600 (Semibold) | Tiêu đề Heading 4 (H4), Card titles |
| `--ktt-text-2xl` | `1.50rem` (24px) | 1.25 | 600 / 700 | Tiêu đề Heading 3 (H3), Section headings |
| `--ktt-text-3xl` | `1.875rem` (30px) | 1.25 | 700 (Bold) | Tiêu đề Heading 2 (H2), Page block headers |
| `--ktt-text-4xl` | `2.25rem` (36px) | 1.20 | 700 (Bold) | Tiêu đề Heading 1 (H1), Page Title |
| `--ktt-text-5xl` | `3.00rem` (48px) | 1.15 | 700 (Bold) | Banner Hero, Số liệu Dashboard nổi bật |

### 2.2. Bảng Màu Chuẩn (Color Palette & Semantics)
* **Brand / Primary**:
  * Default: `--ktt-color-primary: #1A56DB` (Xanh hoàng gia KTT, đạt WCAG tương phản > 5.8:1 trên nền trắng).
  * Hover: `--ktt-color-primary-hover: #1E429F`.
  * Active: `--ktt-color-primary-active: #233876`.
  * Light Background: `--ktt-color-primary-light: #EBF5FF`.
* **Neutral Slate Scale**:
  * Nền chính: `--ktt-color-neutral-50: #F9FAFB`.
  * Đường viền thẻ (Border): `--ktt-color-neutral-200: #E5E7EB`.
  * Văn bản phụ: `--ktt-color-neutral-500: #6B7280`.
  * Văn bản chính: `--ktt-color-neutral-800: #1F2A37`.
  * Tiêu đề đậm: `--ktt-color-neutral-900: #111827`.
* **Semantic Feedback**:
  * Success: `--ktt-color-success: #0E9F6E` (Nền: `#F3FAF7`).
  * Warning: `--ktt-color-warning: #F59E0B` (Nền: `#FDFDEA`).
  * Danger / Error: `--ktt-color-danger: #E02424` (Nền: `#FDF2F2`).
  * Info: `--ktt-color-info: #3F83F8` (Nền: `#E1EFFE`).

---

## 3. Kiến Trúc Dàn Trang (Standard Page Anatomy)

Mỗi trang ứng dụng web hoặc tài liệu HTML trong dự án phải tuân thủ cấu trúc 5 tầng tiêu chuẩn:

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. HEADER (role="banner", sticky top, Logo KTT + Global Nav)     │
├─────────────────────────────────────────────────────────────────┤
│ 2. BREADCRUMBS & CONTEXT BAR (Vị trí hiện tại, Back button)     │
├─────────────────────────────────────────────────────────────────┤
│ 3. MAIN CONTENT (role="main", max-width: 1280px / A4 210mm)     │
│    ┌───────────────────────────────┬───────────────────────┐    │
│    │ Primary Column (70%)          │ Sidebar / Aside (30%) │    │
│    │ - Section H2 + Cards Grid     │ - Metadata, Summary   │    │
│    │ - Tables & Data List          │ - Action buttons      │    │
│    └───────────────────────────────┴───────────────────────┘    │
├─────────────────────────────────────────────────────────────────┤
│ 4. FOOTER (role="contentinfo", Copyright, System Status, Links) │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4. Giao Tiếp Frontend UI/UX ↔ Backend API Contract

Để loại trừ hoàn toàn các lỗi bất đồng bộ giữa giao diện và server, mọi API endpoint giao tiếp với Frontend phải tuân thủ chuẩn sau:

### 4.1. Cấu Trúc Phản Hồi Thành Công (Envelope Schema)
```json
{
  "success": true,
  "data": {
    "id": "rec_01HXYZ",
    "title": "Biên bản Họp Quý 3",
    "status": "APPROVED",
    "author": "Anh Tân (Kho)",
    "created_at": "2026-11-19T20:53:51+07:00"
  },
  "meta": {
    "page": 1,
    "limit": 20,
    "total": 1,
    "timestamp": 1795100031
  }
}
```

### 4.2. Cấu Trúc Phản Hồi Lỗi (Chuẩn RFC 7807 Problem Details)
Khi xảy ra lỗi (HTTP 4xx, 5xx), backend **không bao giờ** trả về HTML stack trace mà luôn trả JSON có format:
```json
{
  "type": "https://api.kienthanhtin.com/errors/validation-failed",
  "title": "Dữ liệu yêu cầu không hợp lệ",
  "status": 422,
  "detail": "Trường 'deadline' phải là một ngày làm việc trong tuần hợp lệ.",
  "instance": "/api/v1/meeting-notes/rec_01HXYZ",
  "invalid_params": [
    {
      "name": "deadline",
      "reason": "Ngày hoàn thành không được rơi vào Chủ Nhật."
    }
  ]
}
```

### 4.3. Năm Trạng Thái Giao Diện Bắt Buộc (The 5 Essential UI States)
1. **Initial / Idle**: Trạng thái mặc định ban đầu.
2. **Loading State**: Hiển thị **Skeleton Screen** thay vì một vòng tròn xoay spinner thô ráp để tránh giật giao diện (Cumulative Layout Shift - CLS).
3. **Empty State**: Khi dữ liệu trả về mảng rỗng `[]`, phải có hình ảnh minh họa + thông điệp thân thiện + Nút hành động kêu gọi (CTA).
4. **Error State**: Hiển thị hộp cảnh báo màu đỏ/cam rõ ràng từ `detail` của API kèm nút "Thử lại" (Retry).
5. **Success / Optimistic State**: Cập nhật UI ngay lập tức trước khi server phản hồi để tạo cảm giác phản hồi tức thì (< 100ms).

---

## 5. Quy Trình Bắt Lỗi Tự Động (DevTools F12, UI & API)

Bộ công cụ kiểm tra tự động nằm tại:
* Script Python CLI: [scripts/ui_audit_scanner.py](file:///d:/IT%20KTT/ProjectDEV/Source-Transcript/doc/Skill/ui-ux-design-system/scripts/ui_audit_scanner.py)
* Test Suite Pytest: [tests/test_ui_ux_design_system.py](file:///d:/IT%20KTT/ProjectDEV/Source-Transcript/tests/test_ui_ux_design_system.py)

### 5.1. Bắt Lỗi UI & Visual Linter
* **Font Lạ / Sai Quy Chuẩn**: Bắt lỗi mọi CSS khai báo font chữ không chứa font chủ đạo `Montserrat`.
* **Vỡ Dàn Trang & Layout**: Kiểm tra thiếu thẻ `<meta name="viewport">` làm giao diện vỡ trên thiết bị di động.
* **Inline Styles Hỗn Loạn**: Phát hiện style cứng (`style="..."`) không qua CSS variables.
* **Hình Ảnh Không Chuẩn**: Bắt lỗi thẻ `<img>` thiếu thuộc tính `alt`, thiếu `width/height` gây Layout Shift (CLS).

### 5.2. Bắt Lỗi DevTools (F12) & DOM Tree
* **Thẻ HTML Không Cân Bằng**: Phát hiện lệch số lượng thẻ mở và thẻ đóng (`<div>`, `<table>`, `<section>`).
* **Semantic & Accessibility Lỗi**: Thẻ `<button>` hoặc `<a>` rỗng nội dung không có `aria-label`, link trỏ vào `href="#"` hoặc rỗng.
* **Console Warnings & Errors**: Quét các đoạn mã JavaScript chứa `console.error()`, unhandled promise rejections hoặc gọi tài nguyên 404.
* **Độ Sâu DOM (DOM Depth)**: Cảnh báo nếu DOM lồng nhau sâu hơn **24 tầng**, gây suy giảm hiệu năng render của trình duyệt.

### 5.3. Bắt Lỗi Hợp Đồng API (Contract Testing)
* **Trạng Thái Mã Lỗi**: Đảm bảo mã lỗi tuân thủ đúng chuẩn RESTful (400, 401, 403, 404, 422, 500).
* **Chuẩn Hóa Ngày Tháng**: Toàn bộ mốc thời gian phải tuân thủ định dạng ISO 8601 (`YYYY-MM-DDTHH:MM:SSZ`).
* **Khớp Schema Envelope**: Xác minh payload response luôn chứa các trường `success`, `data` hoặc `error`.

---

## 6. Hướng Dẫn Chạy Kiểm Thử Bắt Lỗi UI / API / DevTools

Chạy trực tiếp từ terminal của dự án:

```powershell
# 1. Chạy kịch bản quét tĩnh toàn diện UI & DevTools
.\.venv\Scripts\python.exe doc/Skill/ui-ux-design-system/scripts/ui_audit_scanner.py

# 2. Chạy bộ kiểm thử tự động Pytest
.\.venv\Scripts\pytest.exe tests/test_ui_ux_design_system.py -v
```
