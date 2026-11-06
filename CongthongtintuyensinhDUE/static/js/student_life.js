/* sinh-vien.js – trang "Dành cho sinh viên"
   sinh-vien.html#doan-hoi        → Đoàn Thanh niên – Hội Sinh viên
   sinh-vien.html#lcd             → Liên chi đoàn (#lcd-<id> để nhảy tới 1 LCĐ)
   sinh-vien.html#clb             → Câu lạc bộ – Đội – Nhóm
   sinh-vien.html?club=<id>#clb   → mở sẵn chi tiết 1 CLB */
window.DUE.views = window.DUE.views || {};
/* Được router gọi: DUE.views.sv(phần tử, tab, mục con) */
window.DUE.views.sv = function (el, tabArg, subArg) {
  if (el._svRoute) return el._svRoute(tabArg, subArg);       // đã dựng trang → chỉ đổi tab
  const { D, esc, icon, shortName, L } = window.DUE;
  const app = el;
  const facultyName = (id) => D.faculties.find((f) => f.id === id)?.name || "";
  const stripPhones = (s) => String(s || "").replace(/\s*\((?:[^()]*\d{3}[^()]*)\)/g, "");

  /* ---------- Nhóm lĩnh vực CLB ---------- */
  const GROUPS = [
    { key: "hoc-thuat", label: "Học thuật", ic: "menu_book", test: (c) => /^Học thuật/i.test(c) },
    { key: "ky-nang", label: "Kỹ năng & Kinh doanh", ic: "rocket_launch", test: (c) => /Kỹ năng|Kinh doanh|Thương mại/i.test(c) },
    { key: "ngoai-ngu", label: "Ngoại ngữ", ic: "translate", test: (c) => /Ngoại ngữ/i.test(c) },
    { key: "nghe-thuat", label: "Văn nghệ & Âm nhạc", ic: "music_note", test: (c) => /Âm nhạc|Văn nghệ/i.test(c) },
    { key: "the-thao", label: "Thể thao", ic: "sports_martial_arts", test: (c) => /Thể thao/i.test(c) },
    { key: "cong-dong", label: "Truyền thông & Cộng đồng", ic: "campaign", test: (c) => /Truyền thông|Môi trường|xã hội/i.test(c) },
    { key: "khac", label: "Khác", ic: "interests", test: () => true }
  ];
  const groupOf = (c) => GROUPS.find((g) => g.test(c.category || "")) || GROUPS.at(-1);
  const isSchoolLevel = (c) => !c.faculty_id;

  /* ---------- Khung trang ---------- */
  const TABS = [
    { id: "doan-hoi", label: "Đoàn – Hội", ic: "groups" },
    { id: "lcd", label: "Liên chi đoàn", ic: "diversity_3", count: D.lien_chi_doan.length },
    { id: "clb", label: "Câu lạc bộ – Đội – Nhóm", ic: "interests", count: D.clubs.length }
  ];

  app.innerHTML = `
    <div class="relative overflow-hidden bg-primary-container text-on-primary">
      <div class="absolute -right-24 -top-24 w-96 h-96 rounded-full bg-on-primary-container/10"></div>
      <div class="absolute right-56 -bottom-40 w-80 h-80 rounded-full bg-secondary-container/20"></div>
      <div class="relative max-w-7xl mx-auto px-6 lg:px-12 pt-space-xl sm:pt-space-2xl pb-space-xl">
        <nav aria-label="Breadcrumb" class="mb-space-lg">
          <ol class="flex items-center gap-space-xs font-body-sm text-body-sm text-on-primary-container">
            <li><a class="hover:text-on-primary hover:underline underline-offset-4" href="${L.home()}">Trang chủ</a></li>
            <li class="flex items-center gap-space-xs">${icon("chevron_right", "text-[16px]")}<span class="text-on-primary" aria-current="page">Dành cho sinh viên</span></li>
          </ol>
        </nav>
        <p class="font-label-md text-label-md uppercase tracking-widest text-secondary-fixed-dim mb-space-sm">Đời sống sinh viên DUE</p>
        <h1 class="font-headline-lg-mobile text-headline-lg-mobile sm:font-headline-lg sm:text-headline-lg max-w-3xl mb-space-md">Tham gia, kết nối và phát triển bản thân</h1>
        <p class="font-body-lg text-body-lg text-on-primary/80 max-w-2xl">Tìm hiểu Đoàn Thanh niên – Hội Sinh viên, Liên chi đoàn các khoa và các câu lạc bộ, đội, nhóm đang hoạt động tại Trường Đại học Kinh tế – ĐHĐN.</p>
        <div class="grid grid-cols-3 gap-space-md max-w-xl mt-space-xl">
          ${[[D.lien_chi_doan.length, "Liên chi đoàn"], [D.clubs.length, "CLB – Đội – Nhóm"], ["54K+", "Theo dõi fanpage Đoàn"]].map(([n, l]) => `
            <div class="rounded-xl bg-on-primary/10 p-space-md"><p class="font-headline-md text-headline-md text-secondary-fixed-dim">${n}</p><p class="font-label-md text-label-md text-on-primary/80">${l}</p></div>`).join("")}
        </div>
      </div>
      <div class="relative max-w-7xl mx-auto px-6 lg:px-12">
        <div id="sv-tabs" role="tablist" aria-label="Nội dung" class="flex gap-space-xs overflow-x-auto no-scrollbar">
          ${TABS.map((t) => `
            <button role="tab" id="tab-${t.id}" aria-controls="panel-${t.id}" data-tab="${t.id}"
              class="tab-btn shrink-0 inline-flex items-center gap-space-sm px-space-lg py-space-md rounded-t-xl font-label-lg text-label-lg transition-colors">
              ${icon(t.ic, "text-[20px]")}${t.label}${t.count ? `<span class="tab-count px-space-sm rounded-full font-label-sm text-label-sm">${t.count}</span>` : ""}
            </button>`).join("")}
        </div>
      </div>
    </div>
    <div class="max-w-7xl mx-auto px-6 lg:px-12 py-space-xl lg:py-space-2xl">
      ${TABS.map((t) => `<section role="tabpanel" id="panel-${t.id}" aria-labelledby="tab-${t.id}" hidden></section>`).join("")}
    </div>
    <dialog id="club-dialog" class="w-[min(94vw,640px)] max-h-[88vh] rounded-2xl p-0 shadow-2xl"></dialog>`;

  /* ---------- Đoàn – Hội ---------- */
  function renderDoanHoi() {
    const Y = D.doan_hoi, T = Y.doan_thanh_nien, O = Y.office_contact;
    const campaignIcon = (n) => /Tình nguyện|Mùa hè xanh/i.test(n) ? "volunteer_activism" : /Green|xanh/i.test(n) ? "eco" : /5 tốt|tiên tiến|tin tốt/i.test(n) ? "workspace_premium" : /khiêu vũ|Thủ lĩnh|Tài năng|văn hóa|Hội trại/i.test(n) ? "celebration" : "flag";
    document.getElementById("panel-doan-hoi").innerHTML = `
      <div class="grid gap-space-lg lg:grid-cols-3 fade-in">
        <div class="lg:col-span-2 space-y-space-lg">
          <div class="rounded-xl bg-secondary-fixed/60 border border-secondary-fixed-dim/60 p-space-lg sm:p-space-xl">
            <p class="font-label-md text-label-md uppercase text-secondary mb-space-sm">Phương châm hoạt động</p>
            <p class="font-headline-md text-headline-md sm:font-headline-lg sm:text-headline-lg text-on-secondary-fixed-variant">“${esc(T.motto)}”</p>
            <p class="font-body-md text-body-md text-on-surface-variant mt-space-md">${esc(Y.reputation)}</p>
          </div>

          <div class="bg-surface-container-lowest rounded-xl border border-outline-variant/50 p-space-lg sm:p-space-xl">
            <h2 class="font-headline-md text-headline-md text-primary mb-space-lg">Chương trình & phong trào tiêu biểu</h2>
            <div class="grid gap-space-md sm:grid-cols-2">
              ${Y.programs_and_campaigns.map((c) => `
                <div class="flex gap-space-md p-space-md rounded-xl bg-surface-container-low">
                  <span class="shrink-0 w-10 h-10 rounded-lg bg-primary-fixed text-primary-container flex items-center justify-center">${icon(campaignIcon(c.name), "text-[22px]")}</span>
                  <div class="min-w-0">
                    <p class="font-label-lg text-label-lg text-on-surface">${c.url ? `<a target="_blank" rel="noopener" class="hover:text-primary-container hover:underline" href="${esc(c.url)}">${esc(c.name)}</a>` : esc(c.name)}</p>
                    ${c.detail ? `<p class="font-body-sm text-body-sm text-on-surface-variant">${esc(c.detail)}</p>` : ""}
                  </div>
                </div>`).join("")}
            </div>
          </div>

          <div class="bg-surface-container-lowest rounded-xl border border-outline-variant/50 divide-y divide-outline-variant/50">
            ${[["Chức năng", T.functions, "account_tree"], ["Nhiệm vụ", T.tasks, "task_alt"]].map(([t, list, ic]) => `
              <details class="group p-space-lg">
                <summary class="flex items-center justify-between cursor-pointer list-none font-headline-sm text-headline-sm text-primary">
                  <span class="flex items-center gap-space-sm">${icon(ic, "text-primary-container")}${t} của Đoàn trường</span>
                  ${icon("expand_more", "group-open:rotate-180 transition-transform")}
                </summary>
                <ul class="mt-space-md space-y-space-sm">${list.map((x) => `<li class="flex gap-space-sm font-body-md text-body-md text-on-surface-variant">${icon("check_circle", "text-secondary-container text-[20px]")}<span>${esc(x)}</span></li>`).join("")}</ul>
              </details>`).join("")}
          </div>
        </div>

        <aside class="space-y-space-lg">
          <div class="bg-surface-container-lowest rounded-xl border border-outline-variant/50 p-space-lg">
            <h2 class="font-headline-sm text-headline-sm text-primary mb-space-xs">Ban Thường vụ Đoàn trường</h2>
            <p class="font-body-sm text-body-sm text-on-surface-variant mb-space-md">${esc(T.term)} · BCH ${T.executive_committee.bch_members} đồng chí</p>
            <ul class="space-y-space-md">
              ${T.standing_office.map((p) => `<li class="flex gap-space-md">
                <span class="shrink-0 w-10 h-10 rounded-full bg-primary-container text-on-primary flex items-center justify-center">${icon("person", "text-[20px]")}</span>
                <div><p class="font-label-lg text-label-lg">${esc(p.name)}</p><p class="font-body-sm text-body-sm text-on-surface-variant">${esc(p.role)}</p></div></li>`).join("")}
            </ul>
          </div>
          <div class="rounded-xl bg-primary-container text-on-primary p-space-lg">
            <h2 class="font-headline-sm text-headline-sm mb-space-md">Văn phòng Đoàn – Hội</h2>
            <ul class="space-y-space-sm font-body-sm text-body-sm">
              <li class="flex gap-space-sm">${icon("location_on", "text-[20px] text-secondary-fixed-dim")}${esc(O.office)}</li>
              <li class="flex gap-space-sm">${icon("call", "text-[20px] text-secondary-fixed-dim")}<a class="hover:underline" href="tel:02363950358">${esc(O.phone)}</a></li>
              <li class="flex gap-space-sm">${icon("mail", "text-[20px] text-secondary-fixed-dim")}<a class="hover:underline break-all" href="mailto:${esc(O.email_doan)}">${esc(O.email_doan)}</a></li>
              <li class="flex gap-space-sm">${icon("mail", "text-[20px] text-secondary-fixed-dim")}<a class="hover:underline break-all" href="mailto:${esc(O.email_hoi)}">${esc(O.email_hoi)}</a></li>
            </ul>
            <div class="flex flex-wrap gap-space-sm mt-space-lg">
              <a target="_blank" rel="noopener" href="${esc(T.facebook)}" class="inline-flex items-center gap-space-xs px-space-md py-space-sm rounded-full bg-secondary-container text-white font-label-lg text-label-lg hover:bg-secondary">${icon("thumb_up", "text-[18px]")}Fanpage</a>
              <a target="_blank" rel="noopener" href="${esc(T.website)}" class="inline-flex items-center gap-space-xs px-space-md py-space-sm rounded-full border border-on-primary/40 font-label-lg text-label-lg hover:bg-on-primary/10">${icon("language", "text-[18px]")}Website</a>
            </div>
          </div>
          <div class="bg-surface-container-lowest rounded-xl border border-outline-variant/50 p-space-lg">
            <h2 class="font-headline-sm text-headline-sm text-primary mb-space-md">Thành tích qua các nhiệm kỳ</h2>
            <div class="flex flex-wrap gap-space-sm">${Y.achievements_pages.map((a) => `<a target="_blank" rel="noopener" href="${esc(a.url)}" class="px-space-md py-space-xs rounded-full bg-surface-container font-label-md text-label-md text-primary-container hover:bg-primary-fixed">${esc(a.term)}</a>`).join("")}</div>
          </div>
        </aside>
      </div>`;
  }

  /* ---------- Liên chi đoàn ---------- */
  function renderLcd() {
    const social = (c) => [
      c.facebook && [c.facebook, "thumb_up", "Fanpage"], c.instagram && [c.instagram, "photo_camera", "Instagram"],
      c.tiktok && [c.tiktok, "music_video", "TikTok"], c.email && ["mailto:" + c.email, "mail", "Email"]
    ].filter(Boolean);
    document.getElementById("panel-lcd").innerHTML = `
      <div class="flex flex-col sm:flex-row sm:items-end justify-between gap-space-md mb-space-lg">
        <div>
          <h2 class="font-headline-md text-headline-md text-primary">Liên chi đoàn các khoa</h2>
          <p class="font-body-md text-body-md text-on-surface-variant">Mỗi khoa có một Liên chi đoàn trực thuộc Đoàn trường, tổ chức hoạt động học thuật, tình nguyện, văn hóa cho sinh viên khoa.</p>
        </div>
      </div>
      <div class="grid gap-space-lg md:grid-cols-2 fade-in">
        ${D.lien_chi_doan.map((l) => {
          const s = social(l.contact);
          return `
          <article id="lcd-${l.id}" class="flex flex-col bg-surface-container-lowest rounded-xl border border-outline-variant/50 p-space-lg hover:shadow-[0_8px_28px_rgba(0,30,64,0.10)] transition-shadow">
            <div class="flex items-start gap-space-md mb-space-md">
              <span class="shrink-0 w-12 h-12 rounded-xl bg-primary-container text-on-primary flex items-center justify-center">${icon("diversity_3", "text-[24px]")}</span>
              <div class="min-w-0">
                <h3 class="font-headline-sm text-headline-sm text-primary">${esc(l.name.replace(/\s*\(.*?\)\s*$/, ""))}</h3>
                <a href="${L.khoa(l.faculty_id)}" class="font-body-sm text-body-sm text-primary-container hover:underline">${esc(facultyName(l.faculty_id))}</a>
              </div>
            </div>
            <dl class="grid grid-cols-2 gap-space-sm mb-space-md">
              <div class="rounded-lg bg-surface-container-low p-space-sm"><dt class="font-label-sm text-label-sm uppercase text-on-surface-variant">Bí thư</dt><dd class="font-label-lg text-label-lg">${esc(l.secretary || "Đang cập nhật")}</dd></div>
              <div class="rounded-lg bg-surface-container-low p-space-sm"><dt class="font-label-sm text-label-sm uppercase text-on-surface-variant">Nhiệm kỳ</dt><dd class="font-label-lg text-label-lg">${esc(l.term ? l.term.split(" ")[0] : "Đang cập nhật")}</dd></div>
            </dl>
            ${l.activities.length ? `<p class="font-label-md text-label-md uppercase text-on-surface-variant mb-space-sm">Hoạt động tiêu biểu</p>
              <ul class="space-y-space-xs mb-space-md">${l.activities.slice(0, 4).map((a) => `<li class="flex gap-space-sm font-body-sm text-body-sm">${icon("arrow_right", "text-secondary-container text-[20px]")}<span>${esc(a)}</span></li>`).join("")}</ul>` : `<p class="font-body-sm text-body-sm text-on-surface-variant mb-space-md">Thông tin hoạt động đang được cập nhật.</p>`}
            <div class="mt-auto flex flex-wrap gap-space-sm pt-space-md border-t border-outline-variant/50">
              ${s.map(([h, ic, t]) => `<a ${h.startsWith("mailto") ? "" : 'target="_blank" rel="noopener"'} href="${esc(h)}" class="inline-flex items-center gap-space-xs px-space-md py-space-xs rounded-full bg-surface-container text-primary-container font-label-md text-label-md hover:bg-primary-fixed">${icon(ic, "text-[16px]")}${t}</a>`).join("")}
              ${l.pages[0] ? `<a target="_blank" rel="noopener" href="${esc(l.pages[0])}" class="inline-flex items-center gap-space-xs px-space-md py-space-xs rounded-full bg-surface-container text-primary-container font-label-md text-label-md hover:bg-primary-fixed">${icon("open_in_new", "text-[16px]")}Trang LCĐ</a>` : ""}
              <a href="${L.khoa(l.faculty_id, "sinh-vien")}" class="inline-flex items-center gap-space-xs px-space-md py-space-xs rounded-full bg-secondary-container text-white font-label-md text-label-md hover:bg-secondary ml-auto">${icon("school", "text-[16px]")}Về khoa</a>
            </div>
          </article>`;
        }).join("")}
      </div>`;
  }

  /* ---------- Câu lạc bộ ---------- */
  const state = { q: "", group: "all", level: "all" };

  function renderClbShell() {
    const used = GROUPS.filter((g) => D.clubs.some((c) => groupOf(c) === g));
    const chip = (key, label, ic) => `<button type="button" data-group="${key}" aria-pressed="false"
      class="grp-chip shrink-0 inline-flex items-center gap-space-xs px-space-md py-space-sm rounded-full border font-label-lg text-label-lg transition-colors">${ic ? icon(ic, "text-[18px]") : ""}${label}</button>`;
    document.getElementById("panel-clb").innerHTML = `
      <div class="flex flex-col lg:flex-row lg:items-end justify-between gap-space-md mb-space-lg">
        <div>
          <h2 class="font-headline-md text-headline-md text-primary">Câu lạc bộ – Đội – Nhóm</h2>
          <p class="font-body-md text-body-md text-on-surface-variant">Chọn lĩnh vực bạn quan tâm hoặc tìm theo tên.</p>
        </div>
        <div class="flex flex-col sm:flex-row gap-space-sm">
          <label class="relative">
            <span class="sr-only">Tìm câu lạc bộ</span>
            ${icon("search", "absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant text-[20px]")}
            <input id="clb-search" type="search" placeholder="Tìm CLB, lĩnh vực…" class="w-full sm:w-72 pl-10 pr-4 py-2 rounded-full border border-outline-variant bg-surface-container-lowest font-body-sm text-body-sm focus:border-primary-container focus:ring-primary-container">
          </label>
          <select id="clb-level" class="rounded-full border border-outline-variant bg-surface-container-lowest font-body-sm text-body-sm py-2 pl-4 pr-10">
            <option value="all">Tất cả cấp</option><option value="truong">Cấp trường</option><option value="khoa">Cấp khoa</option>
          </select>
        </div>
      </div>
      <div class="flex gap-space-sm overflow-x-auto no-scrollbar pb-space-sm mb-space-lg" role="group" aria-label="Lọc theo lĩnh vực">
        ${chip("all", "Tất cả", "apps")}${used.map((g) => chip(g.key, g.label, g.ic)).join("")}
      </div>
      <p id="clb-count" class="font-body-sm text-body-sm text-on-surface-variant mb-space-md" aria-live="polite"></p>
      <div id="clb-grid" class="grid gap-space-lg sm:grid-cols-2 lg:grid-cols-3"></div>
      <div class="mt-space-2xl rounded-2xl bg-primary-container text-on-primary p-space-lg sm:p-space-xl">
        <p class="font-label-md text-label-md uppercase tracking-widest text-secondary-fixed-dim mb-space-sm">Không chỉ có CLB</p>
        <h3 class="font-headline-md text-headline-md mb-space-lg">Hoạt động thường niên của sinh viên DUE</h3>
        <div class="grid gap-space-md sm:grid-cols-2 lg:grid-cols-3">
          ${[["volunteer_activism", "Tình nguyện Đông", "Chiến dịch tình nguyện mùa đông của Đoàn – Hội"],
             ["wb_sunny", "Chiến dịch Mùa hè xanh", "Tình nguyện hè tại các địa phương"],
             ["nightlife", "Khiêu vũ Lovely Night", "Đêm khiêu vũ thường niên của sinh viên"],
             ["military_tech", "Thủ lĩnh sinh viên", "Cuộc thi tìm kiếm thủ lĩnh sinh viên"],
             ["star", "Sinh viên Tài năng – Thanh lịch", "Cuộc thi tài năng và phong cách sinh viên"],
             ["sports_soccer", "Giải thể thao", "Các giải thể thao cấp trường và cấp khoa"]].map(([ic, t, d]) => `
            <div class="flex gap-space-md rounded-xl bg-on-primary/10 p-space-md">
              <span class="shrink-0 w-10 h-10 rounded-lg bg-secondary-container text-white flex items-center justify-center">${icon(ic, "text-[22px]")}</span>
              <div><p class="font-label-lg text-label-lg">${t}</p><p class="font-body-sm text-body-sm text-on-primary/75">${d}</p></div>
            </div>`).join("")}
        </div>
        <p class="mt-space-lg font-body-sm text-body-sm text-on-primary/70">Nguồn: mục “Câu lạc bộ” – Cổng tư vấn tuyển sinh 2026 của Trường Đại học Kinh tế.</p>
      </div>`;

    document.getElementById("clb-search").addEventListener("input", (e) => { state.q = e.target.value.trim().toLowerCase(); renderClubs(); });
    document.getElementById("clb-level").addEventListener("change", (e) => { state.level = e.target.value; renderClubs(); });
    document.querySelectorAll(".grp-chip").forEach((b) => b.addEventListener("click", () => { state.group = b.dataset.group; renderClubs(); }));
    renderClubs();
  }

  const norm = (s) => String(s || "").toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/đ/g, "d");

  function renderClubs() {
    document.querySelectorAll(".grp-chip").forEach((b) => {
      const on = b.dataset.group === state.group;
      b.setAttribute("aria-pressed", on);
      b.className = b.className.replace(/\b(bg-primary-container|text-on-primary|border-primary-container|bg-surface-container-lowest|text-on-surface-variant|border-outline-variant|hover:border-primary-container)\b/g, "").trim() + " " +
        (on ? "bg-primary-container text-on-primary border-primary-container" : "bg-surface-container-lowest text-on-surface-variant border-outline-variant hover:border-primary-container");
    });
    const q = norm(state.q);
    const list = D.clubs.filter((c) =>
      (state.group === "all" || groupOf(c).key === state.group) &&
      (state.level === "all" || (state.level === "truong") === isSchoolLevel(c)) &&
      (!q || norm([c.name, c.category, c.description, c.slogan, facultyName(c.faculty_id)].join(" ")).includes(q)));
    document.getElementById("clb-count").textContent = `Hiển thị ${list.length}/${D.clubs.length} câu lạc bộ, đội, nhóm`;
    const grid = document.getElementById("clb-grid");
    if (!list.length) {
      grid.innerHTML = `<div class="col-span-full text-center py-space-2xl">${icon("search_off", "text-[40px] text-on-surface-variant")}<p class="mt-space-sm text-on-surface-variant">Không tìm thấy CLB phù hợp. Thử từ khóa khác nhé.</p></div>`;
      return;
    }
    grid.innerHTML = list.map((c) => {
      const g = groupOf(c);
      return `
      <article class="group flex flex-col bg-surface-container-lowest rounded-xl border border-outline-variant/50 overflow-hidden hover:shadow-[0_8px_28px_rgba(0,30,64,0.12)] hover:-translate-y-0.5 transition-all fade-in">
        ${c.cover ? `<div class="aspect-[21/8] bg-surface-container overflow-hidden"><img src="${esc(c.cover)}" alt="Ảnh bìa ${esc(c.name)}" loading="lazy" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"></div>` : `<div class="h-2 bg-gradient-to-r from-primary-container to-secondary-container"></div>`}
        <div class="flex flex-col flex-1 p-space-lg">
          <div class="flex items-start gap-space-md mb-space-md">
            ${c.logo ? `<img src="${esc(c.logo)}" alt="Logo ${esc(c.name)}" loading="lazy" class="shrink-0 w-14 h-14 rounded-xl object-cover ring-1 ring-outline-variant/60 ${c.cover ? "-mt-space-xl ring-4 ring-surface-container-lowest" : ""}">` : `<span class="shrink-0 w-12 h-12 rounded-xl bg-primary-fixed text-primary-container flex items-center justify-center">${icon(g.ic, "text-[24px]")}</span>`}
            <div class="min-w-0">
              <h3 class="font-headline-sm text-headline-sm text-primary leading-tight">${esc(c.name)}</h3>
              <p class="font-label-md text-label-md text-on-surface-variant mt-space-xs">${isSchoolLevel(c) ? "Cấp trường" : esc(shortName(facultyName(c.faculty_id)))}</p>
            </div>
          </div>
          <div class="flex flex-wrap gap-space-xs mb-space-md">
            <span class="px-space-sm py-0.5 rounded-full bg-secondary-fixed text-on-secondary-fixed-variant font-label-sm text-label-sm">${esc(g.label)}</span>
            ${c.founded ? `<span class="px-space-sm py-0.5 rounded-full bg-surface-container font-label-sm text-label-sm text-on-surface-variant">Từ ${c.founded.slice(0, 4)}</span>` : ""}
            ${c.recruitment ? `<span class="px-space-sm py-0.5 rounded-full bg-tertiary-fixed text-on-tertiary-fixed-variant font-label-sm text-label-sm">Có lịch tuyển TV</span>` : ""}
          </div>
          <p class="font-body-sm text-body-sm text-on-surface-variant line-clamp-3 mb-space-md">${esc(c.intro || c.description || c.category || "Thông tin đang được cập nhật.")}</p>
          <div class="mt-auto flex items-center justify-between gap-space-sm pt-space-md border-t border-outline-variant/50">
            <span class="inline-flex items-center gap-space-xs font-label-md text-label-md text-on-surface-variant">${c.followers ? `${icon("group", "text-[18px]")}${esc(c.followers)} theo dõi` : ""}</span>
            <button type="button" data-club="${c.id}" class="inline-flex items-center gap-space-xs px-space-md py-space-xs rounded-full bg-secondary-container text-white font-label-md text-label-md hover:bg-secondary">
              Chi tiết ${icon("arrow_forward", "text-[16px]")}
            </button>
          </div>
        </div>
      </article>`;
    }).join("");
    grid.querySelectorAll("[data-club]").forEach((b) => b.addEventListener("click", () => openClub(b.dataset.club)));
  }

  function openClub(id) {
    const c = D.clubs.find((x) => x.id === id);
    if (!c) return;
    const g = groupOf(c), dlg = document.getElementById("club-dialog"), k = c.contact || {};
    const row = (ic, label, val) => val ? `<div class="flex gap-space-md"><span class="shrink-0 w-9 h-9 rounded-lg bg-surface-container text-primary-container flex items-center justify-center">${icon(ic, "text-[20px]")}</span><div class="min-w-0"><p class="font-label-sm text-label-sm uppercase text-on-surface-variant">${label}</p><div class="font-body-sm text-body-sm text-on-surface">${val}</div></div></div>` : "";
    dlg.innerHTML = `
      <div class="relative bg-primary-container text-on-primary p-space-lg sm:p-space-xl overflow-hidden">
        ${c.cover ? `<img src="${esc(c.cover)}" alt="" class="absolute inset-0 w-full h-full object-cover opacity-35"><div class="absolute inset-0 bg-gradient-to-t from-primary-container via-primary-container/70 to-primary-container/20"></div>` : ""}
        <div class="relative">
        <button type="button" data-close aria-label="Đóng" class="absolute top-space-md right-space-md w-9 h-9 rounded-full hover:bg-on-primary/10 flex items-center justify-center">${icon("close")}</button>
        ${c.logo ? `<img src="${esc(c.logo)}" alt="Logo ${esc(c.name)}" class="w-16 h-16 rounded-xl object-cover ring-2 ring-on-primary/40 mb-space-md">` : `<span class="inline-flex w-12 h-12 rounded-xl bg-on-primary/10 items-center justify-center mb-space-md">${icon(g.ic, "text-[26px] text-secondary-fixed-dim")}</span>`}
        <h2 class="font-headline-md text-headline-md pr-space-xl">${esc(c.name)}</h2>
        <p class="font-body-sm text-body-sm text-on-primary/80 mt-space-xs">${esc(g.label)} · ${isSchoolLevel(c) ? "Cấp trường" : esc(facultyName(c.faculty_id))}${c.founded ? ` · Thành lập ${c.founded.split("-").reverse().join("/")}` : ""}</p>
        ${c.slogan ? `<p class="mt-space-md font-headline-sm text-headline-sm text-secondary-fixed-dim">“${esc(c.slogan)}”</p>` : ""}
        </div>
      </div>
      <div class="p-space-lg sm:p-space-xl space-y-space-lg overflow-y-auto">
        ${(c.intro || c.description) ? `<p class="font-body-md text-body-md text-on-surface">${esc(c.intro || c.description)}</p>` : ""}
        ${c.highlights?.length ? `<div><p class="font-label-lg text-label-lg text-primary mb-space-sm">Hoạt động nổi bật</p><ul class="space-y-space-xs">${c.highlights.map((h) => `<li class="flex gap-space-sm font-body-sm text-body-sm">${icon("check_circle", "text-secondary-container text-[18px]")}<span>${esc(h)}</span></li>`).join("")}</ul></div>` : ""}
        ${c.recent_activities?.length ? `<div><p class="font-label-lg text-label-lg text-primary mb-space-sm">Gần đây</p><ul class="space-y-space-xs">${c.recent_activities.map((h) => `<li class="flex gap-space-sm font-body-sm text-body-sm text-on-surface-variant">${icon("event", "text-primary-container text-[18px]")}<span>${esc(h)}</span></li>`).join("")}</ul></div>` : ""}
        ${c.recruitment ? `<div class="rounded-xl bg-tertiary-fixed/60 p-space-md flex gap-space-sm">${icon("how_to_reg", "text-on-tertiary-fixed-variant")}<div><p class="font-label-lg text-label-lg text-on-tertiary-fixed-variant">Tuyển thành viên</p><p class="font-body-sm text-body-sm">${esc(c.recruitment)}</p></div></div>` : ""}
        ${c.achievements?.length ? `<div class="rounded-xl bg-secondary-fixed/50 p-space-md flex gap-space-sm">${icon("emoji_events", "text-secondary")}<div><p class="font-label-lg text-label-lg text-secondary">Thành tích</p><ul class="font-body-sm text-body-sm">${c.achievements.map((a) => `<li>${esc(a)}</li>`).join("")}</ul></div></div>` : ""}
        <div class="grid gap-space-md sm:grid-cols-2">
          ${row("badge", "Ban điều hành", c.leaders && esc(stripPhones(c.leaders)))}
          ${row("school", "Cố vấn", c.advisors && esc(c.advisors))}
          ${row("mail", "Email", k.email && `<a class="text-primary-container hover:underline break-all" href="mailto:${esc(k.email)}">${esc(k.email)}</a>`)}
          ${row("call", "Hotline", k.phone && esc(k.phone))}
          ${row("group", "Người theo dõi", c.followers && esc(c.followers))}
          ${row("language", "Website", k.website && `<a target="_blank" rel="noopener" class="text-primary-container hover:underline break-all" href="${esc(k.website.startsWith("http") ? k.website : "https://" + k.website)}">${esc(k.website.replace(/^https?:\/\//, ""))}</a>`)}
        </div>
        <div class="flex flex-wrap gap-space-sm pt-space-md border-t border-outline-variant/60">
          ${k.facebook ? `<a target="_blank" rel="noopener" href="${esc(k.facebook)}" class="inline-flex items-center gap-space-xs px-space-lg py-space-sm rounded-full bg-secondary-container text-white font-label-lg text-label-lg hover:bg-secondary">${icon("thumb_up", "text-[18px]")}Theo dõi fanpage</a>` : ""}
          ${(k.other_links || []).map((u) => `<a target="_blank" rel="noopener" href="${esc(u)}" class="inline-flex items-center gap-space-xs px-space-md py-space-sm rounded-full bg-surface-container text-primary-container font-label-md text-label-md hover:bg-primary-fixed">${icon("link", "text-[16px]")}${esc(u.replace(/^https?:\/\/(www\.)?/, "").split("?")[0])}</a>`).join("")}
          ${c.faculty_id ? `<a href="${L.khoa(c.faculty_id)}" class="inline-flex items-center gap-space-xs px-space-md py-space-sm rounded-full bg-surface-container text-primary-container font-label-md text-label-md hover:bg-primary-fixed">${icon("school", "text-[16px]")}Xem khoa</a>` : ""}
        </div>
      </div>`;
    dlg.querySelector("[data-close]").addEventListener("click", () => dlg.close());
    dlg.showModal();
    setHash(L.sv("clb", id));
  }
  const dlg = document.getElementById("club-dialog");
  dlg.addEventListener("click", (e) => { if (e.target === dlg) dlg.close(); });
  dlg.addEventListener("close", () => setHash(L.sv("clb")));

  /* ---------- Điều hướng tab ---------- */
  function showTab(id, push = true) {
    TABS.forEach((t) => {
      const on = t.id === id, b = document.getElementById("tab-" + t.id);
      b.setAttribute("aria-selected", on);
      b.tabIndex = on ? 0 : -1;
      b.className = b.className.replace(/\b(bg-surface|text-primary|bg-on-primary\/10|text-on-primary|hover:bg-on-primary\/20)\b/g, "").trim() + " " +
        (on ? "bg-surface text-primary" : "bg-on-primary/10 text-on-primary hover:bg-on-primary/20");
      const cnt = b.querySelector(".tab-count");
      if (cnt) cnt.className = "tab-count px-space-sm rounded-full font-label-sm text-label-sm " + (on ? "bg-secondary-container text-white" : "bg-on-primary/15");
      document.getElementById("panel-" + t.id).hidden = !on;
      if (on) { const bar = document.getElementById("sv-tabs"); bar.scrollLeft = b.offsetLeft - 24; }
    });
    if (push) setHash(L.sv(id));
  }
  document.querySelectorAll(".tab-btn").forEach((b) => {
    b.addEventListener("click", () => showTab(b.dataset.tab));
    b.addEventListener("keydown", (e) => {
      const i = TABS.findIndex((t) => t.id === b.dataset.tab);
      const n = e.key === "ArrowRight" ? 1 : e.key === "ArrowLeft" ? -1 : 0;
      if (!n) return;
      const next = TABS[(i + n + TABS.length) % TABS.length].id;
      showTab(next); document.getElementById("tab-" + next).focus();
    });
  });

  function setHash(h) {
    try { if (h.startsWith("#")) history.replaceState(null, "", h); } catch (_) { /* môi trường xem trước có thể chặn */ }
  }

  function routeTo(tab, sub) {
    const explicit = !!tab;
    tab = TABS.some((t) => t.id === tab) ? tab : "doan-hoi";
    showTab(tab, false);
    if (tab === "lcd" && sub) {
      const card = document.getElementById("lcd-" + sub);
      if (card) {
        card.scrollIntoView({ block: "center" });
        card.classList.add("ring-2", "ring-secondary-container");
        setTimeout(() => card.classList.remove("ring-2", "ring-secondary-container"), 2500);
      }
    } else if (explicit) document.getElementById("sv-tabs").scrollIntoView();
    else window.scrollTo(0, 0);
    if (tab === "clb" && sub) { if (!dlg.open) openClub(sub); }
    else if (dlg.open) dlg.close();
  }

  renderDoanHoi(); renderLcd(); renderClbShell();
  el._svRoute = routeTo;
  routeTo(tabArg, subArg);
};
