'use client';

import { useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { Search, Zap, Shield, Scale, ArrowRight, ChevronRight, Brain } from 'lucide-react';
import { createJob } from '@/lib/api';

const EXAMPLE_CLAIMS = [
  "Coffee consumption significantly reduces the risk of type 2 diabetes.",
  "Remote work increases employee productivity compared to office work.",
  "Social media usage is a primary driver of teenage mental health decline.",
  "Electric vehicles have a lower lifetime carbon footprint than gasoline cars.",
];

export default function HomePage() {
  const router = useRouter();
  const [claim, setClaim] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    if (!claim.trim() || claim.length < 10) return;

    setIsLoading(true);
    setError(null);
    try {
      const job = await createJob(claim.trim());
      router.push(`/research/${job.job_id}`);
    } catch (err: any) {
      setError(err.message || 'Failed to start research. Check backend is running.');
      setIsLoading(false);
    }
  }, [claim, router]);

  const handleExample = (example: string) => {
    setClaim(example);
  };

  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Animated background orbs */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -left-40 w-96 h-96 bg-brand-600/20 rounded-full blur-3xl animate-pulse-slow" />
        <div className="absolute top-1/3 -right-32 w-80 h-80 bg-purple-600/15 rounded-full blur-3xl animate-pulse-slow" style={{ animationDelay: '2s' }} />
        <div className="absolute bottom-0 left-1/3 w-64 h-64 bg-brand-800/20 rounded-full blur-3xl animate-pulse-slow" style={{ animationDelay: '4s' }} />
      </div>

      {/* Grid overlay */}
      <div
        className="absolute inset-0 opacity-[0.03]"
        style={{
          backgroundImage: 'linear-gradient(rgba(255,255,255,.15) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.15) 1px, transparent 1px)',
          backgroundSize: '50px 50px',
        }}
      />

      <div className="relative z-10 flex flex-col min-h-screen">
        {/* Header */}
        <header className="flex items-center justify-between px-8 py-6">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 bg-gradient-to-br from-brand-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg shadow-brand-600/30">
              <Scale className="w-5 h-5 text-white" />
            </div>
            <span className="font-bold text-lg tracking-tight">Devil&apos;s Advocate</span>
          </div>
          <nav className="hidden md:flex items-center gap-6 text-sm text-white/60">
            <a href="/history" className="hover:text-white transition-colors">History</a>
            <a href="/docs" className="hover:text-white transition-colors">API Docs</a>
          </nav>
        </header>

        {/* Hero */}
        <main className="flex-1 flex flex-col items-center justify-center px-4 py-16 text-center">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-brand-600/15 border border-brand-400/30 text-brand-300 text-sm font-medium mb-8 animate-fade-in">
            <Zap className="w-3.5 h-3.5" />
            AI-Powered Multi-Agent Research
          </div>

          {/* Headline */}
          <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight mb-6 animate-slide-up">
            <span className="gradient-text">Stress-Test</span>
            <br />
            <span className="text-white">Any Claim</span>
          </h1>

          <p className="text-lg md:text-xl text-white/50 max-w-2xl mb-12 leading-relaxed animate-slide-up" style={{ animationDelay: '0.1s' }}>
            Our AI agents research both sides of any claim — finding supporting evidence 
            and challenging counter-arguments — then score your claim&apos;s credibility.
          </p>

          {/* Input Form */}
          <form
            onSubmit={handleSubmit}
            className="w-full max-w-2xl space-y-4 animate-slide-up"
            style={{ animationDelay: '0.2s' }}
          >
            <div className="relative group">
              <div className="absolute -inset-0.5 bg-gradient-to-r from-brand-600 to-purple-600 rounded-2xl opacity-0 group-focus-within:opacity-100 transition-opacity duration-300 blur-sm" />
              <div className="relative glass-card p-1">
                <textarea
                  id="claim-input"
                  value={claim}
                  onChange={(e) => setClaim(e.target.value)}
                  placeholder="Enter a claim to research... e.g. 'Coffee consumption reduces the risk of type 2 diabetes'"
                  className="w-full bg-transparent px-5 py-4 text-white placeholder-white/30 resize-none focus:outline-none text-base leading-relaxed"
                  rows={3}
                  maxLength={2000}
                  disabled={isLoading}
                />
                <div className="flex items-center justify-between px-4 pb-3">
                  <span className="text-xs text-white/30">{claim.length}/2000</span>
                  <button
                    id="submit-research-btn"
                    type="submit"
                    disabled={isLoading || claim.trim().length < 10}
                    className="btn-primary text-sm px-5 py-2.5"
                  >
                    {isLoading ? (
                      <>
                        <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                        Starting...
                      </>
                    ) : (
                      <>
                        <Search className="w-4 h-4" />
                        Research This
                        <ArrowRight className="w-4 h-4" />
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>

            {error && (
              <div className="glass-card p-4 border-counter-500/30 bg-counter-500/10 text-counter-300 text-sm text-left">
                ⚠️ {error}
              </div>
            )}
          </form>

          {/* Example claims */}
          <div className="mt-8 w-full max-w-2xl animate-slide-up" style={{ animationDelay: '0.3s' }}>
            <p className="text-xs text-white/30 uppercase tracking-widest mb-3">Try an example</p>
            <div className="flex flex-col gap-2">
              {EXAMPLE_CLAIMS.map((example, i) => (
                <button
                  key={i}
                  id={`example-claim-${i}`}
                  onClick={() => handleExample(example)}
                  className="text-left glass-card-hover px-4 py-3 text-sm text-white/60 hover:text-white/90 flex items-center gap-3 group"
                >
                  <ChevronRight className="w-4 h-4 text-brand-400 opacity-0 group-hover:opacity-100 transition-opacity shrink-0" />
                  {example}
                </button>
              ))}
            </div>
          </div>

          {/* Feature chips */}
          <div className="mt-16 flex flex-wrap items-center justify-center gap-4 animate-fade-in" style={{ animationDelay: '0.4s' }}>
            {[
              { icon: Brain, label: 'LangGraph Orchestration' },
              { icon: Shield, label: 'Adversarial Counter-Search' },
              { icon: Scale, label: 'Confidence Scoring' },
              { icon: Zap, label: 'Real-time Streaming' },
            ].map(({ icon: Icon, label }) => (
              <div key={label} className="flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10 text-white/50 text-xs">
                <Icon className="w-3.5 h-3.5 text-brand-400" />
                {label}
              </div>
            ))}
          </div>
        </main>

        {/* Footer */}
        <footer className="text-center py-6 text-white/20 text-xs">
          Devil&apos;s Advocate Research Agent · MVP v1.0
        </footer>
      </div>
    </div>
  );
}
