export default function IhsgBadge({ value }) {
  return (
    <div className="w-28 h-28 rounded-full bg-[#3B7CF6] flex flex-col items-center justify-center shrink-0 shadow-lg shadow-blue-900/40">
      <span className="text-white text-2xl font-bold leading-tight">
        {value}
      </span>
      <span className="text-white/85 text-xs font-medium">IHSG</span>
    </div>
  );
}
