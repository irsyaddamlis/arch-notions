import { createElement } from "react";
import { createRoot } from "react-dom/client";

import IndicatorsDashboard from "./pages/IndicatorsDashboard";

createRoot(document.getElementById("root")).render(
  createElement(IndicatorsDashboard)
);