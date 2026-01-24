"use client";

import { useState } from "react";

type Profile = {
  name: string;
  labels: string[];
  properties: Record<string, unknown>;
  sources: { url?: string; created_at?: number }[];
  related: { name?: string; labels?: string[]; type?: string }[];
};

type Competitor = { competitor: string; reason?: string; source?: string };

type Insight = {
  profile?: Profile | null;
  competitors?: Competitor[];
  profile_result?: unknown;
  competitor_result?: unknown;
  status?: string;
};

export default function CompanyProfile() {
  const [name, setName] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [insight, setInsight] = useState<Insight | null>(null);

  const runInsight = async () => {
    const target = name.trim();
    if (!target) return;
    setLoading(true);
    setError(null);
    setInsight(null);
    try {
      const res = await fetch("/api/agents/company-insight", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ company: target }),
      });
      if (!res.ok) throw new Error(`Insight failed: ${res.status}`);
      const data = (await res.json()) as Insight;
      setInsight(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Insight failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="reveal delay-2 rounded-3xl border border-[var(--surface-border)] bg-[var(--surface-bg)] p-6 text-[var(--surface-ink)] shadow-lg backdrop-blur">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:gap-4">
        <input
          className="w-full rounded-2xl border border-[var(--surface-border)] bg-[var(--surface-bg-strong)] px-4 py-2 text-sm text-[var(--surface-ink)] outline-none"
          placeholder="Enter company (e.g., Siemens AG)"
          value={name}
          onChange={(e) => setName(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") runInsight();
          }}
        />
        <button
          className="h-10 rounded-full bg-[var(--surface-ink)] px-4 text-xs font-semibold text-white transition hover:-translate-y-0.5 hover:shadow-lg disabled:opacity-60"
          onClick={runInsight}
          disabled={loading || !name.trim()}
        >
          {loading ? "Running..." : "Run company insight"}
        </button>
      </div>

      {error ? (
        <div className="mt-3 rounded-2xl border border-[var(--surface-border)] bg-[var(--surface-bg-soft)] px-4 py-2 text-xs text-[var(--surface-ink)]">
          {error}
        </div>
      ) : null}

      {insight?.profile ? (
        <div className="mt-4 space-y-3">
          <div>
            <p className="text-[0.65rem] uppercase tracking-[0.28em] text-[var(--surface-muted)]">Profile</p>
            <p className="text-lg font-semibold">{insight.profile.name}</p>
            <p className="text-xs text-[var(--surface-muted)]">{insight.profile.labels?.join(" • ")}</p>
          </div>
          <div className="grid gap-2 text-sm text-[var(--surface-ink)]">
            {Object.entries(insight.profile.properties || {})
              .filter(([k]) => k !== "name")
              .slice(0, 6)
              .map(([k, v]) => (
                <div key={k} className="flex items-center gap-2 text-[var(--surface-muted)]">
                  <span className="uppercase text-[0.65rem] tracking-[0.2em]">{k}</span>
                  <span className="text-[var(--surface-ink)]">{String(v)}</span>
                </div>
              ))}
          </div>
          {insight.profile.related?.length ? (
            <div>
              <p className="text-[0.65rem] uppercase tracking-[0.28em] text-[var(--surface-muted)]">Related</p>
              <div className="flex flex-wrap gap-2 text-sm">
                {insight.profile.related.slice(0, 8).map((r, idx) => (
                  <span
                    key={`${r.name}-${idx}`}
                    className="rounded-full bg-[var(--surface-bg-strong)] px-3 py-1 text-[var(--surface-ink)]"
                  >
                    {r.name} {r.type ? `• ${r.type}` : ""}
                  </span>
                ))}
              </div>
            </div>
          ) : null}
          {insight.profile.sources?.length ? (
            <div className="space-y-1">
              <p className="text-[0.65rem] uppercase tracking-[0.28em] text-[var(--surface-muted)]">Sources</p>
              <ul className="space-y-1 text-sm">
                {insight.profile.sources.slice(0, 4).map((s, idx) => (
                  <li key={idx} className="truncate text-[var(--surface-ink)]">
                    {s.url}
                  </li>
                ))}
              </ul>
            </div>
          ) : null}
        </div>
      ) : null}

      {insight?.competitors?.length ? (
        <div className="mt-4 space-y-2">
          <p className="text-[0.65rem] uppercase tracking-[0.28em] text-[var(--surface-muted)]">Competitors</p>
          <ul className="space-y-2 text-sm text-[var(--surface-ink)]">
            {insight.competitors.map((c, idx) => (
              <li key={`${c.competitor}-${idx}`}>
                <span className="font-semibold">{c.competitor}</span>
                {c.reason ? ` — ${c.reason}` : ""}
                {c.source ? (
                  <>
                    {" "}
                    <a className="text-[var(--surface-ink)] underline" href={c.source} target="_blank" rel="noreferrer">
                      source
                    </a>
                  </>
                ) : null}
              </li>
            ))}
          </ul>
        </div>
      ) : null}
    </div>
  );
}
