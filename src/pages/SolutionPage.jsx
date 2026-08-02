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
    "Here you can showcase your best work. Each project should include a brief description, the technologies used, and any notable achievements. This helps potential clients or employers understand your capabilities.",
  backButton: "Back to Home",
  noSolutions: "No solutions found.",
  items: [
    {
      title: "Solution One",
      description:
        "A brief description of your first project. Explain what it does and what technologies you used.",
      href: "#!",
      imageUrl: "/static/building-business.jpg",
    },
    {
      title: "Solution Two",
      description:
        "Describe your second project here. Highlight the key features and your role in development.",
      href: "#!",
      imageUrl: "/static/project6.png",
    },
    {
      title: "Solution Three",
      description:
        "Share details about your third project. What problems did it solve? What was the outcome?",
      href: "#!",
      imageUrl: "/static/project1.jpg",
    },
  ],
};

export default function SolutionPage() {
  return (
    <div className="relative min-h-screen px-[3.75rem] py-20 text-white">
      <StarBackground />
      <div className="relative z-10">
        <div className="flex items-start justify-between mb-10">
          <header className="mb-10">
            <a className="inline-block">
              <ArchNotionsLogo className="mb-1 w-128" />
            </a>
            <h1
              className="font-bold text-2xl md:text-1xl lg:text-1xl"
              style={{ color: INK }}
            >
              Establish, Growth, &amp; Sustain with Us
            </h1>
          </header>
          <NavBar current="Solution" />
        </div>

        <div className="relative z-20 w-full max-w-5xl mx-auto">
          <h2
            className="text-2xl font-bold tracking-tight sm:text-3xl lg:text-4xl"
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

        <div className="z-50 grid items-stretch w-full max-w-5xl mx-auto grid-cols-1 my-8 gap-7 sm:gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {solutionsConfig.items.length === 0 ? (
            <p style={{ color: FAINT }}>{solutionsConfig.noSolutions}</p>
          ) : (
            solutionsConfig.items.map((project, index) => (
              <a
                key={index}
                href={project.href}
                className="relative flex flex-col items-stretch duration-300 ease-out p-7 sm:p-3 group h-[25rem] rounded-2xl"
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
                        xmlns="http://www.w3.org/2000/svg"
                        style={{ stroke: BRASS, fill: "none" }}
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
                      className="text-sm block truncate"
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
