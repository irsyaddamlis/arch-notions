/**
 * StatCard - one of the four top-row cards.
 *
 * variant="highlight" renders the solid blue card style (used for the
 * first card in the mockup, e.g. "Indonesia Debt"). Any other variant
 * renders the light card style used by the remaining three.
 */
export default function StatCard({
  label,
  value,
  footnote,
  icon,
  variant = "default",
}) {
  const isHighlight = variant === "highlight";

  return (
    <div
      className={`rounded-2xl p-5 flex flex-col justify-between min-h-[160px] ${
        isHighlight
          ? "bg-gradient-to-br from-[#3B7CF6] to-[#1D4ED8] text-white"
          : "bg-[#F5F6F8] text-[#0B1220]"
      }`}
    >
      <div className="flex items-start justify-between">
        <span
          className={`text-sm ${
            isHighlight ? "text-white/85" : "text-gray-500"
          }`}
        >
          {label}
        </span>
        <span
          className={`shrink-0 rounded-full w-9 h-9 flex items-center justify-center ${
            isHighlight ? "bg-white text-[#1D4ED8]" : "bg-[#3B7CF6] text-white"
          }`}
        >
          {icon}
        </span>
      </div>

      <div className="mt-3">
        <div className="text-3xl font-bold leading-tight">{value}</div>
        <div
          className={`text-xs mt-1 ${
            isHighlight ? "text-white/80" : "text-gray-400"
          }`}
        >
          {footnote}
        </div>
      </div>
    </div>
  );
}
