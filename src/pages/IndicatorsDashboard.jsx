import { Droplet, PackageOpen, TrendingUp, Wallet } from "lucide-react";
import { useEffect, useState } from "react";

import ArchNotionsLogo from "../components/dashboard/ArchNotionsLogo";
import CurrencyList from "../components/dashboard/CurrencyList";
import IhsgBadge from "../components/dashboard/IhsgBadge";
import NavBar from "../components/dashboard/NavBar";
import RateBadge from "../components/dashboard/RateBadge";
import StarBackground from "../components/dashboard/StarBackground";
import StatCard from "../components/dashboard/StatCard";
import TrendChart from "../components/dashboard/TrendChart";

const INDICATORS_ENDPOINT = "/api/indicators/";
const TREND_ENDPOINT = "/api/trend/";

export default function IndicatorsDashboard() {
  const [indicators, setIndicators] = useState({});
  const [trend, setTrend] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;

    async function loadData() {
      try {
        const [indicatorsRes, trendRes] = await Promise.all([
          fetch(INDICATORS_ENDPOINT),
          fetch(TREND_ENDPOINT),
        ]);

        if (!indicatorsRes.ok || !trendRes.ok) {
          throw new Error("Failed to load dashboard data");
        }

        const indicatorsData = await indicatorsRes.json();
        const trendData = await trendRes.json();

        if (!cancelled) {
          setIndicators(indicatorsData);
          setTrend(trendData);
        }
      } catch (err) {
        if (!cancelled) setError(err.message);
      }
    }

    loadData();
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div
      className="relative min-h-screen text-white"
      style={{
        paddingLeft: "clamp(1rem, 6vw, 3.75rem)",
        paddingRight: "clamp(1rem, 6vw, 3.75rem)",
        paddingTop: "clamp(2rem, 6vw, 5rem)",
        paddingBottom: "clamp(2rem, 6vw, 5rem)",
      }}
    >
      {/* 1. Canvas layer (fixed at zIndex 0) */}
      <StarBackground />

      {/* 2. Content layer forced ABOVE canvas (relative z-10) */}
      <div className="relative z-10">
        {/* Header: stacks on mobile, side-by-side from sm up */}
        <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between mb-8 sm:mb-10">
          <header>
            <a href="/" className="inline-block">
              <ArchNotionsLogo className="mb-1 w-40 sm:w-56 md:w-72 lg:w-96" />
            </a>
            <h1 className="text-xl sm:text-2xl font-bold text-white">
              Indonesia's Economic Outlook
            </h1>
          </header>
          <NavBar current="Outlook" />
        </div>

        {error && (
          <div className="mb-6 rounded-lg bg-red-950 text-red-300 text-sm px-4 py-3">
            Couldn't load dashboard data: {error}
          </div>
        )}

        <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-5 mb-8 sm:mb-10">
          <StatCard
            variant="highlight"
            label="Indonesia's Debt"
            value={indicators.id_debt ?? "\u2014"}
            icon={<Wallet size={18} />}
          />
          <StatCard
            label="Broad Money"
            value={indicators.broad_money ?? "\u2014"}
            icon={<PackageOpen size={18} />}
          />
          <StatCard
            label="Oil Price"
            value={indicators.oil_price ?? "\u2014"}
            icon={<Droplet size={18} />}
          />
          <StatCard
            label="GDP Growth"
            value={indicators.gdp ?? "\u2014"}
            icon={<TrendingUp size={18} />}
          />
        </section>

        <section className="grid grid-cols-1 lg:grid-cols-[2fr_auto_1fr] gap-3 items-start">
          <TrendChart data={trend} />

          <div className="flex flex-col gap-3 p-3 sm:p-5">
            <CurrencyList data={indicators} />
          </div>

          {/* IHSG badge + rate badges: side-by-side on larger screens,
              stacked on mobile so the badge doesn't get squeezed next to
              a 2x2 grid in a narrow flex row */}
          <div className="flex flex-col sm:flex-row lg:flex-col items-center justify-center gap-3 p-3 sm:p-5">
            <IhsgBadge value={indicators.ihsg ?? "\u2014"} />

            <div className="grid grid-cols-2 gap-x-4 gap-y-4 sm:gap-x-6 sm:gap-y-6">
              <RateBadge label="SBI Rate" value={indicators.bi_rate ?? "\u2014"} />
              <RateBadge label="Save Deposit" value={indicators.deposit_rate ?? "\u2014"} />
              <RateBadge label="Productive Loan" value={indicators.lending_rate ?? "\u2014"} />
              <RateBadge label="Consumptive Loan" value={indicators.loan_rate ?? "\u2014"} />
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
