import { ChevronLeft, ChevronRight, Download, FileText, Search, ShieldCheck, X } from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";

import ArchNotionsLogo from "../components/dashboard/ArchNotionsLogo";
import NavBar from "../components/dashboard/NavBar";
import StarBackground from "../components/dashboard/StarBackground";

const ARTICLES_ENDPOINT = "/api/articles/";
const PDFJS_URL = "/static/pdfjs/pdf.mjs";
const PDFJS_WORKER_URL = "/static/pdfjs/pdf.worker.mjs";
const PAGE_SIZE = 5;

const INK = "#F5F3EC";
const MUTED = "#9CA3AF";
const FAINT = "#6B7280";
const BRASS = "#C9A227";
const EMERALD = "#34D399";
const CARD_BG = "#0c1018";
const HAIRLINE = "rgba(255,255,255,0.08)";

// Some categories in the DB were created ad-hoc (not through the fixed
// choices list) and come back as raw slugs like "business_development".
// This normalizes ANY category string to a clean title-cased label,
// regardless of what the backend sends, so the UI never shows a raw slug.
function formatCategoryLabel(raw) {
  if (!raw) return "";
  return raw
    .replace(/[_-]+/g, " ")
    .trim()
    .split(" ")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

function formatShortDate(date) {
  if (!date) return "-";
  return new Date(date).toLocaleDateString("en-GB", {
    day: "2-digit", month: "short", year: "numeric"
  });
}

function ClearanceMark({ downloadable, compact = false }) {
  if (downloadable) {
    return (
      <span
        className="flex items-center gap-1.5 rounded-md font-semibold tracking-[0.12em] whitespace-nowrap"
        style={{
          borderColor: `${EMERALD}40`, backgroundColor: `${EMERALD}1A`, color: EMERALD,
          padding: compact ? "3px 6px" : "4px 10px", fontSize: compact ? 9 : 10
        }}
      >
        <ShieldCheck className={compact ? "h-3 w-3" : "h-3.5 w-3.5"} />
        {!compact && "Cleared"}
      </span>
    );
  }
  return (
    <span
      className="inline-flex items-center gap-1.5 rounded-md border font-semibold uppercase tracking-[0.12em] whitespace-nowrap"
      style={{
        borderColor: HAIRLINE, color: FAINT,
        padding: compact ? "3px 6px" : "4px 10px", fontSize: compact ? 9 : 10
      }}
    >
      {!compact && "View only"}
    </span>
  );
}

function ViewerPanel({ article, onClose, onBack, canDownload }) {
  const canvasRef = useRef(null);
  const pdfDocRef = useRef(null);
  const [pageNum, setPageNum] = useState(1);
  const [pageCount, setPageCount] = useState(0);
  const [loadState, setLoadState] = useState("loading");

  useEffect(() => {
    if (!article) return;
    let cancelled = false;
    setLoadState("loading");
    setPageNum(1);

    import(/* @vite-ignore */ PDFJS_URL).then((pdfjsLib) => {
      if (cancelled) return;
      pdfjsLib.GlobalWorkerOptions.workerSrc = PDFJS_WORKER_URL;
      pdfjsLib.getDocument({ url: article.file_url }).promise
        .then((pdf) => {
          if (cancelled) return;
          pdfDocRef.current = pdf;
          setPageCount(pdf.numPages);
          setLoadState("ready");
          renderPage(pdf, 1);
        })
        .catch(() => { if (!cancelled) setLoadState("error"); });
    }).catch(() => { if (!cancelled) setLoadState("error"); });

    return () => { cancelled = true; };
  }, [article]);

  function renderPage(pdf, num) {
    pdf.getPage(num).then((page) => {
      const canvas = canvasRef.current;
      if (!canvas) return;
      const viewport = page.getViewport({ scale: 1.3 });
      canvas.height = viewport.height;
      canvas.width = viewport.width;
      page.render({ canvasContext: canvas.getContext("2d"), viewport });
    });
  }

  function goToPage(next) {
    const pdf = pdfDocRef.current;
    if (!pdf) return;
    const clamped = Math.min(Math.max(next, 1), pdf.numPages);
    setPageNum(clamped);
    renderPage(pdf, clamped);
  }

  if (!article) return null;

  return (
    <div
      className="flex h-full flex-col rounded-xl border"
      style={{ backgroundColor: CARD_BG, borderColor: HAIRLINE }}
    >
      <div className="flex items-start justify-between gap-4 border-b px-4 py-3 sm:px-5 sm:py-4" style={{ borderColor: HAIRLINE }}>
        <div className="flex min-w-0 items-center gap-2">
          {/* Back button only shows on mobile - lets the user return to the list
              instead of the desktop-only side-by-side split view */}
          <button
            onClick={onBack}
            className="md:hidden shrink-0 rounded-md p-1.5 transition hover:bg-white/10"
            style={{ color: MUTED }}
            aria-label="Back to list"
          >
            <ChevronLeft className="h-5 w-5" />
          </button>
          <div className="min-w-0">
            <p className="truncate text-sm font-medium" style={{ color: INK }}>{article.title}</p>
            <p className="mt-0.5 text-[11px]" style={{ color: FAINT }}>
              {article.creator ? `By ${article.creator} · ` : ""}
              {formatShortDate(article.date)}
            </p>
          </div>
        </div>
        <button onClick={onClose} className="hidden md:block shrink-0 rounded-md p-1.5 transition hover:bg-white/10" style={{ color: MUTED }}>
          <X className="h-5 w-5" />
        </button>
      </div>

      <div className="flex flex-1 flex-col items-center justify-center overflow-auto p-4" style={{ backgroundColor: "#050709" }}>
        {loadState === "loading" && (
          <p className="py-16 text-center text-sm" style={{ color: MUTED }}>Loading document…</p>
        )}
        {loadState === "error" && (
          <p className="py-16 text-center text-sm" style={{ color: MUTED }}>
            Couldn't load this document for preview please check you internet connection.
          </p>
        )}
        <canvas ref={canvasRef} className="block max-w-full" style={{ display: loadState === "ready" ? "block" : "none" }} />
      </div>

      <div className="flex items-center justify-between gap-4 border-t px-4 py-3 sm:px-5" style={{ borderColor: HAIRLINE }}>
        <div className="flex items-center gap-2">
          <button
            onClick={() => goToPage(pageNum - 1)}
            disabled={pageNum <= 1}
            className="rounded-md border p-1.5 transition disabled:opacity-30"
            style={{ borderColor: HAIRLINE, color: MUTED }}
          >
            <ChevronLeft className="h-4 w-4" />
          </button>
          <span className="text-[12px] tabular-nums" style={{ color: MUTED }}>
            {pageCount ? `Page ${pageNum} of ${pageCount}` : "—"}
          </span>
          <button
            onClick={() => goToPage(pageNum + 1)}
            disabled={pageNum >= pageCount}
            className="rounded-md border p-1.5 transition disabled:opacity-30"
            style={{ borderColor: HAIRLINE, color: MUTED }}
          >
            <ChevronRight className="h-4 w-4" />
          </button>
        </div>

        {canDownload && (
          <a
            href={`${article.file_url}?download=1`}
            className="flex items-center gap-1.5 rounded-md px-3 py-1.5 text-[12px] font-semibold"
            style={{ backgroundColor: `${EMERALD}1A`, color: EMERALD }}
          >
            <Download className="h-3.5 w-3.5" />
            Download
          </a>
        )}
      </div>
    </div>
  );
}

export default function ArticlesPage() {
  const [articles, setArticles] = useState([]);
  const [categories, setCategories] = useState([]);
  const [activeCategory, setActiveCategory] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [status, setStatus] = useState("loading");
  const [previewArticle, setPreviewArticle] = useState(null);
  const [page, setPage] = useState(1);
  const [canDownload, setCanDownload] = useState(false);

  const fetchArticles = () => {
    setStatus("loading");
    fetch(ARTICLES_ENDPOINT, { credentials: "include" })
      .then(async (res) => {
        if (res.status === 403) { setStatus("forbidden"); return null; }
        if (!res.ok) throw new Error(`Request failed: ${res.status}`);
        return res.json();
      })
      .then((data) => {
        if (!data) return;
        setArticles(data.results || []);
        setCategories(data.categories || []);
        setCanDownload(!!data.can_download);
        setStatus("ready");
      })
      .catch(() => setStatus("error"));
  };

  useEffect(() => { fetchArticles(); }, []);

  const filtered = useMemo(() => {
    const q = searchQuery.trim().toLowerCase();
    return articles.filter((a) => {
      const matchesCategory = activeCategory === "all" || a.category === activeCategory || a.category_display === activeCategory;
      const matchesSearch =
        !q ||
        (a.title || "").toLowerCase().includes(q) ||
        (a.creator || "").toLowerCase().includes(q) ||
        (a.category_display || "").toLowerCase().includes(q);
      return matchesCategory && matchesSearch;
    });
  }, [articles, activeCategory, searchQuery]);

  useEffect(() => { setPage(1); }, [activeCategory, searchQuery]);

  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const pageItems = filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  const isSplit = !!previewArticle;

  return (
    <div
      className="relative min-h-screen"
      style={{
        backgroundColor: "#07090e",
        color: INK,
        paddingLeft: "clamp(1rem, 6vw, 3.75rem)",
        paddingRight: "clamp(1rem, 6vw, 3.75rem)",
        paddingTop: "clamp(2rem, 6vw, 5rem)",
        paddingBottom: "clamp(2rem, 6vw, 5rem)",
      }}
    >
      <StarBackground />

      <div className="relative z-10">
        {/* Header: stacks on mobile, sits side-by-side from sm up */}
        <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between mb-8 sm:mb-10">
          <header>
            <ArchNotionsLogo className="mb-1 w-40 sm:w-56 md:w-72 lg:w-96" />
            <h1 className="text-xl sm:text-2xl font-semibold tracking-tight" style={{ color: "#fff" }}>
              Insight &amp; Knowledge
            </h1>
          </header>
          <NavBar current="Articles" />
        </div>

        {/* On mobile: single column, list and viewer never share the row.
            From md up: side-by-side split view as before. */}
        <div className="flex flex-col md:flex-row gap-6 items-start">
          {/* List column: hidden on mobile once an article is open, so the
              viewer gets the full screen instead of a cramped sliver */}
          <div
            className={`transition-all duration-300 ease-in-out ${isSplit ? "hidden md:block" : "w-full"}`}
            style={{ flexShrink: 0, width: isSplit ? 360 : undefined }}
          >
            <div className="w-full">
              <div style={{ position: "relative", width: "100%", maxWidth: isSplit ? "none" : 320, marginBottom: 16 }}>
                <Search
                  style={{
                    position: "absolute",
                    color: FAINT,
                    left: 16,
                    top: "50%",
                    transform: "translateY(-50%)",
                    width: 16,
                    height: 16,
                    pointerEvents: "none",
                  }}
                />
                <input
                  type="text"
                  placeholder="Search the library…"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  style={{
                    width: "100%",
                    borderRadius: 8,
                    border: `1px solid ${HAIRLINE}`,
                    backgroundColor: CARD_BG,
                    color: INK,
                    fontSize: 14,
                    outline: "none",
                    paddingTop: 10,
                    paddingBottom: 10,
                    paddingLeft: 44,
                    paddingRight: 16,
                  }}
                />
              </div>

              <div className="mb-6">
                <select
                  value={activeCategory}
                  onChange={(e) => setActiveCategory(e.target.value)}
                  className="w-full sm:w-64 rounded-lg border px-3 py-2.5 text-sm outline-none"
                  style={{ backgroundColor: CARD_BG, borderColor: HAIRLINE, color: INK }}
                >
                  <option value="all">All categories</option>
                  {categories.map((c) => (
                    <option key={c.value} value={c.value}>{c.label}</option>
                  ))}
                </select>
              </div>

              {status === "loading" && <p className="text-sm" style={{ color: MUTED }}>Loading the register…</p>}

              {status === "forbidden" && (
                <div className="rounded-lg border px-5 py-4 text-sm" style={{ borderColor: HAIRLINE, color: MUTED }}>
                  Your account is waiting approval.
                </div>
              )}

              {status === "error" && (
                <div className="rounded-lg border px-5 py-4 text-sm" style={{ borderColor: HAIRLINE, color: MUTED }}>
                  Couldn't load the register.{" "}
                  <button onClick={fetchArticles} className="underline" style={{ color: BRASS }}>Try again</button>
                </div>
              )}

              {status === "ready" && (
                <div>
                  {/* Column header row: desktop-table style, hidden below md
                      since the mobile layout uses stacked cards instead */}
                  <div
                    className="hidden md:flex gap-4 pb-2 text-[12px] font-semibold tracking-[0.12em] border-b"
                    style={{ borderColor: HAIRLINE, color: FAINT }}
                  >
                    <span style={{ width: "3rem", flexShrink: 0 }}>Ref.</span>
                    <span style={{ width: "24rem", flexShrink: 0 }}>Subject</span>
                    <span style={{ width: "9rem", flexShrink: 0 }}>Category</span>
                    <span style={{ width: "9rem", flexShrink: 0 }}>Author</span>
                    <span style={{ width: "7rem", flexShrink: 0 }}>Filed</span>
                    <span style={{ width: "8rem", flexShrink: 0, textAlign: "right" }}>Access</span>
                  </div>

                  {filtered.length === 0 && (
                    <div className="mt-4 rounded-lg border border-dashed px-5 py-10 text-center text-sm" style={{ borderColor: HAIRLINE, color: MUTED }}>
                      Nothing filed under this search or category.
                    </div>
                  )}

                  {pageItems.map((article, i) => {
                    const isActive = previewArticle?.id === article.id;
                    const refNum = (page - 1) * PAGE_SIZE + i + 1;

                    return (
                      <div
                        key={article.id}
                        className="flex flex-col md:flex-row md:items-center gap-2 md:gap-4 py-4 border-b transition-colors"
                        style={{
                          borderColor: HAIRLINE,
                          backgroundColor: isActive ? "rgba(201,162,39,0.08)" : "transparent",
                        }}
                      >
                        {/* Mobile card layout: ref + title on one line, badge
                            top-right, metadata wrapped underneath */}
                        <div className="flex items-start justify-between gap-3 md:hidden">
                          <button
                            type="button"
                            onClick={() => setPreviewArticle(article)}
                            className="group flex items-center gap-2 text-left min-w-0 border-0 bg-transparent p-0"
                          >
                            <span className="text-xs font-mono shrink-0" style={{ color: FAINT }}>
                              {String(refNum).padStart(2, "0")}
                            </span>
                            <FileText className="h-3.5 w-3.5 shrink-0" style={{ color: FAINT }} />
                            <span
                              className="truncate text-[14px] font-medium leading-snug group-hover:underline"
                              style={{ color: isActive ? BRASS : INK }}
                            >
                              {article.title}
                            </span>
                          </button>
                          <div className="shrink-0">
                            <ClearanceMark downloadable={canDownload} compact />
                          </div>
                        </div>
                        <div className="flex flex-wrap items-center gap-x-3 gap-y-1 pl-[1.9rem] text-[12px] md:hidden" style={{ color: MUTED }}>
                          {(article.category_display || article.category) && (
                            <span>{formatCategoryLabel(article.category_display || article.category)}</span>
                          )}
                          {article.creator && <span>{article.creator}</span>}
                          <span>{formatShortDate(article.date)}</span>
                        </div>

                        {/* Desktop table-row layout, unchanged from before */}
                        <span className="hidden md:block text-sm font-mono" style={{ width: "3rem", flexShrink: 0, color: FAINT }}>
                          {String(refNum).padStart(2, "0")}
                        </span>

                        <div className="hidden md:block" style={{ width: isSplit ? "100%" : "24rem", flexShrink: 0 }}>
                          <button
                            type="button"
                            onClick={() => setPreviewArticle(article)}
                            className="group flex items-center gap-2 text-left cursor-pointer max-w-full border-0 bg-transparent p-0 outline-none"
                            title="Click to view document"
                          >
                            <FileText
                              className="h-3.5 w-3.5 shrink-0 transition-colors group-hover:text-[#C9A227]"
                              style={{ color: FAINT }}
                            />
                            <span
                              className="truncate text-[14px] font-medium leading-snug transition-colors group-hover:underline group-hover:text-[#C9A227]"
                              style={{ color: isActive ? BRASS : INK }}
                            >
                              {article.title}
                            </span>
                          </button>

                          {isSplit && (
                            <div className="mt-1 flex items-center gap-2" style={{ color: MUTED, fontSize: 11 }}>
                              {article.creator && <span className="truncate">By {article.creator}</span>}
                              <span>·</span>
                              <span>{formatShortDate(article.date)}</span>
                            </div>
                          )}
                        </div>

                        {!isSplit && (
                          <>
                            <span className="hidden md:block" style={{ width: "9rem", flexShrink: 0, color: MUTED, minWidth: 0 }}>
                              {article.category_display || article.category}
                            </span>
                            <span
                              className="hidden md:flex items-center gap-1.5 text-[13px]"
                              style={{ width: "9rem", flexShrink: 0, color: MUTED, minWidth: 0 }}
                            >
                              {article.creator}
                            </span>
                            <span className="hidden md:block text-[13px]" style={{ width: "7rem", flexShrink: 0, color: MUTED }}>
                              {formatShortDate(article.date)}
                            </span>
                          </>
                        )}

                        <div className="hidden md:flex" style={{ width: isSplit ? "auto" : "8rem", flexShrink: 0, justifyContent: "flex-end" }}>
                          <ClearanceMark downloadable={canDownload} compact={isSplit} />
                        </div>
                      </div>
                    );
                  })}

                  {filtered.length > 0 && (
                    <div className="flex w-full items-center justify-between mt-4">
                      <button
                        onClick={() => setPage((p) => Math.max(1, p - 1))}
                        disabled={page <= 1}
                        className="flex items-center gap-1 rounded-md border px-3 py-1.5 text-[12px] font-semibold transition-opacity"
                        style={{
                          borderColor: HAIRLINE,
                          color: MUTED,
                          opacity: page <= 1 ? 0.3 : 1,
                          cursor: page <= 1 ? "default" : "pointer",
                        }}
                      >
                        <ChevronLeft className="h-3.5 w-3.5" />
                        Prev
                      </button>

                      <span
                        className="rounded-md border px-3 py-1.5 text-[12px] font-semibold"
                        style={{ borderColor: HAIRLINE, color: MUTED }}
                      >
                        Page {page} of {totalPages}
                      </span>

                      <button
                        onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                        disabled={page >= totalPages}
                        className="flex items-center gap-1 rounded-md border px-3 py-1.5 text-[12px] font-semibold transition-opacity"
                        style={{
                          borderColor: HAIRLINE,
                          color: MUTED,
                          opacity: page >= totalPages ? 0.3 : 1,
                          cursor: page >= totalPages ? "default" : "pointer",
                        }}
                      >
                        Next
                        <ChevronRight className="h-3.5 w-3.5" />
                      </button>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>

          {isSplit && (
            <div
              className="w-full transition-all duration-300 ease-in-out"
              style={{ flex: 1, minWidth: 0, height: "70vh" }}
            >
              <ViewerPanel
                article={previewArticle}
                onClose={() => setPreviewArticle(null)}
                onBack={() => setPreviewArticle(null)}
                canDownload={canDownload}
              />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
