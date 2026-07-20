export default function RateBadge({ value, label }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px', width: '100%' }}>
      <span className="text-3xl font-bold text-white">{value}</span>
      <div 
        className="bg-[#3B7CF6] text-white text-sm font-medium rounded-full px-4"
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          textAlign: 'center',
          width: '100%',
          maxWidth: '160px',
          height: '48px',
          lineHeight: '1.2'
        }}
      >
        {label}
      </div>
    </div>
  );
}