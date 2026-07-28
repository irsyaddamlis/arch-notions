import { createElement } from "react";
import { createRoot } from "react-dom/client";

import ArticlesDashboard from "./pages/ArticlePage";

createRoot(document.getElementById("root")).render(
  createElement(ArticlesDashboard)
);
