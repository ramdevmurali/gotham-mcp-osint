import { NextResponse } from "next/server";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8001";

export async function POST(request: Request) {
  const payload = await request.json();

  const response = await fetch(`${API_BASE}/agents/company-insight`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  const text = await response.text();
  try {
    const data = JSON.parse(text);
    return NextResponse.json(data, { status: response.status });
  } catch {
    return NextResponse.json({ raw: text }, { status: response.status });
  }
}
