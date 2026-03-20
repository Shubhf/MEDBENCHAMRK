export default function GapReportEmail({ topic = "", gapCount = 0 }: { topic?: string; gapCount?: number }) {
  return (
    <div style={{ fontFamily: "Inter, sans-serif", maxWidth: 600, margin: "0 auto", backgroundColor: "#0a0a0a", color: "#fafafa", padding: 32 }}>
      <h1 style={{ color: "#0ea5e9", fontSize: 24 }}>Your Gap Report is Ready</h1>
      <p>Your analysis on <strong>{topic}</strong> found <strong>{gapCount} research gaps</strong>.</p>
      <p>Each gap includes evidence quotes, clinical relevance scores, and PICO experiment proposals.</p>
      <a href="https://medresearchmind.app/gaps" style={{ display: "inline-block", padding: "12px 24px", backgroundColor: "#0ea5e9", color: "white", borderRadius: 8, textDecoration: "none", fontWeight: 600 }}>
        View Gap Report
      </a>
      <p style={{ color: "#a1a1aa", fontSize: 14, marginTop: 24 }}>Found a gap you want to pursue? Click &quot;Accept&quot; to help us improve future suggestions.</p>
    </div>
  );
}
