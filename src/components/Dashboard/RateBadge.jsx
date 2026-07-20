export default function RateBadge({ value, label }) {
  return (
    <div className="flex flex-col items-center gap-2">
      <span className="text-3xl font-bold text-white">{value}</span>
      <span className="bg-[#3B7CF6] text-white text-sm font-medium rounded-full px-5 py-2">
        {label}
      </span>
    </div>
  );
}
