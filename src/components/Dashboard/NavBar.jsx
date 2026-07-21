const NAV_ITEMS = [
  { label: "Home", href: "/" },  
  { label: "Outlook" },
  { label: "About", href: "/profile/" },
  { label: "Services", href: "/services/" },
  { label: "Articles", href: "/articles/" },
];

/**
 * Simple top nav bar reusing the same 4 destinations as the homepage
 * carousel (About/Outlook/Services/Articles), styled to match the
 * Indicators dashboard rather than the homepage's drag-carousel -
 * that carousel is absolutely positioned for a fullscreen 100vh hero
 * and wasn't built to sit inside a normal scrolling page.
 *
 * Usage: <NavBar current="Outlook" />
 */
export default function NavBar({ current }) {
  return (
    <nav className="flex items-center gap-2">
      {NAV_ITEMS.map((item) => {
        const isActive = item.label === current;
        return (
          <a
            key={item.label}
            href={item.href}
            className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
              isActive
                ? "bg-[#3B7CF6] text-white"
                : "text-gray-400 hover:text-white"
            }`}
          >
            {item.label}
          </a>
        );
      })}
    </nav>
  );
}
