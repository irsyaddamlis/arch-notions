import ArchNotionsLogo from "../components/dashboard/ArchNotionsLogo";
import NavBar from "../components/dashboard/NavBar";
import StarBackground from "../components/dashboard/StarBackground";

const INK = "#F5F3EC";
const MUTED = "#9CA3AF";
const FAINT = "#6B7280";
const BRASS = "#C9A227";
const EMERALD = "#34D399";
const CARD_BG = "#0c1018";
const HAIRLINE = "rgba(255,255,255,0.08)";

const solutionsConfig = {
  title: "Our Solutions",
  description:
    "Drive end-to-end business optimization and operating model design, leveraging data analytics and change management to execute sustainable people and organizational transformations",
  items: [
    {
      title: "Business Analytics & Intelligence",
      description:
        "We transform your market, financial, and operational data into centralized, automated intelligence assets that provide complete decision clarity. By combining historical performance tracking with forward-looking predictive modeling, we empower leadership teams to mitigate risk, optimize unit economics, and drive sustainable growth.",
      href: "#!",
      imageUrl: "/static/building-business.jpg",
    },
    {
      title: "Project Management & Transformation",
      description:
        "We streamline complex strategic initiatives through rigorous, end-to-end project governance—from initial scoping and execution to risk mitigation and final delivery. Our disciplined oversight ensures your projects stay on schedule, within budget, and structured for measurable impact.",
      href: "#!",
      imageUrl: "/static/project6.png",
    },
    {
      title: "People & Performance Optimization",
      description:
        "We optimize workforce productivity and organization-wide performance by combining data-driven talent insights with custom capability development. From skill gaps to strategic alignment, we ensure your workforce is structured and equipped to achieve key business targets.",
      href: "#!",
      imageUrl: "/static/project1.jpg",
    },
  ],
};

export default function SolutionPage() {
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
      <StarBackground />
      <div className="relative z-10">
        {/* Header: stacks on mobile, side-by-side from sm up */}
        <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between mb-8 sm:mb-10">
          <header>
            <a className="inline-block">
              <ArchNotionsLogo className="mb-1 w-40 sm:w-56 md:w-72 lg:w-96" />
            </a>
            <h1
              className="font-bold text-xl sm:text-2xl"
              style={{ color: INK }}
            >
              Establish, Growth, &amp; Sustain with Us
            </h1>
          </header>
          <NavBar current="Solution" />
        </div>

        <div className="relative z-20 w-full">
          <h2
            className="text-xl font-bold tracking-tight sm:text-2xl lg:text-3xl"
            style={{ color: INK }}
          >
            {solutionsConfig.title}
          </h2>
          <p
            className="mt-3 text-sm leading-6 sm:leading-7 lg:leading-8 sm:text-base lg:text-lg"
            style={{ color: MUTED }}
          >
            {solutionsConfig.description}
          </p>
        </div>

        <div className="z-50 grid items-stretch w-full mx-auto grid-cols-1 my-8 gap-5 sm:gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {solutionsConfig.items.length === 0 ? (
            <p style={{ color: FAINT }}>{solutionsConfig.noSolutions}</p>
          ) : (
            solutionsConfig.items.map((project, index) => (
              <a
                key={index}
                href={project.href}
                className="relative flex flex-col items-stretch duration-300 ease-out p-4 sm:p-3 group h-[22rem] sm:h-[25rem] rounded-2xl"
              >
                <span
                  className="absolute inset-0 z-20 block w-full h-full duration-300 ease-out border border-dashed group-hover:-translate-x-1 group-hover:-translate-y-1 rounded-2xl transition-colors"
                  style={{
                    borderColor: "transparent",
                    backgroundColor: "transparent",
                  }}
                />
                <span
                  className="absolute inset-0 z-10 block w-full h-full duration-300 ease-out border border-dashed group-hover:translate-x-1 group-hover:translate-y-1 rounded-2xl"
                  style={{ borderColor: HAIRLINE }}
                />
                <span className="relative z-30 block duration-300 ease-out group-hover:-translate-x-1 group-hover:-translate-y-1">
                  <span className="block w-full">
                    <img
                      src={project.imageUrl}
                      alt={project.title}
                      loading="lazy"
                      className="w-full h-auto rounded-lg aspect-[16/9] object-cover"
                    />
                  </span>
                  <span className="block w-full px-1 mt-5 mb-1 sm:mt-3">
                    <span
                      className="flex items-center mb-0 text-base font-semibold tracking-tight"
                      style={{ color: INK }}
                    >
                      <span>{project.title}</span>
                      <svg
                        className="group-hover:translate-x-0 group-hover:translate-y-0 -rotate-45 translate-y-1 -translate-x-1 w-2.5 h-2.5 ml-1 transition-all ease-in-out duration-200 transform"
                        viewBox="0 0 13 15"
                      >
                        <g
                          strokeWidth="1"
                          fillRule="evenodd"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                        >
                          <g transform="translate(0.666667, 2.333333)" strokeWidth="2.4">
                            <polyline
                              className="transition-all duration-200 ease-out opacity-0 delay-0 group-hover:opacity-100"
                              points="5.33333333 0 10.8333333 5.5 5.33333333 11"
                            />
                            <line
                              className="transition-all duration-200 ease-out transform -translate-x-1 opacity-0 group-hover:translate-x-0 group-hover:opacity-100"
                              x1="10.8333333"
                              y1="5.5"
                              x2="0.833333333"
                              y2="5.16666667"
                            />
                          </g>
                        </g>
                      </svg>
                    </span>
                    <span
                      className="text-sm block truncate-2-lines"
                      style={{ color: MUTED }}
                    >
                      {project.description}
                    </span>
                  </span>
                </span>
              </a>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
