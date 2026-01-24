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

export default function CompanyProfile() {
  const [name, setName] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [profile, setProfile] = useState<Profile | null>(null);
  const [competitors, setCompetitors] = useState<Competitor[]>([]);
  const [loadingComp, setLoadingComp] = useState(false);

  const fetchProfile = async () => {
    if (!name.trim()) return;
    setLoading(true);
    setError(null);
    setProfile(null);
    setCompetitors([]);
    try {
      const res = await fetch(`/api/graph-profile?name=${encodeURIComponent(name)}`);
      if (!res.ok) throw new Error(`Profile failed: ${res.status}`);
      const data = (await res.json()) as Profile;
      setProfile(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Profile failed");
    } finally {
      setLoading(false);
    }
  };

  const runCompetitors = async () => {
    const target = profile?.name || name.trim();
    if (!target) return;
    setLoadingComp(true);
    setError(null);
    try {
      // Trigger agent to fetch and write competitors
      await fetch("/api/agents/competitors", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ company: target }),
      });
      // Then read from graph
      const res = await fetch(`/api/graph-competitors?company=${encodeURIComponent(target)}`);
      if (!res.ok) throw new Error(`Competitors failed: ${res.status}`);
      const data = (await res.json()) as { competitors?: Competitor[] };
      setCompetitors(data.competitors ?? []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Competitors failed");
    } finally {
      setLoadingComp(false);
    }
  };

  return (
    <div className="reveal delay-2 rounded-3xl border border-[var(--surface-border)] bg-[var(--surface-bg)] p-6 text-[var(--surface-ink)] shadow-lg backdrop-blur">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:gap-4">
        <input
          className="w-full rounded-2xl border border-[var(--surface-border)] bg-[var(--surface-bg-strong)] px-4 py-2 text-sm text-[var(--surface-ink)] outline-none"
          placeholder="Search company (e.g., Siemens AG)"
          value={name}
          onChange={(e) => setName(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") fetchProfile();
          }}
        />
        <button
          className="h-10 rounded-full bg-[var(--surface-ink)] px-4 text-xs font-semibold text-white transition hover:-translate-y-0.5 hover:shadow-lg disabled:opacity-60"
          onClick={fetchProfile}
          disabled={loading}
        >
          {loading ? "Loading..." : "View profile"}
        </button>
        <button
          className="h-10 rounded-full border border-[var(--surface-border)] bg-[var(--surface-bg-strong)] px-4 text-xs font-semibold text-[var(--surface-ink)] transition hover:-translate-y-0.5 hover:shadow-lg disabled:opacity-60"
          onClick={runCompetitors}
          disabled={loadingComp || (!profile && !name.trim())}
        >
          {loadingComp ? "Finding..." : "View competitors"}
        </button>
      </div>

      {error ? (
        <div className="mt-3 rounded-2xl border border-[var(--surface-border)] bg-[var(--surface-bg-soft)] px-4 py-2 text-xs text-[var(--surface-ink)]">
          {error}
        </div>
      ) : null}

      {profile ? (
        <div className="mt-4 space-y-3">
          <div>
            <p className="text-[0.65rem] uppercase tracking-[0.28em] text-[var(--surface-muted)]">Profile</p>
            <p className="text-lg font-semibold">{profile.name}</p>
            <p className="text-xs text-[var(--surface-muted)]">{profile.labels?.join(" • ")}</p>
          </div>
          <div className="grid gap-2 text-sm text-[var(--surface-ink)]">
            {Object.entries(profile.properties || {})
              .filter(([k]) => k !== "name")
              .slice(0, 6)
              .map(([k, v]) => (
                <div key={k} className="flex items-center gap-2 text-[var(--surface-muted)]">
                  <span className="uppercase text-[0.65rem] tracking-[0.2em]">{k}</span>
                  <span className="text-[var(--surface-ink)]">{String(v)}</span>
                </div>
              ))}
          </div>
          {profile.related?.length ? (
            <div>
              <p className="text-[0.65rem] uppercase tracking-[0.28em] text-[var(--surface-muted)]">Related</p>
              <div className="flex flex-wrap gap-2 text-sm">
                {profile.related.slice(0, 8).map((r, idx) => (
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
          {profile.sources?.length ? (
            <div className="space-y-1">
              <p className="text-[0.65rem] uppercase tracking-[0.28em] text-[var(--surface-muted)]">Sources</p>
              <ul className="space-y-1 text-sm">
                {profile.sources.slice(0, 4).map((s, idx) => (
                  <li key={idx} className="truncate text-[var(--surface-ink)]">
                    {s.url}
                  </li>
                ))}
              </ul>
            </div>
          ) : null}
        </div>
      ) : null}

      {competitors.length ? (
        <div className="mt-4 space-y-2">
          <p className="text-[0.65rem] uppercase tracking-[0.28em] text-[var(--surface-muted)]">Competitors</p>
          <ul className="space-y-2 text-sm text-[var(--surface-ink)]">
            {competitors.map((c, idx) => (
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
