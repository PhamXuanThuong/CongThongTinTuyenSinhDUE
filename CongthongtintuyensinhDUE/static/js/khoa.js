/* khoa.js – trang Khoa
   khoa.html            → danh sách tất cả các khoa
   khoa.html?id=ketoan  → chi tiết một khoa */
(function () {
  const { D, esc, icon, shortName, FACULTY_ICONS, L } = window.DUE;
  let app;

  const LINK_LABELS = {
    intro: "Giới thiệu", history: "Lịch sử hình thành", vision_mission: "Tầm nhìn – Sứ mệnh", mission_vision: "Sứ mệnh – Tầm nhìn",
    staff: "Đội ngũ giảng viên", programs: "Chương trình đào tạo", majors: "Các chuyên ngành", student_life: "Đời sống sinh viên",
    student_activities: "Hoạt động sinh viên", scholarships: "Học bổng", scholarships_internships: "Học bổng – Thực tập",
    internship_career: "Thực tập – Việc làm", career: "Cơ hội nghề nghiệp", news: "Tin tức", clubs_and_youth_union: "CLB & Liên chi đoàn",
    education_philosophy: "Triết lý giáo dục", admissions_info: "Thông tin tuyển sinh", facilities: "Cơ sở vật chất"
  };
  const TYPE_STYLE = {
    "Tiêu chuẩn": "bg-surface-container-high text-on-primary-fixed-variant",
    "Bán phần tiếng Anh": "bg-tertiary-fixed text-on-tertiary-fixed-variant",
    "Toàn phần tiếng Anh": "bg-secondary-fixed text-on-secondary-fixed-variant"
  };

  const section = (id, title, ic, body) => `
    <section id="${id}" class="bg-surface-container-lowest rounded-xl border border-outline-variant/50 p-space-lg sm:p-space-xl shadow-[0_1px_3px_rgba(0,30,64,0.04)] fade-in">
      <h2 class="flex items-center gap-space-sm font-headline-md text-headline-md text-primary mb-space-lg">
        <span class="w-9 h-9 rounded-lg bg-primary-fixed text-primary-container flex items-center justify-center">${icon(ic, "text-[20px]")}</span>
        ${title}
      </h2>
      ${body}
    </section>`;

  const btn = (href, label, ic, variant = "primary", external = false) => {
    const styles = {
      primary: "bg-secondary-container text-white hover:bg-secondary",
      outline: "border border-on-primary/40 text-on-primary hover:bg-on-primary/10",
      tonal: "bg-surface-container text-primary-container hover:bg-surface-container-high"
    };
    return `<a href="${esc(href)}" ${external ? 'target="_blank" rel="noopener"' : ""}
      class="inline-flex items-center gap-space-sm px-space-lg py-space-sm rounded-full font-label-lg text-label-lg transition-colors ${styles[variant]}">
      ${icon(ic, "text-[18px]")}${label}</a>`;
  };

  /* ---------- Danh sách khoa ---------- */
  function renderIndex() {
    document.title = "Các khoa - Cổng thông tin tuyển sinh DUE";
    const cards = D.faculties.map((f) => {
      const majors = D.majors.filter((m) => m.faculty_id === f.id);
      return `
      <a href="${L.khoa(f.id)}" class="group flex flex-col bg-surface-container-lowest rounded-xl border border-outline-variant/50 p-space-lg hover:border-primary-container hover:shadow-[0_8px_28px_rgba(0,30,64,0.12)] hover:-translate-y-0.5 transition-all">
        <span class="w-12 h-12 rounded-xl bg-primary-fixed text-primary-container flex items-center justify-center mb-space-md group-hover:bg-primary-container group-hover:text-on-primary transition-colors">
          ${icon(FACULTY_ICONS[f.id] || "school", "text-[26px]")}
        </span>
        <h3 class="font-headline-sm text-headline-sm text-primary mb-space-xs">${esc(f.name)}</h3>
        <p class="font-body-sm text-body-sm text-on-surface-variant mb-space-md">
          ${f.type === "institute" ? "Cử nhân liên kết quốc tế, chương trình năm cuối" : majors.map((m) => esc(m.name)).join(" · ") || "Đang cập nhật"}
        </p>
        <span class="mt-auto inline-flex items-center gap-space-xs font-label-lg text-label-lg text-secondary">
          Xem chi tiết ${icon("arrow_forward", "text-[18px] group-hover:translate-x-1 transition-transform")}
        </span>
      </a>`;
    }).join("");

    app.innerHTML = `
      ${hero({
        crumbs: [["Trang chủ", L.home()], ["Khoa", null]],
        eyebrow: "Đào tạo", title: "Các khoa đào tạo",
        lead: "8 khoa và Viện Đào tạo quốc tế với 19 ngành tuyển sinh năm 2026. Chọn một khoa để xem ngành học, đội ngũ, hoạt động sinh viên và thông tin liên hệ."
      })}
      <div class="max-w-7xl mx-auto px-6 lg:px-12 py-space-2xl">
        <div class="grid gap-space-lg sm:grid-cols-2 lg:grid-cols-3">${cards}</div>
      </div>`;
  }

  function hero({ crumbs, eyebrow, title, lead, chips = [], actions = "", ic }) {
    return `
    <div class="relative overflow-hidden bg-primary-container text-on-primary">
      <div class="absolute -right-24 -top-24 w-96 h-96 rounded-full bg-on-primary-container/10"></div>
      <div class="absolute right-40 -bottom-32 w-72 h-72 rounded-full bg-secondary-container/20"></div>
      <div class="relative max-w-7xl mx-auto px-6 lg:px-12 py-space-xl sm:py-space-2xl">
        <nav aria-label="Breadcrumb" class="mb-space-lg">
          <ol class="flex flex-wrap items-center gap-space-xs font-body-sm text-body-sm text-on-primary-container">
            ${crumbs.map(([t, h], i) => `<li class="flex items-center gap-space-xs">${i ? icon("chevron_right", "text-[16px]") : ""}${h ? `<a class="hover:text-on-primary underline-offset-4 hover:underline" href="${h}">${t}</a>` : `<span class="text-on-primary" aria-current="page">${esc(t)}</span>`}</li>`).join("")}
          </ol>
        </nav>
        <div class="flex items-start gap-space-lg">
          ${ic ? `<span class="hidden sm:flex shrink-0 w-16 h-16 rounded-2xl bg-on-primary/10 items-center justify-center">${icon(ic, "text-[34px] text-secondary-fixed-dim")}</span>` : ""}
          <div class="max-w-3xl">
            <p class="font-label-md text-label-md uppercase tracking-widest text-secondary-fixed-dim mb-space-sm">${eyebrow}</p>
            <h1 class="font-headline-lg-mobile text-headline-lg-mobile sm:font-headline-lg sm:text-headline-lg mb-space-md">${esc(title)}</h1>
            <p class="font-body-lg text-body-lg text-on-primary/80">${lead}</p>
            ${chips.length ? `<div class="flex flex-wrap gap-space-sm mt-space-lg">${chips.map((c) => `<span class="px-space-md py-space-xs rounded-full bg-on-primary/10 font-label-md text-label-md">${esc(c)}</span>`).join("")}</div>` : ""}
            ${actions ? `<div class="flex flex-wrap gap-space-md mt-space-lg">${actions}</div>` : ""}
          </div>
        </div>
      </div>
    </div>`;
  }

  /* ---------- Chi tiết khoa ---------- */
  function renderFaculty(f) {
    document.title = `${f.name} - Cổng thông tin tuyển sinh DUE`;
    const majors = D.majors.filter((m) => m.faculty_id === f.id);
    const lcds = D.lien_chi_doan.filter((l) => l.faculty_id === f.id);
    const clubs = D.clubs.filter((c) => c.faculty_id === f.id);
    const specCount = majors.reduce((n, m) => n + Math.max(1, m.specializations.length), 0);
    const LD = f.leadership, C = f.contact;

    const stats = [
      [majors.length, "Ngành tuyển sinh"], [specCount, "Chuyên ngành"],
      [f.departments.length || "—", "Bộ môn"], [lcds.length + clubs.length, "LCĐ & CLB"]
    ];

    /* Mục lục bên trái */
    const toc = [["gioi-thieu", "Giới thiệu", "info"], ["nganh-hoc", "Ngành & chuyên ngành", "school"],
      ["lanh-dao", "Lãnh đạo & bộ môn", "badge"], ["sinh-vien", "Hoạt động sinh viên", "diversity_3"], ["lien-he", "Liên hệ", "call"]];

    /* Giới thiệu */
    const introParts = [
      f.history && `<p class="font-body-md text-body-md text-on-surface-variant">${esc(f.history)}</p>`,
      f.mission && `<blockquote class="border-l-4 border-secondary-container pl-space-md font-body-lg text-body-lg text-on-surface italic">${esc(f.mission)}</blockquote>`,
      f.staff_summary && `<div class="flex items-start gap-space-sm p-space-md rounded-lg bg-surface-container-low">${icon("groups", "text-primary-container")}<p class="font-body-sm text-body-sm"><b>Đội ngũ:</b> ${esc(f.staff_summary)}</p></div>`,
      LD.dean_message_summary && `<div class="p-space-md rounded-lg bg-secondary-fixed/50"><p class="font-label-md text-label-md text-secondary uppercase mb-space-xs">Thông điệp Trưởng khoa</p><p class="font-body-sm text-body-sm">${esc(LD.dean_message_summary)}</p></div>`,
      f.achievements.length && `<div><h3 class="font-headline-sm text-headline-sm text-primary mb-space-sm">Điểm nổi bật</h3><ul class="space-y-space-sm">${f.achievements.map((a) => `<li class="flex gap-space-sm font-body-sm text-body-sm">${icon("verified", "text-secondary-container text-[20px] icon-fill")}<span>${esc(a)}</span></li>`).join("")}</ul></div>`,
      f.career_paths.length && `<div><h3 class="font-headline-sm text-headline-sm text-primary mb-space-sm">Cơ hội việc làm</h3><div class="flex flex-wrap gap-space-sm">${f.career_paths.map((c) => `<span class="px-space-md py-space-xs rounded-full bg-surface-container font-label-md text-label-md text-on-surface-variant">${esc(c)}</span>`).join("")}</div></div>`,
      f.notable_activities.length && `<div><h3 class="font-headline-sm text-headline-sm text-primary mb-space-sm">Hoạt động tiêu biểu</h3><ul class="list-disc pl-space-lg font-body-sm text-body-sm space-y-space-xs">${f.notable_activities.map((a) => `<li>${esc(a)}</li>`).join("")}</ul></div>`
    ].filter(Boolean);
    const intro = introParts.length ? `<div class="space-y-space-lg">${introParts.join("")}</div>`
      : `<p class="font-body-md text-on-surface-variant">Thông tin giới thiệu đang được cập nhật. Xem thêm tại <a class="text-primary-container underline" target="_blank" rel="noopener" href="${esc(f.url)}">trang chính thức của khoa</a>.</p>`;

    /* Ngành học */
    let majorsBody;
    if (majors.length) {
      majorsBody = `
        <div class="flex flex-wrap gap-space-md mb-space-lg font-label-md text-label-md">
          ${Object.entries(TYPE_STYLE).map(([t, c]) => `<span class="inline-flex items-center gap-space-xs"><span class="w-3 h-3 rounded-full ${c.split(" ")[0]}"></span>${t}</span>`).join("")}
        </div>
        <div class="grid gap-space-md md:grid-cols-2">
          ${majors.map((m) => `
            <article class="rounded-xl border border-outline-variant/60 p-space-lg hover:border-primary-container transition-colors">
              <div class="flex items-start justify-between gap-space-sm mb-space-md">
                <h3 class="font-headline-sm text-headline-sm text-primary">${esc(m.name)}</h3>
                ${m.ownership_confirmed ? "" : `<span title="Đang xác nhận khoa quản lý" class="shrink-0 px-space-sm py-0.5 rounded-full bg-surface-container font-label-sm text-label-sm text-on-surface-variant">Đang cập nhật</span>`}
              </div>
              ${m.specializations.length ? `<ul class="space-y-space-md">${m.specializations.map((s) => `
                <li>
                  <p class="font-label-lg text-label-lg text-on-surface mb-space-xs">${esc(s.name)}</p>
                  <div class="flex flex-wrap gap-space-xs">${(s.program_types || []).map((t) => `<span class="px-space-sm py-0.5 rounded-full font-label-sm text-label-sm ${TYPE_STYLE[t] || "bg-surface-container"}">${esc(t)}</span>`).join("")}</div>
                </li>`).join("")}</ul>` : `<p class="font-body-sm text-body-sm text-on-surface-variant">Đào tạo theo ngành, không chia chuyên ngành trên cổng tuyển sinh.</p>`}
            </article>`).join("")}
        </div>
        <p class="mt-space-lg font-body-sm text-body-sm text-on-surface-variant">Nguồn: Cổng tư vấn tuyển sinh 2026. Chỉ tiêu, tổ hợp và học phí xem tại
          <a class="text-primary-container underline" target="_blank" rel="noopener" href="https://due.udn.vn/vi-vn/tuvantuyensinh2026/">trang tuyển sinh chính thức</a>.</p>`;
    } else if (f.special_programs.length) {
      majorsBody = `<div class="grid gap-space-md md:grid-cols-2">${f.special_programs.map((p) => `
        <a target="_blank" rel="noopener" href="${esc(p.url)}" class="flex items-center justify-between gap-space-md rounded-xl border border-outline-variant/60 p-space-lg hover:border-primary-container">
          <span class="font-headline-sm text-headline-sm text-primary">${esc(p.name)}</span>${icon("open_in_new", "text-primary-container")}
        </a>`).join("")}</div>`;
    } else {
      majorsBody = `<p class="text-on-surface-variant">Đang cập nhật.</p>`;
    }
    const pg = f.postgraduate, pgList = [...pg.masters.map((x) => "Thạc sĩ: " + x), ...pg.doctoral.map((x) => "Tiến sĩ: " + x), ...pg.other];
    if (pgList.length) majorsBody += `
      <div class="mt-space-lg pt-space-lg border-t border-outline-variant/60">
        <h3 class="font-headline-sm text-headline-sm text-primary mb-space-sm">Đào tạo sau đại học</h3>
        <div class="flex flex-wrap gap-space-sm">${pgList.map((x) => `<span class="px-space-md py-space-xs rounded-full bg-surface-container font-label-md text-label-md">${esc(x)}</span>`).join("")}</div>
      </div>`;

    /* Lãnh đạo – chỉ hiển thị email công vụ, không hiển thị số di động cá nhân */
    const personCard = (p, role) => `
      <div class="flex items-start gap-space-md p-space-md rounded-xl bg-surface-container-low">
        <span class="shrink-0 w-11 h-11 rounded-full bg-primary-container text-on-primary flex items-center justify-center">${icon("person", "text-[22px]")}</span>
        <div class="min-w-0">
          <p class="font-label-md text-label-md uppercase text-secondary">${esc(role)}</p>
          <p class="font-label-lg text-label-lg text-on-surface">${esc(p.name)}</p>
          ${p.also ? `<p class="font-body-sm text-body-sm text-on-surface-variant">${esc(p.also)}</p>` : ""}
          ${p.email ? `<a href="mailto:${esc(p.email)}" class="font-body-sm text-body-sm text-primary-container hover:underline break-all">${esc(p.email)}</a>` : ""}
        </div>
      </div>`;
    const people = [
      LD.dean && personCard(LD.dean, "Trưởng khoa"),
      ...LD.vice_deans.map((v) => personCard(v, "Phó Trưởng khoa")),
      ...LD.program_directors.map((p) => personCard(p, p.role))
    ].filter(Boolean);
    const leadBody = `
      ${people.length ? `<div class="grid gap-space-md sm:grid-cols-2">${people.join("")}</div>` : `<p class="font-body-md text-on-surface-variant">Thông tin ban lãnh đạo đang được cập nhật.</p>`}
      ${f.departments.length ? `
        <h3 class="font-headline-sm text-headline-sm text-primary mt-space-xl mb-space-md">Bộ môn</h3>
        <ul class="divide-y divide-outline-variant/60 rounded-xl border border-outline-variant/60">
          ${f.departments.map((d) => `<li class="flex flex-col sm:flex-row sm:items-center justify-between gap-space-xs p-space-md">
            <span class="font-label-lg text-label-lg">${esc(d.name)}</span>
            ${d.head ? `<span class="font-body-sm text-body-sm text-on-surface-variant">Trưởng BM: ${esc(d.head)}</span>` : ""}</li>`).join("")}
        </ul>` : ""}`;

    /* Hoạt động sinh viên */
    const svCards = [
      ...lcds.map((l) => ({ href: `${L.sv("lcd", l.id)}`, ic: "diversity_3", tag: "Liên chi đoàn", t: l.name, s: l.secretary ? `Bí thư: ${l.secretary}` : (l.activities[0] || "Xem hoạt động") })),
      ...clubs.map((c) => ({ href: `${L.sv("clb", c.id)}`, ic: "interests", tag: "Câu lạc bộ", t: c.name, s: c.description || c.category || "" }))
    ];
    const svBody = svCards.length ? `<div class="grid gap-space-md sm:grid-cols-2">${svCards.map((c) => `
      <a href="${c.href}" class="group flex items-start gap-space-md p-space-md rounded-xl border border-outline-variant/60 hover:border-secondary-container hover:bg-secondary-fixed/30 transition-colors">
        <span class="shrink-0 w-10 h-10 rounded-lg bg-secondary-fixed text-secondary flex items-center justify-center">${icon(c.ic, "text-[22px]")}</span>
        <span class="min-w-0">
          <span class="block font-label-sm text-label-sm uppercase text-secondary">${c.tag}</span>
          <span class="block font-label-lg text-label-lg text-on-surface">${esc(c.t)}</span>
          <span class="block font-body-sm text-body-sm text-on-surface-variant line-clamp-2">${esc(c.s)}</span>
        </span>
      </a>`).join("")}</div>
      <a href="${L.sv("clb")}" class="mt-space-lg inline-flex items-center gap-space-xs font-label-lg text-label-lg text-secondary hover:underline">Khám phá tất cả CLB của trường ${icon("arrow_forward", "text-[18px]")}</a>`
      : `<p class="text-on-surface-variant">Đang cập nhật. <a class="text-primary-container underline" href="${L.sv()}">Xem hoạt động sinh viên toàn trường</a>.</p>`;

    /* Liên hệ */
    const contactRows = [
      C.office && ["location_on", "Văn phòng", esc(C.office)],
      C.phone && ["call", "Điện thoại", `<a class="hover:underline" href="tel:${esc(C.phone.replace(/[^\d+]/g, "").slice(0, 11))}">${esc(C.phone)}</a>`],
      C.email && ["mail", "Email", `<a class="hover:underline break-all" href="mailto:${esc(C.email)}">${esc(C.email)}</a>`],
      C.admissions_email && ["contact_mail", "Email tuyển sinh", `<a class="hover:underline break-all" href="mailto:${esc(C.admissions_email)}">${esc(C.admissions_email)}</a>`],
      C.secretary && ["support_agent", "Thư ký khoa", `${esc(C.secretary.name)}${C.secretary.email ? ` – <a class="hover:underline" href="mailto:${esc(C.secretary.email)}">${esc(C.secretary.email)}</a>` : ""}`],
      C.facebook && ["thumb_up", "Fanpage", `<a class="hover:underline break-all" target="_blank" rel="noopener" href="${esc(C.facebook)}">${esc(C.facebook.replace("https://www.", ""))}</a>`],
      C.contact_page && ["link", "Trang liên hệ", `<a class="hover:underline" target="_blank" rel="noopener" href="${esc(C.contact_page)}">Mở trang liên hệ</a>`]
    ].filter(Boolean);
    const links = Object.entries(f.links || {});
    const contactBody = `
      <div class="grid gap-space-xl lg:grid-cols-2">
        <dl class="space-y-space-md">${contactRows.map(([ic, k, v]) => `
          <div class="flex gap-space-md">
            <span class="shrink-0 w-10 h-10 rounded-lg bg-surface-container text-primary-container flex items-center justify-center">${icon(ic, "text-[20px]")}</span>
            <div class="min-w-0"><dt class="font-label-md text-label-md text-on-surface-variant uppercase">${k}</dt><dd class="font-body-md text-body-md text-on-surface">${v}</dd></div>
          </div>`).join("") || `<p class="text-on-surface-variant">Đang cập nhật.</p>`}
        </dl>
        <div>
          <h3 class="font-headline-sm text-headline-sm text-primary mb-space-md">Liên kết hữu ích</h3>
          <div class="flex flex-col gap-space-sm">
            <a target="_blank" rel="noopener" href="${esc(f.url)}" class="flex items-center justify-between p-space-md rounded-lg bg-primary-container text-on-primary hover:bg-primary transition-colors">
              <span class="font-label-lg text-label-lg">Trang chính thức của khoa</span>${icon("open_in_new", "text-[20px]")}</a>
            ${links.map(([k, u]) => `<a target="_blank" rel="noopener" href="${esc(u)}" class="flex items-center justify-between p-space-md rounded-lg border border-outline-variant/60 hover:border-primary-container hover:bg-surface-container-low transition-colors">
              <span class="font-label-lg text-label-lg">${LINK_LABELS[k] || k}</span>${icon("open_in_new", "text-[18px] text-on-surface-variant")}</a>`).join("")}
          </div>
        </div>
      </div>`;

    const others = D.faculties.filter((x) => x.id !== f.id);
    app.innerHTML = `
      ${hero({
        crumbs: [["Trang chủ", L.home()], ["Khoa", L.khoa()], [shortName(f.name), null]],
        eyebrow: f.type === "institute" ? "Viện" : "Khoa", title: f.name, ic: FACULTY_ICONS[f.id],
        lead: majors.length ? `Đào tạo ${majors.length} ngành: ${majors.map((m) => esc(m.name)).join(", ")}.` : "Chương trình cử nhân liên kết quốc tế và đào tạo năm cuối tại nước ngoài.",
        chips: f.formed_from.length ? ["Hình thành từ: " + f.formed_from.map((x) => x.replace(/\s*\(.*?\)/, "")).join(", ")] : [],
        actions: [
          majors.length ? btn(L.khoa(f.id, "nganh-hoc"), "Xem ngành tuyển sinh", "school") : "",
          btn(f.url, "Trang chính thức", "open_in_new", "outline", true),
          C.facebook ? btn(C.facebook, "Fanpage", "thumb_up", "outline", true) : ""
        ].join("")
      })}

      <div class="bg-surface-container-lowest border-b border-outline-variant/50">
        <div class="max-w-7xl mx-auto px-6 lg:px-12 grid grid-cols-2 md:grid-cols-4">
          ${stats.map(([n, l], i) => `<div class="py-space-lg px-space-md text-center border-outline-variant/50 ${i % 2 === 0 ? "border-r" : "md:border-r"} ${i < 2 ? "border-b md:border-b-0" : ""} ${i === 3 ? "md:border-r-0" : ""}"><p class="font-headline-lg text-headline-lg text-primary-container">${n}</p><p class="font-label-md text-label-md text-on-surface-variant uppercase">${l}</p></div>`).join("")}
        </div>
      </div>

      <div class="max-w-7xl mx-auto px-6 lg:px-12 py-space-xl lg:py-space-2xl grid gap-space-xl lg:grid-cols-[260px_1fr]">
        <aside class="lg:sticky lg:top-36 self-start space-y-space-lg">
          <label class="lg:hidden block">
            <span class="sr-only">Chọn khoa</span>
            <select id="faculty-select" class="w-full rounded-lg border-outline-variant bg-surface-container-lowest font-label-lg text-label-lg py-space-sm">
              ${D.faculties.map((x) => `<option value="${x.id}" ${x.id === f.id ? "selected" : ""}>${esc(x.name)}</option>`).join("")}
            </select>
          </label>
          <nav aria-label="Mục lục" class="hidden lg:block bg-surface-container-lowest rounded-xl border border-outline-variant/50 p-space-sm">
            ${toc.map(([id, t, ic]) => `<a href="${L.khoa(f.id, id)}" data-toc="${id}" class="flex items-center gap-space-sm px-space-md py-space-sm rounded-lg font-label-lg text-label-lg text-on-surface-variant hover:bg-surface-container-low hover:text-primary-container">${icon(ic, "text-[20px]")}${t}</a>`).join("")}
          </nav>
          <div class="hidden lg:block bg-surface-container-lowest rounded-xl border border-outline-variant/50 p-space-md">
            <p class="font-label-md text-label-md uppercase text-on-surface-variant px-space-sm mb-space-sm">Khoa khác</p>
            ${others.map((x) => `<a href="${L.khoa(x.id)}" class="flex items-center gap-space-sm px-space-sm py-space-xs rounded-lg font-body-sm text-body-sm text-on-surface hover:bg-surface-container-low hover:text-primary-container">${icon(FACULTY_ICONS[x.id] || "school", "text-[18px] text-on-surface-variant")}${esc(shortName(x.name))}</a>`).join("")}
          </div>
        </aside>
        <div class="space-y-space-lg min-w-0">
          ${section("gioi-thieu", "Giới thiệu", "info", intro)}
          ${section("nganh-hoc", f.type === "institute" ? "Chương trình đào tạo" : "Ngành & chuyên ngành tuyển sinh 2026", "school", majorsBody)}
          ${section("lanh-dao", "Ban lãnh đạo & bộ môn", "badge", leadBody)}
          ${section("sinh-vien", "Liên chi đoàn & câu lạc bộ", "diversity_3", svBody)}
          ${section("lien-he", "Liên hệ", "call", contactBody)}
        </div>
      </div>`;

    document.getElementById("faculty-select")?.addEventListener("change", (e) => { location.href = L.khoa(e.target.value); });
    highlightToc();
  }

  function highlightToc() {
    const links = document.querySelectorAll("[data-toc]");
    if (!links.length || !("IntersectionObserver" in window)) return;
    const io = new IntersectionObserver((entries) => {
      entries.forEach((en) => {
        if (!en.isIntersecting) return;
        links.forEach((a) => {
          const on = a.dataset.toc === en.target.id;
          a.classList.toggle("bg-primary-fixed", on);
          a.classList.toggle("text-primary-container", on);
        });
      });
    }, { rootMargin: "-40% 0px -55% 0px" });
    links.forEach((a) => { const s = document.getElementById(a.dataset.toc); s && io.observe(s); });
  }

  function renderNotFound(id) {
    app.innerHTML = `<div class="max-w-xl mx-auto px-6 py-space-2xl text-center">
      ${icon("search_off", "text-[48px] text-on-surface-variant")}
      <h1 class="font-headline-md text-headline-md text-primary my-space-md">Không tìm thấy khoa "${esc(id)}"</h1>
      <a class="text-primary-container underline" href="${L.khoa()}">Xem danh sách các khoa</a></div>`;
  }

  /* Được router gọi: DUE.views.khoa(phần tử, id khoa, mục) */
  window.DUE.views = window.DUE.views || {};
  window.DUE.views.khoa = function (el, id, sec) {
    app = el;
    const key = id || "";
    if (app.dataset.view === "khoa:" + key && sec) {           // cùng khoa → chỉ cuộn tới mục
      document.getElementById(sec)?.scrollIntoView({ behavior: "smooth" });
      return;
    }
    app.dataset.view = "khoa:" + key;
    const f = id && D.faculties.find((x) => x.id === id);
    if (!id) renderIndex(); else if (f) renderFaculty(f); else renderNotFound(id);
    if (sec) setTimeout(() => document.getElementById(sec)?.scrollIntoView(), 60); else window.scrollTo(0, 0);
  };
})();
