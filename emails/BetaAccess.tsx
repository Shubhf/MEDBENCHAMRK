export default function BetaAccessEmail({ name = "Researcher" }: { name?: string }) {
  return (
    <div style={{ fontFamily: "Inter, sans-serif", maxWidth: 600, margin: "0 auto", backgroundColor: "#0a0a0a", color: "#fafafa", padding: 32 }}>
      <h1 style={{ color: "#0ea5e9", fontSize: 24 }}>You&apos;re In!</h1>
      <p>Hi {name},</p>
      <p>Your beta access to MedResearch Mind is ready.</p>
      <p>As a beta user, you get Pro features free for 30 days — 100 papers, unlimited queries, full gap reports, and PICO experiment design.</p>
      <a href="https://medresearchmind.app/auth/signup" style={{ display: "inline-block", padding: "12px 24px", backgroundColor: "#0ea5e9", color: "white", borderRadius: 8, textDecoration: "none", fontWeight: 600 }}>
        Activate Beta Access
      </a>
      <p style={{ color: "#a1a1aa", fontSize: 14, marginTop: 32 }}>I&apos;d love your honest feedback. Reply with what works and what doesn&apos;t.<br/>— Shubh</p>
    </div>
  );
}
