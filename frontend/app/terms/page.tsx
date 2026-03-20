export default function TermsPage() {
  return (
    <div className="min-h-screen p-6 max-w-3xl mx-auto">
      <a href="/" className="text-accent text-sm mb-4 inline-block">&larr; Home</a>
      <h1 className="text-3xl font-bold mb-8">Terms of Service</h1>
      <div className="prose prose-invert prose-sm max-w-none space-y-6 text-muted">
        <p>Last updated: March 2026</p>

        <h2 className="text-foreground text-lg font-semibold">1. Not Medical Advice</h2>
        <p>MedResearch Mind is a research intelligence tool. It is NOT a medical device, clinical decision-support system, or diagnostic tool. Outputs should not be used for patient care. The tool is intended for research purposes only — literature review, gap identification, and experiment design.</p>

        <h2 className="text-foreground text-lg font-semibold">2. Acceptable Use</h2>
        <p>You may use MedResearch Mind for: academic research, literature review, identifying research directions, designing experiments, and benchmarking AI models. You may NOT use it for: clinical decision-making, patient diagnosis, generating fraudulent research, or any illegal purpose.</p>

        <h2 className="text-foreground text-lg font-semibold">3. Data Ownership</h2>
        <p>You retain ownership of all papers you upload and queries you make. By using the service, you grant us a license to process your data for service delivery and to use anonymized interaction data for AI model training.</p>

        <h2 className="text-foreground text-lg font-semibold">4. Accuracy</h2>
        <p>While we strive for zero hallucination, AI outputs may contain errors. Always verify citations, statistics, and clinical claims against original sources. We are not liable for decisions made based on our outputs.</p>

        <h2 className="text-foreground text-lg font-semibold">5. Service Tiers</h2>
        <p>Free tier: 10 papers, 20 queries/month. Pro ($9/month): 100 papers, unlimited queries. Lab ($29/month): unlimited, team workspace. We reserve the right to modify tier limits with 30 days notice.</p>

        <h2 className="text-foreground text-lg font-semibold">6. Termination</h2>
        <p>We may suspend accounts that violate these terms. You may delete your account at any time, which will remove all your data within 30 days.</p>

        <h2 className="text-foreground text-lg font-semibold">7. Contact</h2>
        <p>Shubh Garg — legal@medresearchmind.app<br/>Thapar Institute of Engineering and Technology</p>
      </div>
    </div>
  );
}
