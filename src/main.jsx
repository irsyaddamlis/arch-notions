import { createElement, useCallback, useEffect, useRef, useState } from "react";
import { createRoot } from "react-dom/client";

//const BG_IMAGE   = "/static/building-business.jpg";
const LOGO_IMAGE = "/static/arch-notions-logo.png";

const MENU_ITEMS = [
  { label: "About",    href: "/profile/" },
  { label: "Services", href: "/services/" },
  { label: "Articles", href: "/articles/" },
  { label: "Features", href: "/features/" },
];

const CONTACT = {
  email: "we_ready@arch-notions.com",
  whatsapp: "+62 85555553261",
  waLink: "https://wa.me/6285555553261",
};

const ITEM_W    = 130;
const THRESHOLD = 60;

const styles = {
  root: {
    position: "relative",
    width: "100vw",
    height: "100vh",
    minHeight: 520,
    overflow: "hidden",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontFamily: "Georgia, serif",
    userSelect: "none",
    background: "#05050a",
  },
  //bgLayer: {
  //  position: "absolute",
  //  inset: 0,
  //  backgroundImage: `url("${BG_IMAGE}")`,
  //  backgroundSize: "cover",
  //  backgroundPosition: "center",
  //  opacity: 0.9,
  //  zIndex: 0,
  //},
  canvas: {
    position: "absolute",
    inset: 0,
    width: "100%",
    height: "100%",
    display: "block",
    zIndex: 1,
  },
  bgOverlay: {
    position: "absolute",
    inset: 0,
    //background: "rgba(248, 248, 255, 0.3)",
    background: "rgba(5, 5, 10, 0.4)",
    zIndex: 2,
    pointerEvents: "none"
  },
  logoWrap: {
    position: "absolute",
    top: "40%",
    left: 0,
    right: 0,
    width: "100%",
    display: "flex",
    //background: "rgba(248, 248, 255, 0.5)",
    background: "transparent",
    justifyContent: "center",
    transform: "translateY(-50%)",
    zIndex: 2,
  },
  logoImg: {
    width: "min(90vw, 800px)",
    height: "auto",
    display: "block",
    filter: "drop-shadow(0 0 14px rgba(90,160,90,0.2))",
  },
  carouselZone: (cursor) => ({
    position: "absolute",
    bottom: 100,
    left: "50%",
    transform: "translateX(-50%)",
    width: "100%",
    maxWidth: 520,
    height: 90,
    zIndex: 4,
    cursor,
  }),
  track: (offsetPx, isDragging) => ({
    position: "absolute",
    top: "50%",
    left: "50%",
    display: "flex",
    alignItems: "center",
    transform: `translateY(-50%) translateX(calc(-50% + ${offsetPx}px))`,
    pointerEvents: "auto",
    transition: isDragging ? "none" : "transform 0.6s cubic-bezier(0.23, 1, 0.32, 1)",
  }),
  menuItem: (state) => ({
    color:
      state === "active"
        ? "#e8e8e0"
        : state === "near"
        ? "rgba(232,232,224,0.72)"
        : "rgba(232,232,224,0.42)",
    fontSize: state === "active" ? 12 : 11,
    letterSpacing: state === "active" ? "3.5px" : "3px",
    textTransform: "uppercase",
    padding: "10px 0",
    border:
      state === "active"
        ? "0.5px solid rgba(90,170,110,0.65)"
        : "0.5px solid rgba(90,170,110,0.12)",
    background:
      state === "active"
        ? "rgba(8,18,12,0.72)"
        : "rgba(8,18,12,0.35)",
    whiteSpace: "nowrap",
    flexShrink: 0,
    width: ITEM_W,
    textAlign: "center",
    boxSizing: "border-box",
    opacity: state === "active" ? 1 : state === "near" ? 0.72 : 0.42,
    transform: state === "active" ? "scale(1.1)" : state === "near" ? "scale(0.93)" : "scale(0.84)",
    transition: "color 0.35s, border-color 0.35s, background 0.35s, opacity 0.35s, transform 0.35s",
    textDecoration: "none",
  }),
  activeLine: {
    position: "absolute",
    bottom: 88,
    left: "50%",
    transform: "translateX(-50%)",
    width: 28,
    height: 1,
    background: "#5aaa6e",
    zIndex: 5,
  },
  dotsRow: {
    position: "absolute",
    bottom: 70,
    left: "50%",
    transform: "translateX(-50%)",
    display: "flex",
    gap: 8,
    zIndex: 5,
  },
  dot: (active) => ({
    width: 4,
    height: 4,
    borderRadius: "50%",
    background: active ? "#5aaa6e" : "rgba(90,170,110,0.28)",
    transform: active ? "scale(1.4)" : "scale(1)",
    transition: "background 0.3s, transform 0.3s",
  }),
  hint: (visible) => ({
    position: "absolute",
    bottom: 196,
    left: "50%",
    transform: "translateX(-50%)",
    color: "rgba(255,255,255,0.18)",
    fontSize: 9,
    letterSpacing: "2.5px",
    textTransform: "uppercase",
    zIndex: 4,
    pointerEvents: "none",
    opacity: visible ? 1 : 0,
    transition: "opacity 0.6s",
    whiteSpace: "nowrap",
  }),
  contactBar: {
    position: "absolute",
    bottom: 0,
    left: 0,
    right: 0,
    background: "rgba(29,49,46,0.85)",
    backdropFilter: "blur(8px)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    gap: 32,
    padding: "12px 24px",
    zIndex: 6,
    flexWrap: "wrap",
  },
  contactLabel: {
    fontSize: 10,
    letterSpacing: "2px",
    textTransform: "uppercase",
    color: "rgba(248,248,255,0.5)",
    marginRight: 6,
  },
  contactLink: {
    fontSize: 13,
    color: "#F8F8FF",
    textDecoration: "none",
    letterSpacing: "0.5px",
    transition: "color 0.2s",
  },
  contactDivider: {
    width: 1,
    height: 20,
    background: "rgba(248,248,255,0.2)",
  },
};

function getItemState(index, current, floatIndex) {
  const ref = floatIndex !== null ? floatIndex : current;
  const d = Math.abs(index - ref);
  if (d < 0.55) return "active";
  if (d < 1.4)  return "near";
  return "idle";
}

function clamp(val, min, max) {
  return Math.max(min, Math.min(max, val));
}

//This is starfield Function
function Starfield() {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let animationFrameId;
    let width = 0;
    let height = 0;
    const numStars = 150;
    let stars = [];

    function setupStars() {
      stars = [];
      for (let i = 0; i < numStars; i++) {
        stars.push({
          x: Math.random() * width - width / 2,
          y: Math.random() * height - height / 2,
          z: Math.random() * width,
        });
      }
    }

    function handleResize() {
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight;
      setupStars();
    }

    handleResize();

    function animate() {
      // Direct, forced sizing correction checks
      if (canvas.width === 0 || canvas.height === 0 || width === 0) {
        handleResize();
      }

      ctx.fillStyle = "rgba(5, 5, 10, 0.25)";
      ctx.fillRect(0, 0, width, height);

      // Force high-contrast white colors for visible particles
      ctx.fillStyle = "#ffffff";
      
      for (let i = 0; i < numStars; i++) {
        const star = stars[i];
        if (!star) continue;

        star.z -= 2; 
        if (star.z <= 0) {
          star.z = width;
          star.x = Math.random() * width - width / 2;
          star.y = Math.random() * height - height / 2;
        }

        const k = 128.0 / star.z;
        const px = star.x * k + width / 2;
        const py = star.y * k + height / 2;

        if (px >= 0 && px <= width && py >= 0 && py <= height) {
          const size = (1 - star.z / width) * 3;
          ctx.beginPath();
          ctx.arc(px, py, size, 0, Math.PI * 2);
          ctx.fill();
        }
      }

      animationFrameId = requestAnimationFrame(animate);
    }

    animate();
    window.addEventListener("resize", handleResize);

    return () => {
      cancelAnimationFrame(animationFrameId);
      window.removeEventListener("resize", handleResize);
    };
  }, []);

  return <canvas ref={canvasRef} style={styles.canvas} />;
}

export default function HomePage() {
  const [current, setCurrent]         = useState(0);
  const [liveOffset, setLiveOffset]   = useState(0);
  const [floatIndex, setFloatIndex]   = useState(null);
  const [cursor, setCursorStyle]      = useState("pointer");
  const [hintVisible, setHintVisible] = useState(true);
  const [hoveredContact, setHoveredContact] = useState(null);

  const lastX       = useRef(null);
  const lastWheel   = useRef(0);
  const accumulated = useRef(0);
  const currentRef  = useRef(0);

  currentRef.current = current;

  function trackOffset(live = 0) {
    const base = -currentRef.current * ITEM_W;
    return base + live + (MENU_ITEMS.length / 2 - 0.5) * ITEM_W;
  }

  const onMouseEnter = useCallback((e) => {
    const r = e.currentTarget.getBoundingClientRect();
    lastX.current       = e.clientX - r.left;
    accumulated.current = 0;
    setHintVisible(false);
    setCursorStyle("pointer");
  }, []);

  const onMouseDown = useCallback((e) => {
    const r = e.currentTarget.getBoundingClientRect();
    lastX.current       = e.clientX - r.left;
    accumulated.current = 0;
  }, []);

  const onMouseMove = useCallback((e) => {
    if (lastX.current === null) return;
    const r     = e.currentTarget.getBoundingClientRect();
    const x     = e.clientX - r.left;
    const delta = x - lastX.current;
    lastX.current = x;
    accumulated.current += delta;

    if (delta < -1.5)     setCursorStyle("w-resize");
    else if (delta > 1.5) setCursorStyle("e-resize");
    else                  setCursorStyle("pointer");

    if (accumulated.current < -THRESHOLD && currentRef.current < MENU_ITEMS.length - 1) {
      setCurrent(c => c + 1);
      accumulated.current = 0;
      setLiveOffset(0);
      setFloatIndex(null);
      return;
    }
    if (accumulated.current > THRESHOLD && currentRef.current > 0) {
      setCurrent(c => c - 1);
      accumulated.current = 0;
      setLiveOffset(0);
      setFloatIndex(null);
      return;
    }

    const live = clamp(accumulated.current * 0.3, -ITEM_W * 0.55, ITEM_W * 0.55);
    setLiveOffset(live);
    const base = -currentRef.current * ITEM_W;
    setFloatIndex(-(base + live) / ITEM_W);
  }, []);

  const onMouseLeave = useCallback(() => {
    lastX.current       = null;
    accumulated.current = 0;
    setLiveOffset(0);
    setFloatIndex(null);
    setCursorStyle("pointer");
  }, []);

  const onTouchStart = useCallback((e) => {
    lastX.current       = e.touches[0].clientX;
    accumulated.current = 0;
  }, []);

  const onTouchMove = useCallback((e) => {
    if (e.cancelable) e.preventDefault();
    const x     = e.touches[0].clientX;
    const delta = x - lastX.current;
    lastX.current = x;
    accumulated.current += delta;

    if (accumulated.current < -THRESHOLD && currentRef.current < MENU_ITEMS.length - 1) {
      setCurrent(c => c + 1);
      accumulated.current = 0;
      setLiveOffset(0);
      setFloatIndex(null);
      return;
    }
    if (accumulated.current > THRESHOLD && currentRef.current > 0) {
      setCurrent(c => c - 1);
      accumulated.current = 0;
      setLiveOffset(0);
      setFloatIndex(null);
      return;
    }

    const live = clamp(accumulated.current * 0.3, -ITEM_W * 0.55, ITEM_W * 0.55);
    setLiveOffset(live);
    const base = -currentRef.current * ITEM_W;
    setFloatIndex(-(base + live) / ITEM_W);
  }, []);

  const onTouchEnd = useCallback(() => {
    lastX.current       = null;
    accumulated.current = 0;
    setLiveOffset(0);
    setFloatIndex(null);
  }, []);

  const onWheel = useCallback((e) => {
    const now = Date.now();
    if (now - lastWheel.current < 300) return;
    if (Math.abs(e.deltaY) < 10) return;
    if (e.deltaY > 0 && currentRef.current < MENU_ITEMS.length - 1) {
      setCurrent(c => c + 1);
      lastWheel.current = now;
    } else if (e.deltaY < 0 && currentRef.current > 0) {
      setCurrent(c => c - 1);
      lastWheel.current = now;
    }
  }, []);

  return (
    <div style={styles.root}>
      {/* 1. Put the Starfield component here so it actually renders */}
      <Starfield /> 
      
      {/* 2. The overlay will sit safely right on top of it */}
      <div style={styles.bgOverlay} />
      
      <div style={styles.logoWrap}>
        <img src={LOGO_IMAGE} alt="arch-notions" style={styles.logoImg} />
      </div>

      <div style={styles.hint(hintVisible)}>move mouse left · right over menu</div>

      <div
        style={styles.carouselZone(cursor)}
        onMouseDown={onMouseDown}
        onMouseEnter={onMouseEnter}
        onMouseMove={onMouseMove}
        onMouseUp={onMouseLeave}
        onMouseLeave={onMouseLeave}
        onWheel={onWheel}
        onTouchStart={onTouchStart}
        onTouchMove={onTouchMove}
        onTouchEnd={onTouchEnd}
      >
        <div style={styles.track(trackOffset(liveOffset), lastX.current !== null)}>
          {MENU_ITEMS.map((item, i) => {
            const state = getItemState(i, current, floatIndex);
            return (
              <a
                key={item.label}
                href={item.href}
                style={styles.menuItem(state)}
                onClick={(e) => {
                  if (state !== "active") {
                    e.preventDefault();
                    setCurrent(i);
                    setLiveOffset(0);
                    setFloatIndex(null);
                    return;
                  }
                  if (Math.abs(accumulated.current) > 6) {
                    e.preventDefault();
                  }
                }}
              >
                {item.label}
              </a>
            );
          })}
        </div>
      </div>

      <div style={styles.activeLine} />

      <div style={styles.dotsRow}>
        {MENU_ITEMS.map((_, i) => (
          <div
            key={i}
            style={styles.dot(i === current)}
            onClick={() => { setCurrent(i); setLiveOffset(0); setFloatIndex(null); }}
          />
        ))}
      </div>

      {/* Contact bar */}
      <div style={styles.contactBar}>
        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <span style={styles.contactLabel}>Email</span>
          <a
            href={`mailto:${CONTACT.email}`}
            style={{
              ...styles.contactLink,
              color: hoveredContact === "email" ? "#5aaa6e" : "#F8F8FF",
            }}
            onMouseEnter={() => setHoveredContact("email")}
            onMouseLeave={() => setHoveredContact(null)}
          >
            {CONTACT.email}
          </a>
        </div>
        <div style={styles.contactDivider} />
        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <span style={styles.contactLabel}>WhatsApp</span>
          <a
            href={CONTACT.waLink}
            target="_blank"
            rel="noopener noreferrer"
            style={{
              ...styles.contactLink,
              color: hoveredContact === "wa" ? "#5aaa6e" : "#F8F8FF",
            }}
            onMouseEnter={() => setHoveredContact("wa")}
            onMouseLeave={() => setHoveredContact(null)}
          >
            {CONTACT.whatsapp}
          </a>
        </div>
      </div>
    </div>
  );
}

createRoot(document.getElementById("root")).render(createElement(HomePage));