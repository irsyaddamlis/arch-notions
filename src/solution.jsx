import { createElement } from "react";
import { createRoot } from "react-dom/client";

import SolutionPage from "./pages/SolutionPage";

createRoot(document.getElementById("root")).render(
  createElement(SolutionPage)
);