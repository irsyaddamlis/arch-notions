const CURRENCIES = [
  { code: "USD", flag: "\u{1F1FA}\u{1F1F8}" },
  { code: "GBP", flag: "\u{1F1EC}\u{1F1E7}" },
  { code: "EUR", flag: "\u{1F1EA}\u{1F1FA}" },
  { code: "SGD", flag: "\u{1F1F8}\u{1F1EC}" },
  { code: "CNY", flag: "\u{1F1E8}\u{1F1F3}" },
  { code: "JPY", flag: "\u{1F1EF}\u{1F1F5}" },
  { code: "AUD", flag: "\u{1F1E6}\u{1F1FA}" },
];

/**
 * data: object keyed by lowercase currency code + "_idr", e.g.
 * { usd_idr: "16,205.00", gbp_idr: "20,450.10", ... }
 * matching the IndicatorSnapshot keys from refresh_market_hourly.
 */
export default function CurrencyList({ data = {} }) {
  return (
    <div className="flex flex-col gap-3">
      {CURRENCIES.map(({ code, flag }) => {
        const key = `${code.toLowerCase()}_idr`;
        const value = data[key] ?? "\u2014";
        return (
          <div key={code} className="flex items-center gap-3">
            <span className="text-2xl leading-none" aria-hidden="true">
              {flag}
            </span>
            <span className="text-white text-lg font-medium">{value}</span>
          </div>
        );
      })}
    </div>
  );
}
