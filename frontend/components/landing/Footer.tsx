export default function Footer() {
  return (
    <footer className="border-t border-card-border py-12 px-4">
      <div className="max-w-5xl mx-auto text-center space-y-4">
        <p className="text-foreground font-semibold">MedResearch Mind</p>
        <p className="text-sm text-muted">
          The Research Brain for Medical AI
        </p>
        <div className="flex items-center justify-center gap-6 text-sm text-muted">
          <a href="#" className="hover:text-accent transition-colors">
            GitHub
          </a>
          <a href="#" className="hover:text-accent transition-colors">
            LinkedIn
          </a>
          <a href="#" className="hover:text-accent transition-colors">
            Twitter
          </a>
        </div>
        <div className="flex items-center justify-center gap-6 text-xs text-zinc-600">
          <a href="/privacy" className="hover:text-muted transition-colors">
            Privacy Policy
          </a>
          <a href="/terms" className="hover:text-muted transition-colors">
            Terms of Service
          </a>
        </div>
        <p className="text-xs text-zinc-700">
          &copy; 2024-2026 MedResearch Mind. All rights reserved.
        </p>
      </div>
    </footer>
  );
}
