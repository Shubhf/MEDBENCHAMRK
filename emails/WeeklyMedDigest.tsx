export default function WeeklyDigest({ papers = [] as any[], gaps = [] as any[] }) {
  return (
    <div style={{ fontFamily: "Inter, sans-serif", maxWidth: 600, margin: "0 auto", backgroundColor: "#0a0a0a", color: "#fafafa", padding: 32 }}>
      <h1 style={{ color: "#0ea5e9", fontSize: 24 }}>Your Weekly Medical AI Digest</h1>
      <p>Here&apos;s what&apos;s new in your research areas this week:</p>
      <h2 style={{ fontSize: 18, marginTop: 24 }}>New Papers</h2>
      {papers.length === 0 ? <p style={{ color: "#a1a1aa" }}>No new papers found this week.</p> : papers.map((p: any, i: number) => (
        <div key={i} style={{ borderBottom: "1px solid #27272a", padding: "8px 0" }}>
          <p style={{ fontWeight: 600, fontSize: 14 }}>{p.title}</p>
          <p style={{ color: "#a1a1aa", fontSize: 12 }}>{p.venue} | {p.modality}</p>
        </div>
      ))}
      <h2 style={{ fontSize: 18, marginTop: 24 }}>Emerging Gaps</h2>
      {gaps.length === 0 ? <p style={{ color: "#a1a1aa" }}>Continue uploading papers to discover gaps.</p> : gaps.map((g: any, i: number) => (
        <p key={i} style={{ fontSize: 14 }}>&bull; {g.description}</p>
      ))}
      <a href="https://medresearchmind.app/dashboard" style={{ display: "inline-block", padding: "12px 24px", backgroundColor: "#0ea5e9", color: "white", borderRadius: 8, textDecoration: "none", fontWeight: 600, marginTop: 16 }}>
        Open Dashboard
      </a>
    </div>
  );
}
