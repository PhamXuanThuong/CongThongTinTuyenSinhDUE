/* =========================================================
   portal.js – dùng chung cho mọi trang của cổng thông tin
   1) Gắn menu xổ xuống cho "KHOA" và "DÀNH CHO SINH VIÊN"
   2) Trang con: mượn header/footer từ index.html để giữ giao diện thống nhất
   ========================================================= */
(function () {
  const D = window.DUE_DATA;
  /* Đường dẫn: mọi trang con nằm trong portal.html và dùng hash (#/khoa/ketoan, #/sinh-vien/clb/see-club)
     → chạy được với mọi server (http.server, Django, Flask), mở bằng file:// và trong khung xem trước. */
  const PORTAL_FILE = "portal.html";
  const base = () => (document.body && document.body.hasAttribute("data-portal") ? "" : PORTAL_FILE);
  const L = {
    home: () => (document.body && document.body.dataset.home) || "index.html",
    khoa: (id, sec) => base() + "#/khoa" + (id ? "/" + id : "") + (sec ? "/" + sec : ""),
    sv: (tab, sub) => base() + "#/sinh-vien" + (tab ? "/" + tab : "") + (sub ? "/" + sub : "")
  };

  const FACULTY_ICONS = {
    tcnh: "account_balance", dlkdqt: "travel_explore", tmdt_mkt_cns: "storefront",
    kt: "monitoring", qtkd: "business_center", ketoan: "calculate",
    llct: "auto_stories", luat: "gavel", vdtqt: "public"
  };

  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const shortName = (name) => name.replace(/^Khoa\s+/i, "");
  const icon = (name, cls = "") => `<span class="material-symbols-outlined ${cls}" aria-hidden="true">${name}</span>`;
  const qs = (k) => new URLSearchParams(location.search).get(k);

  /* ---------------- Menu xổ xuống ---------------- */
  function findNavLink(root, path, text) {
    return root.querySelector(`a[data-path="${path}"]`) ||
      [...root.querySelectorAll("nav a")].find((a) => a.textContent.trim().toUpperCase() === text);
  }

  function facultyMenuHTML() {
    const items = D.faculties.map((f) => {
      const n = D.majors.filter((m) => m.faculty_id === f.id).length;
      const sub = f.type === "institute" ? "Chương trình liên kết quốc tế" : `${n} ngành tuyển sinh 2026`;
      return `
        <a href="${L.khoa(f.id)}" role="menuitem"
           class="group/item flex items-start gap-space-md p-space-md rounded-xl hover:bg-surface-container-low focus:bg-surface-container-low focus:outline-none transition-colors">
          <span class="shrink-0 w-10 h-10 rounded-lg bg-primary-fixed text-primary-container flex items-center justify-center group-hover/item:bg-primary-container group-hover/item:text-on-primary transition-colors">
            ${icon(FACULTY_ICONS[f.id] || "school", "text-[22px]")}
          </span>
          <span class="flex flex-col">
            <span class="font-label-lg text-label-lg text-on-surface normal-case">${esc(shortName(f.name))}</span>
            <span class="font-body-sm text-body-sm text-on-surface-variant normal-case">${sub}</span>
          </span>
        </a>`;
    }).join("");
    return `
      <div class="p-space-md">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-space-xs">${items}</div>
      </div>
      <div class="border-t border-outline-variant/60 bg-surface-container-low px-space-lg py-space-md flex items-center justify-between rounded-b-xl">
        <span class="font-body-sm text-body-sm text-on-surface-variant normal-case">8 khoa và Viện Đào tạo quốc tế</span>
        <a href="${L.khoa()}" class="inline-flex items-center gap-space-xs font-label-lg text-label-lg text-primary-container hover:text-secondary normal-case">
          Xem tất cả ${icon("arrow_forward", "text-[18px]")}
        </a>
      </div>`;
  }

  function studentMenuHTML() {
    const items = [
      { href: L.sv("doan-hoi"), ic: "groups", t: "Đoàn Thanh niên – Hội Sinh viên", s: "Cơ cấu, phong trào, chiến dịch tình nguyện" },
      { href: L.sv("lcd"), ic: "diversity_3", t: "Liên chi đoàn các khoa", s: `${D.lien_chi_doan.length} Liên chi đoàn trực thuộc` },
      { href: L.sv("clb"), ic: "interests", t: "Câu lạc bộ – Đội – Nhóm", s: `${D.clubs.length} CLB học thuật, kỹ năng, văn nghệ, thể thao` }
    ];
    return `<div class="p-space-md flex flex-col gap-space-xs">${items.map((i) => `
      <a href="${i.href}" role="menuitem"
         class="group/item flex items-start gap-space-md p-space-md rounded-xl hover:bg-surface-container-low focus:bg-surface-container-low focus:outline-none transition-colors">
        <span class="shrink-0 w-10 h-10 rounded-lg bg-secondary-fixed text-secondary flex items-center justify-center group-hover/item:bg-secondary-container group-hover/item:text-white transition-colors">
          ${icon(i.ic, "text-[22px]")}
        </span>
        <span class="flex flex-col">
          <span class="font-label-lg text-label-lg text-on-surface normal-case">${i.t}</span>
          <span class="font-body-sm text-body-sm text-on-surface-variant normal-case">${i.s}</span>
        </span>
      </a>`).join("")}</div>`;
  }

  function attachDropdown(link, panelHTML, widthCls, align = "left") {
    if (!link || link.dataset.dropdown) return;
    link.dataset.dropdown = "1";
    const wrap = document.createElement("div");
    wrap.className = "relative h-full flex items-center";
    link.parentNode.insertBefore(wrap, link);
    wrap.appendChild(link);

    link.setAttribute("aria-haspopup", "true");
    link.setAttribute("aria-expanded", "false");
    link.classList.add("gap-1");
    link.insertAdjacentHTML("beforeend", icon("expand_more", "text-[18px] transition-transform duration-200 dd-chevron"));

    const panel = document.createElement("div");
    panel.setAttribute("role", "menu");
    panel.className = `dd-panel absolute top-full ${align === "right" ? "right-0" : "left-1/2 -translate-x-1/2"} pt-space-sm ${widthCls} opacity-0 invisible translate-y-1 transition-all duration-200 z-50`;
    panel.innerHTML = `<div class="bg-surface-container-lowest rounded-xl shadow-[0_12px_40px_rgba(0,30,64,0.16)] border border-outline-variant/50 overflow-hidden">${panelHTML}</div>`;
    wrap.appendChild(panel);

    let timer;
    const open = () => {
      clearTimeout(timer);
      document.querySelectorAll(".dd-open").forEach((w) => w !== wrap && close(w));
      wrap.classList.add("dd-open");
      panel.classList.remove("opacity-0", "invisible", "translate-y-1");
      link.setAttribute("aria-expanded", "true");
      link.querySelector(".dd-chevron").style.transform = "rotate(180deg)";
    };
    const close = (w = wrap) => {
      const p = w.querySelector(".dd-panel"), l = w.querySelector("a[aria-haspopup]");
      w.classList.remove("dd-open");
      p.classList.add("opacity-0", "invisible", "translate-y-1");
      l.setAttribute("aria-expanded", "false");
      l.querySelector(".dd-chevron").style.transform = "";
    };
    wrap.addEventListener("mouseenter", () => matchMedia("(hover:hover)").matches && open());
    wrap.addEventListener("mouseleave", () => { timer = setTimeout(() => close(), 150); });
    link.addEventListener("click", (e) => {
      e.preventDefault();
      // Máy tính: rê chuột đã mở menu → bấm thì giữ mở. Cảm ứng: bấm để bật/tắt.
      if (matchMedia("(hover:hover)").matches || !wrap.classList.contains("dd-open")) open(); else close();
    });
    link.addEventListener("keydown", (e) => {
      if (e.key === "ArrowDown") { e.preventDefault(); open(); panel.querySelector("a")?.focus(); }
    });
    panel.addEventListener("keydown", (e) => {
      const links = [...panel.querySelectorAll("a")], i = links.indexOf(document.activeElement);
      if (e.key === "ArrowDown") { e.preventDefault(); links[(i + 1) % links.length].focus(); }
      if (e.key === "ArrowUp") { e.preventDefault(); links[(i - 1 + links.length) % links.length].focus(); }
      if (e.key === "Escape") { close(); link.focus(); }
    });
    document.addEventListener("click", (e) => { if (!wrap.contains(e.target)) close(); });
    panel.addEventListener("click", (e) => { if (e.target.closest("a")) close(); });
    document.addEventListener("keydown", (e) => { if (e.key === "Escape") close(); });
  }

  let lastActive = null;
  function setActive(root, path) {
    if (path) lastActive = path;
    const nav = root.querySelector("nav[data-active-classes]") || root.querySelector("nav");
    if (!nav || !path) return;
    const activeCls = (nav.dataset.activeClasses || "text-secondary-container border-b-2 border-secondary-container font-bold").split(/\s+/);
    const inactiveCls = ["text-on-surface-variant", "hover:text-primary-container"];
    nav.querySelectorAll("a[data-path]").forEach((a) => {
      const on = a.dataset.path === path;
      a.classList.remove(...activeCls, "font-bold", ...(on ? inactiveCls : []));
      if (on) a.classList.add(...activeCls, "font-bold"); else a.classList.add(...inactiveCls);
    });
  }

  function enhanceNav(root = document) {
    const home = findNavLink(root, "trang-chu", "TRANG CHỦ");
    if (home && home.getAttribute("href") === "#") home.setAttribute("href", L.home());
    attachDropdown(findNavLink(root, "khoa", "KHOA"), facultyMenuHTML(), "w-[min(92vw,640px)]");
    const sv = findNavLink(root, "danh-cho-sinh-vien", "DÀNH CHO SINH VIÊN") || findNavLink(root, "sinh-vien", "DÀNH CHO SINH VIÊN");
    attachDropdown(sv, studentMenuHTML(), "w-[min(92vw,380px)]");
    if (sv && !sv.dataset.path) sv.dataset.path = "danh-cho-sinh-vien";
  }

  /* ---------------- Header/footer cho trang con ---------------- */
  const FALLBACK_HEADER = `
    <header class="fixed top-0 left-0 right-0 z-50 bg-surface-container-lowest/90 backdrop-blur-xl shadow-[0_1px_8px_rgba(0,0,0,0.04)]">
      <div class="max-w-7xl mx-auto px-6 lg:px-12 flex items-center justify-between min-h-[5rem] gap-space-lg">
        <a href="index.html" class="font-headline-sm text-headline-sm text-primary-container">DUE Tuyển sinh</a>
        <nav class="flex items-center gap-space-lg h-[5rem] overflow-x-auto" data-active-classes="text-secondary-container border-b-2 border-secondary-container">
          <a class="h-full flex items-center font-label-lg text-label-lg text-on-surface-variant uppercase whitespace-nowrap" data-path="trang-chu" href="index.html">Trang chủ</a>
          <a class="h-full flex items-center font-label-lg text-label-lg text-on-surface-variant uppercase whitespace-nowrap" data-path="khoa" href="#">Khoa</a>
          <a class="h-full flex items-center font-label-lg text-label-lg text-on-surface-variant uppercase whitespace-nowrap" data-path="danh-cho-sinh-vien" href="#">Dành cho sinh viên</a>
        </nav>
      </div>
    </header>`;

  async function mountLayout(activePath) {
    const hSlot = document.getElementById("site-header"), fSlot = document.getElementById("site-footer");
    let header = null, footer = null;
    try {
      for (const url of [L.home(), "/"]) {                    // index.html hoặc trang gốc của server (Django/Flask)
        const res = await fetch(url, { cache: "no-cache" });
        if (!res.ok) continue;
        const doc = new DOMParser().parseFromString(await res.text(), "text/html");
        header = doc.querySelector("header");
        footer = doc.querySelector("footer");
        if (header) break;
      }
    } catch (_) { /* mở bằng file:// – dùng header dự phòng */ }
    if (hSlot) hSlot.outerHTML = header ? header.outerHTML : FALLBACK_HEADER;
    if (fSlot && footer) fSlot.outerHTML = footer.outerHTML;
    enhanceNav(document);
    setActive(document, activePath || lastActive);
  }

  /* ---------------- Router cho portal.html ---------------- */
  function startRouter({ homeView } = {}) {
    const app = document.getElementById("app");
    let current = "";
    const go = () => {
      const [page, a, b] = decodeURIComponent(location.hash.replace(/^#\/?/, "")).split("/").filter(Boolean);
      const kind = page === "khoa" ? "khoa" : page === "sinh-vien" ? "sv" : homeView ? "home" : "khoa";
      if (kind !== current) { app.innerHTML = ""; delete app._svRoute; delete app.dataset.view; current = kind; }
      if (kind === "khoa") { setActive(document, "khoa"); window.DUE.views.khoa(app, a, b); }
      else if (kind === "sv") { setActive(document, "danh-cho-sinh-vien"); window.DUE.views.sv(app, a, b); document.title = "Dành cho sinh viên - Cổng thông tin tuyển sinh DUE"; }
      else { setActive(document, "trang-chu"); homeView(app); window.scrollTo(0, 0); }
    };
    window.addEventListener("hashchange", go);
    // Tự xử lý link "#/..." – cần cho khung xem trước (iframe srcdoc), nơi link hash mặc định bị mở sang about:blank
    document.addEventListener("click", (e) => {
      const a = e.target.closest && e.target.closest('a[href^="#/"]');
      if (!a || e.defaultPrevented || e.button !== 0 || e.ctrlKey || e.metaKey || e.shiftKey) return;
      e.preventDefault();
      const h = a.getAttribute("href");
      if (location.hash === h) go(); else location.hash = h;
    });
    go();
  }

  window.DUE = { D, esc, icon, shortName, qs, FACULTY_ICONS, L, enhanceNav, setActive, mountLayout, startRouter, views: (window.DUE && window.DUE.views) || {} };

  // Trang chủ: chỉ cần gắn menu (không có #site-header)
  document.addEventListener("DOMContentLoaded", () => {
    if (!document.getElementById("site-header")) enhanceNav(document);
  });
})();
