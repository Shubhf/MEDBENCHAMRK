// Welcome Email Template — React Email compatible
export default function WelcomeEmail({ name = "Researcher" }: { name?: string }) {
  return (
    <div style={{ fontFamily: "Inter, sans-serif", maxWidth: 600, margin: "0 auto", backgroundColor: "#0a0a0a", color: "#fafafa", padding: 32 }}>
      <h1 style={{ color: "#0ea5e9", fontSize: 24 }}>Welcome to MedResearch Mind</h1>
      <p>Hi {name},</p>
      <p>Thanks for joining MedResearch Mind — the research brain for medical AI.</p>
      <p>Here&apos;s how to get started:</p>
      <ol>
        <li><strong>Upload papers</strong> — PubMed links, ArXiv papers, MICCAI talks, or PDFs</li>
        <li><strong>Find gaps</strong> — Select 5+ papers and click &quot;Find Gaps&quot;</li>
        <li><strong>Design experiments</strong> — Get PICO-formatted proposals from any gap</li>
      </ol>
      <a href="https://medresearchmind.app/dashboard" style={{ display: "inline-block", padding: "12px 24px", backgroundColor: "#0ea5e9", color: "white", borderRadius: 8, textDecoration: "none", fontWeight: 600 }}>
        Go to Dashboard
      </a>
      <p style={{ color: "#a1a1aa", fontSize: 14, marginTop: 32 }}>
        Built by Shubh Garg — 11 published medical AI papers.<br/>
        Questions? Reply to this email.
      </p>
    </div>
  );
}
