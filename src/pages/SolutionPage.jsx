import { useState } from "react";

import ArchNotionsLogo from "../components/dashboard/ArchNotionsLogo";
import NavBar from "../components/dashboard/NavBar";
import StarBackground from "../components/dashboard/StarBackground";

const ARTICLES_ENDPOINT = "/api/solution/";
const PDFJS_URL = "/static/pdfjs/pdf.mjs";
const PDFJS_WORKER_URL = "/static/pdfjs/pdf.worker.mjs";

const INK = "#F5F3EC";
const MUTED = "#9CA3AF";
const FAINT = "#6B7280";
const BRASS = "#C9A227";
const EMERALD = "#34D399";
const CARD_BG = "#0c1018";
const HAIRLINE = "rgba(255,255,255,0.08)";

export default function SolutionPage() {
  const [data, setData] = useState({});

  return (
    <div className="relative min-h-screen px-15 py-20 text-white">
      <StarBackground />
      <div className="relative z-10">
        <div className="flex items-start justify-between mb-10">
          <header className="mb-10">
            <a className="inline-block">
            <ArchNotionsLogo className="mb-1 w-128" />
            </a>
            <h1 className="text-18rem font-bold text-white">
            Establish, Growth, &amp; Sustain with Us
            </h1>
          </header>
          <NavBar current="Solution" />
        </div>
      </div>
    </div>
  );
}
