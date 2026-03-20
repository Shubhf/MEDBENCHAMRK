export default function PrivacyPage() {
  return (
    <div className="min-h-screen p-6 max-w-3xl mx-auto">
      <a href="/" className="text-accent text-sm mb-4 inline-block">&larr; Home</a>
      <h1 className="text-3xl font-bold mb-8">Privacy Policy</h1>
      <div className="prose prose-invert prose-sm max-w-none space-y-6 text-muted">
        <p>Last updated: March 2026</p>

        <h2 className="text-foreground text-lg font-semibold">1. Information We Collect</h2>
        <p>We collect: account information (name, email, institution), research papers you upload, queries you make, and interaction data (which gaps you accept or reject).</p>

        <h2 className="text-foreground text-lg font-semibold">2. How We Use Your Data</h2>
        <p>Your data is used to: provide the service, improve our AI models, and generate anonymized training data. We never share your uploaded papers with other users. Training data is anonymized with one-way hashing — we never store your email alongside interaction logs.</p>

        <h2 className="text-foreground text-lg font-semibold">3. Training Data</h2>
        <p>When you accept or reject a research gap suggestion, that interaction is logged as anonymized training data to improve our AI model (MedResearchSLM). Your user identity is irreversibly hashed. The training data includes: the gap suggestion, your decision, and medical metadata (modality, anatomy, condition). It does not include your name, email, or institution.</p>

        <h2 className="text-foreground text-lg font-semibold">4. Data Storage</h2>
        <p>Data is stored on Supabase (hosted on AWS). Uploaded PDFs are stored in Supabase Storage with access restricted to your account. We use row-level security to ensure users can only access their own data.</p>

        <h2 className="text-foreground text-lg font-semibold">5. Third-Party Services</h2>
        <p>We use: Supabase (database, auth, storage), Groq (LLM inference — your queries are sent for processing), Ollama (local embeddings — no data leaves your session), Resend (email). We do not sell data to third parties.</p>

        <h2 className="text-foreground text-lg font-semibold">6. Medical Disclaimer</h2>
        <p>MedResearch Mind is a research tool, not a clinical decision-support system. It should not be used for patient care, diagnosis, or treatment decisions. All outputs are for research purposes only.</p>

        <h2 className="text-foreground text-lg font-semibold">7. Your Rights</h2>
        <p>You can: export your data, delete your account and all associated data, opt out of training data collection (contact us). To exercise these rights, email privacy@medresearchmind.app.</p>

        <h2 className="text-foreground text-lg font-semibold">8. Contact</h2>
        <p>Shubh Garg — privacy@medresearchmind.app<br/>Thapar Institute of Engineering and Technology</p>
      </div>
    </div>
  );
}
