import { createElement } from "react";
import { createRoot } from "react-dom/client";

import SolutionPage from "./pages/ArticlePage";

createRoot(document.getElementById("root")).render(
  createElement(SolutionPage)
);