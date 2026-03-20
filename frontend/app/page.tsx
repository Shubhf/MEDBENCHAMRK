import Hero from "@/components/landing/Hero";
import SocialProof from "@/components/landing/SocialProof";
import Features from "@/components/landing/Features";
import WhyMedicalAI from "@/components/landing/WhyMedicalAI";
import HowItWorks from "@/components/landing/HowItWorks";
import Benchmark from "@/components/landing/Benchmark";
import Pricing from "@/components/landing/Pricing";
import EmailCapture from "@/components/landing/EmailCapture";
import Footer from "@/components/landing/Footer";

export default function LandingPage() {
  return (
    <main className="min-h-screen">
      <Hero />
      <SocialProof />
      <Features />
      <WhyMedicalAI />
      <HowItWorks />
      <Benchmark />
      <Pricing />
      <EmailCapture />
      <Footer />
    </main>
  );
}
