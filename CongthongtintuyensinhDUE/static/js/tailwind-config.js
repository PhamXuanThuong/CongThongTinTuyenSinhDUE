/* Cấu hình Tailwind dùng chung – sao chép token từ trang chủ (index.html).
   Nếu bạn đổi màu/kiểu chữ ở trang chủ, hãy chuyển cấu hình inline của index.html sang file này
   và để mọi trang cùng nạp file này ngay sau <script src="https://cdn.tailwindcss.com">. */
window.tailwind = window.tailwind || {};
tailwind.config = {
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        "primary": "#001e40",
        "on-primary": "#ffffff",
        "primary-container": "#003366",
        "on-primary-container": "#a7c8ff",
        "primary-fixed": "#d5e3ff",
        "primary-fixed-dim": "#a7c8ff",
        "on-primary-fixed": "#001b3c",
        "on-primary-fixed-variant": "#1f477b",
        "inverse-primary": "#a7c8ff",
        "secondary": "#9d4300",
        "on-secondary": "#ffffff",
        "secondary-container": "#fd761a",
        "on-secondary-container": "#5c2400",
        "secondary-fixed": "#ffdbca",
        "secondary-fixed-dim": "#ffb690",
        "on-secondary-fixed-variant": "#783200",
        "tertiary": "#002035",
        "on-tertiary": "#ffffff",
        "tertiary-container": "#003655",
        "on-tertiary-container": "#40a2e7",
        "tertiary-fixed": "#cce5ff",
        "tertiary-fixed-dim": "#93ccff",
        "on-tertiary-fixed": "#001d31",
        "on-tertiary-fixed-variant": "#004b73",
        "error": "#ba1a1a",
        "on-error": "#ffffff",
        "error-container": "#ffdad6",
        "on-error-container": "#93000a",
        "background": "#faf8ff",
        "on-background": "#131b2e",
        "surface": "#faf8ff",
        "surface-bright": "#faf8ff",
        "surface-dim": "#d2d9f4",
        "surface-tint": "#3a5f94",
        "surface-variant": "#dae2fd",
        "surface-container-lowest": "#ffffff",
        "surface-container-low": "#f2f3ff",
        "surface-container": "#eaedff",
        "surface-container-high": "#e2e7ff",
        "surface-container-highest": "#dae2fd",
        "on-surface": "#131b2e",
        "on-surface-variant": "#43474f",
        "inverse-surface": "#283044",
        "inverse-on-surface": "#eef0ff",
        "outline": "#737780",
        "outline-variant": "#c3c6d1"
      },
      borderRadius: { DEFAULT: "0.25rem", lg: "0.5rem", xl: "0.75rem", "2xl": "1rem", full: "9999px" },
      spacing: {
        "space-xs": "0.25rem", "space-sm": "0.5rem", "space-md": "1rem", "space-lg": "1.5rem",
        "space-xl": "2.5rem", "space-2xl": "4rem", "gutter": "1.5rem", "gutter-mobile": "1rem",
        "margin": "2rem", "margin-mobile": "1rem", "margin-desktop": "3rem"
      },
      fontFamily: {
        "display-hero": ["Space Grotesk"], "display-hero-mobile": ["Space Grotesk"],
        "headline-lg": ["Space Grotesk"], "headline-lg-mobile": ["Space Grotesk"],
        "headline-md": ["Space Grotesk"], "headline-sm": ["Space Grotesk"],
        "body-lg": ["Be Vietnam Pro"], "body-md": ["Be Vietnam Pro"], "body-sm": ["Be Vietnam Pro"],
        "label-lg": ["Be Vietnam Pro"], "label-md": ["Be Vietnam Pro"], "label-sm": ["Be Vietnam Pro"]
      },
      fontSize: {
        "display-hero": ["56px", { lineHeight: "64px", letterSpacing: "-0.03em", fontWeight: "700" }],
        "display-hero-mobile": ["36px", { lineHeight: "44px", letterSpacing: "-0.02em", fontWeight: "700" }],
        "headline-lg": ["36px", { lineHeight: "44px", letterSpacing: "-0.02em", fontWeight: "700" }],
        "headline-lg-mobile": ["28px", { lineHeight: "36px", letterSpacing: "-0.01em", fontWeight: "700" }],
        "headline-md": ["24px", { lineHeight: "32px", letterSpacing: "-0.01em", fontWeight: "600" }],
        "headline-sm": ["20px", { lineHeight: "28px", fontWeight: "600" }],
        "body-lg": ["18px", { lineHeight: "28px", fontWeight: "400" }],
        "body-md": ["16px", { lineHeight: "24px", fontWeight: "400" }],
        "body-sm": ["14px", { lineHeight: "20px", fontWeight: "400" }],
        "label-lg": ["14px", { lineHeight: "20px", letterSpacing: "0.01em", fontWeight: "600" }],
        "label-md": ["12px", { lineHeight: "16px", letterSpacing: "0.02em", fontWeight: "600" }],
        "label-sm": ["11px", { lineHeight: "14px", letterSpacing: "0.04em", fontWeight: "700" }]
      }
    }
  }
};
