import { useState } from "react";


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

export default function ArticlesPage() {
  const [articles, setArticles] = useState([]);
  const [categories, setCategories] = useState([]);
  const [activeCategory, setActiveCategory] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [status, setStatus] = useState("loading");
  const [previewArticle, setPreviewArticle] = useState(null);
  const [page, setPage] = useState(1);

}