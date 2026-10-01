import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: "Devil's Advocate Research Agent",
  description: "AI-powered multi-agent research system that stress-tests claims with pro and counter evidence",
  keywords: ["research", "AI", "fact-checking", "evidence", "devil's advocate"],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      </head>
      <body>{children}</body>
    </html>
  );
}
