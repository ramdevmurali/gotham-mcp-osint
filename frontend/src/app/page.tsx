import MissionConsole from "@/components/layout/mission-console";
import FeatureCard from "@/components/ui/feature-card";
import Pill from "@/components/ui/pill";
import StatCard from "@/components/ui/stat-card";
import StatusPill from "@/components/ui/status-pill";
import ThemeToggle from "@/components/ui/theme-toggle";
import { featureCards, missionHighlights, stats } from "@/lib/content";

export default function Home() {
  return (
    <div className="page-shell">
      <div className="float-glow one" />
      <div className="float-glow two" />
      <div className="grain" />

      <main className="relative mx-auto flex w-full max-w-6xl flex-col gap-20 px-6 pb-24 pt-10 sm:px-10 lg:px-16">
        <nav className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="h-10 w-10 rounded-2xl bg-[var(--ink)] text-[var(--parchment)] flex items-center justify-center font-semibold">
              G
            </span>
            <div>
              <p className="text-xs uppercase tracking-[0.32em] text-[var(--ink-muted)]">
                Project Gotham
              </p>
              <p className="font-[var(--font-display)] text-lg text-[var(--ink)]">
                Intelligence Console
              </p>
            </div>
          </div>
          <StatusPill label="Live graph ingest" />
          <ThemeToggle />
        </nav>

        <section className="grid gap-12 lg:grid-cols-[1.1fr_0.9fr] lg:items-center">
          <div className="flex flex-col gap-8">
            <Pill>OSINT missions → Graph entities</Pill>
            <div className="space-y-6">
              <h1 className="reveal delay-1 font-[var(--font-display)] text-4xl leading-tight text-[var(--ink)] sm:text-5xl lg:text-6xl">
                Turn open-source signals into a living intelligence graph.
              </h1>
              <p className="reveal delay-2 text-base leading-7 text-[var(--ink-muted)] sm:text-lg">
                Project Gotham stitches sources, entities, and relationships in real time.
                Drop a mission, watch the graph populate, and keep every source traceable.
              </p>
            </div>
            <div className="reveal delay-3 flex flex-wrap items-center gap-4">
              <button className="h-12 rounded-full bg-[var(--ink)] px-6 text-sm font-semibold text-[var(--parchment)] transition hover:-translate-y-0.5 hover:shadow-lg">
                Launch a mission
              </button>
              <button className="h-12 rounded-full border border-[var(--fog)] bg-white/70 px-6 text-sm font-semibold text-[var(--ink)] transition hover:-translate-y-0.5 hover:shadow-lg">
                View sample graph
              </button>
              <div className="text-xs font-semibold uppercase tracking-[0.3em] text-[var(--ink-muted)]">
                Aura-ready • MCP tools • Neo4j
              </div>
            </div>
            <div className="grid gap-4 sm:grid-cols-3">
              {stats.map((stat) => (
                <StatCard key={stat.label} value={stat.value} label={stat.label} />
              ))}
            </div>
          </div>

          <MissionConsole highlights={missionHighlights} />
        </section>

        <section className="grid gap-6 lg:grid-cols-3">
          {featureCards.map((card, index) => (
            <FeatureCard
              key={card.title}
              title={card.title}
              copy={card.copy}
              delay={index + 1}
            />
          ))}
        </section>
      </main>
    </div>
  );
}
