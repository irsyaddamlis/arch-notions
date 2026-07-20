import { Droplet, PackageOpen, TrendingUp, Wallet } from "lucide-react";
import { useEffect, useState } from "react";

import ArchNotionsLogo from "../components/dashboard/ArchNotionsLogo";
import CurrencyList from "../components/dashboard/CurrencyList";
import IhsgBadge from "../components/dashboard/IhsgBadge";
import RateBadge from "../components/dashboard/RateBadge";
import StatCard from "../components/dashboard/StatCard";
import TrendChart from "../components/dashboard/TrendChart";

// Adjust these to match your actual Django/DRF endpoints.
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
    <div className="min-h-screen bg-[#0A0E17] px-8 py-10">
      <header className="mb-10">
        <ArchNotionsLogo className="mb-4" />
        <h1 className="text-4xl font-bold text-white">Indicators</h1>
        <p className="text-gray-400 mt-1">Indonesia Economic Outlook</p>
      </header>

      {error && (
        <div className="mb-6 rounded-lg bg-red-950 text-red-300 text-sm px-4 py-3">
          Couldn't load dashboard data: {error}
        </div>
      )}

      <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-10">
        <StatCard
          variant="highlight"
          label="Indonesia Debt"
          value={indicators.id_debt ?? "\u2014"}
          footnote="+12% from last month"
          icon={<Wallet size={18} />}
        />
        <StatCard
          label="Broad Money"
          value={indicators.broad_money ?? "\u2014"}
          footnote="+8% growth"
          icon={<PackageOpen size={18} />}
        />
        <StatCard
          label="Oil Price"
          value={indicators.oil_price ?? "\u2014"}
          footnote="+5% this week"
          icon={<Droplet size={18} />}
        />
        <StatCard
          label="GDP Growth"
          value={indicators.gdp ?? "\u2014"}
          footnote="+1.2% increase"
          icon={<TrendingUp size={18} />}
        />
      </section>

      <section className="grid grid-cols-1 lg:grid-cols-[2fr_auto_1fr] gap-8 items-start">
        <TrendChart data={trend} />

        <div className="flex items-center justify-center">
          <IhsgBadge value={indicators.ihsg ?? "\u2014"} />
        </div>

        <div className="flex flex-col gap-8">
          <CurrencyList data={indicators} />

          <div className="grid grid-cols-2 gap-x-6 gap-y-6">
            <RateBadge label="BI Rate" value={indicators.bi_rate ?? "\u2014"} />
            <RateBadge label="Deposit" value={indicators.deposit_rate ?? "\u2014"} />
            <RateBadge label="Lending Rate" value={indicators.lending_rate ?? "\u2014"} />
            <RateBadge label="Loan Rate" value={indicators.loan_rate ?? "\u2014"} />
          </div>
        </div>
      </section>
    </div>
  );
}
