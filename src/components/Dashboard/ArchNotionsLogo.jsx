export default function ArchNotionsLogo({ className = "" }) {
  return (
    <div className={`relative inline-block ${className}`}>
      <svg
        viewBox="0 0 320 60"
        className="absolute -top-8 left-0 w-full h-auto"
        aria-hidden="true"
      >
        <path
          d="M10,50 C 80,-10 240,-10 310,50"
          fill="none"
          stroke="#7BA05B"
          strokeWidth="3"
          strokeLinecap="round"
        />
      </svg>
      <span className="font-serif italic text-3xl text-[#7BA05B] tracking-tight">
        arch-notions
      </span>
    </div>
  );
}
