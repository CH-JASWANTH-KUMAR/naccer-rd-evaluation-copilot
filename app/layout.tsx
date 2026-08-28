import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "NaCCER R&D Evaluation Copilot | Enterprise Proposal Platform",
  description: "Production-oriented AI/ML R&D Proposal Evaluation platform base foundation for NaCCER/CMPDI technical reviewers.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full">
      <body className="h-full bg-slate-50 text-slate-900 antialiased font-sans">
        {children}
      </body>
    </html>
  );
}
