"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { UploadCloud, ArrowLeft, CheckCircle2, AlertCircle, FileText, Loader2 } from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { RESEARCH_DOMAINS, MOCK_INSTITUTIONS } from "@/lib/constants";
import { Header } from "@/components/layout/Header";
import { Sidebar } from "@/components/layout/Sidebar";
import { proposalService } from "@/lib/api/proposals";
import { institutionService } from "@/lib/api/institutions";
import { documentService, ApiDocumentDetail } from "@/lib/api/documents";
import { Institution } from "@/lib/types";

export default function UploadProposalPage() {
  const router = useRouter();

  const [institutions, setInstitutions] = useState<Institution[]>([]);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  // Form State
  const [title, setTitle] = useState("");
  const [institutionId, setInstitutionId] = useState("");
  const [domain, setDomain] = useState("");
  const [piName, setPiName] = useState("");
  const [budget, setBudget] = useState("4500000");

  // Status & Progress State
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [processedDoc, setProcessedDoc] = useState<ApiDocumentDetail | null>(null);
  const [createdProposalId, setCreatedProposalId] = useState<string | null>(null);

  useEffect(() => {
    async function loadInstitutions() {
      const data = await institutionService.getInstitutions();
      setInstitutions(data);
      if (data.length > 0) {
        setInstitutionId(data[0].id);
      }
    }
    loadInstitutions();
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      if (!file.name.toLowerCase().endsWith(".pdf")) {
        setErrorMessage("Only PDF documents (.pdf) are supported.");
        setSelectedFile(null);
        return;
      }
      setErrorMessage(null);
      setSelectedFile(file);
      if (!title) {
        setTitle(file.name.replace(/\.pdf$/i, ""));
      }
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title || !institutionId || !domain || !piName) {
      setErrorMessage("Please complete all required administrative metadata fields.");
      return;
    }

    if (!selectedFile) {
      setErrorMessage("Please select a proposal PDF document to upload.");
      return;
    }

    setIsSubmitting(true);
    setErrorMessage(null);

    try {
      // 1. Create Proposal Record
      const newProposal = await proposalService.createProposal({
        title,
        institution_id: institutionId,
        principal_investigator: piName,
        domain,
        budget_total: parseFloat(budget) || 0,
      });

      setCreatedProposalId(newProposal.id);

      // 2. Upload & Process PDF Document
      const docResult = await documentService.uploadDocument(newProposal.id, selectedFile);
      setProcessedDoc(docResult);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Failed to process proposal document.";
      setErrorMessage(message);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex">
      <Sidebar />

      <div className="flex-1 flex flex-col min-w-0 lg:pl-64">
        <Header />

        <main className="flex-1 p-6 md:p-8 max-w-4xl w-full mx-auto space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between border-b border-slate-200 pb-4">
            <div>
              <Link href="/proposals" className="text-xs text-slate-500 hover:text-slate-900 flex items-center mb-1">
                <ArrowLeft className="h-3 w-3 mr-1" />
                Back to Proposals Directory
              </Link>
              <h1 className="text-xl font-bold text-slate-900 tracking-tight">
                Upload New R&amp;D Proposal
              </h1>
              <p className="text-xs text-slate-500 mt-0.5">
                Submit proposal PDF and metadata for page-aware document processing.
              </p>
            </div>
          </div>

          {/* Error Banner */}
          {errorMessage && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-md text-xs text-red-700 flex items-start space-x-2">
              <AlertCircle className="h-4 w-4 text-red-500 flex-shrink-0 mt-0.5" />
              <div>
                <span className="font-semibold">Error: </span>
                {errorMessage}
              </div>
            </div>
          )}

          {/* Processing Results Banner */}
          {processedDoc && (
            <Card className="border-emerald-200 bg-emerald-50/50">
              <CardContent className="p-6 space-y-3 text-xs">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    {processedDoc.processing_status === "PROCESSED" ? (
                      <CheckCircle2 className="h-5 w-5 text-emerald-600" />
                    ) : (
                      <AlertCircle className="h-5 w-5 text-amber-600" />
                    )}
                    <h3 className="font-bold text-slate-900 text-sm">
                      Document Processing {processedDoc.processing_status}
                    </h3>
                  </div>
                  <Badge variant={processedDoc.processing_status === "PROCESSED" ? "success" : "warning"}>
                    {processedDoc.processing_status}
                  </Badge>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 bg-white p-3 rounded-md border border-slate-200">
                  <div>
                    <span className="text-[10px] text-slate-400 uppercase font-mono block">Filename</span>
                    <span className="font-semibold text-slate-800 truncate block">{processedDoc.filename}</span>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-400 uppercase font-mono block">Extracted Pages</span>
                    <span className="font-semibold text-slate-800">{processedDoc.pages_count} pages</span>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-400 uppercase font-mono block">Sections Detected</span>
                    <span className="font-semibold text-slate-800">{processedDoc.sections_count} sections</span>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-400 uppercase font-mono block">File Size</span>
                    <span className="font-semibold text-slate-800">
                      {(processedDoc.file_size / (1024 * 1024)).toFixed(2)} MB
                    </span>
                  </div>
                </div>

                {processedDoc.processing_error && (
                  <div className="p-3 bg-amber-100/80 border border-amber-200 rounded text-amber-800">
                    <span className="font-semibold">Processing Note: </span>
                    {processedDoc.processing_error}
                  </div>
                )}

                <div className="pt-2 flex justify-end">
                  {createdProposalId && (
                    <Button size="sm" onClick={() => router.push(`/proposals/${createdProposalId}`)}>
                      Open Proposal Workspace
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          )}

          {!processedDoc && (
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* PDF Dropzone Workspace */}
              <Card className="border-2 border-dashed border-slate-300 bg-white">
                <CardContent className="p-8 flex flex-col items-center justify-center text-center cursor-pointer hover:bg-slate-50/50 transition-colors relative">
                  <input
                    type="file"
                    accept=".pdf,application/pdf"
                    onChange={handleFileChange}
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                  />
                  <div className="p-4 rounded-full bg-slate-100 mb-3">
                    {selectedFile ? (
                      <FileText className="h-8 w-8 text-blue-600" />
                    ) : (
                      <UploadCloud className="h-8 w-8 text-slate-600" />
                    )}
                  </div>
                  <h3 className="text-sm font-bold text-slate-900">
                    {selectedFile ? selectedFile.name : "Drag & Drop Technical Proposal PDF"}
                  </h3>
                  <p className="text-xs text-slate-500 mt-1 max-w-sm">
                    {selectedFile
                      ? `${(selectedFile.size / (1024 * 1024)).toFixed(2)} MB PDF selected`
                      : "Supports PDF proposals up to 50MB. Text will be extracted page-by-page."}
                  </p>
                  <Button type="button" variant="outline" size="sm" className="mt-4 pointer-events-none">
                    {selectedFile ? "Change PDF File" : "Select File from Device"}
                  </Button>
                </CardContent>
              </Card>

              {/* Proposal Metadata Form */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm">Proposal Metadata &amp; Registration Details</CardTitle>
                  <CardDescription>Primary administrative parameters for NaCCER indexing.</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4 text-xs">
                  <div>
                    <label className="font-mono text-[10px] uppercase font-semibold text-slate-600 block mb-1">
                      Full Project Title *
                    </label>
                    <Input
                      value={title}
                      onChange={(e) => setTitle(e.target.value)}
                      placeholder="e.g. AI-Driven Real-Time Methane Leakage Detection System..."
                      required
                    />
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div>
                      <label className="font-mono text-[10px] uppercase font-semibold text-slate-600 block mb-1">
                        Host Institution *
                      </label>
                      <Select value={institutionId} onChange={(e) => setInstitutionId(e.target.value)} required>
                        <option value="">Select Institution</option>
                        {(institutions.length > 0 ? institutions : MOCK_INSTITUTIONS).map((inst) => (
                          <option key={inst.id} value={inst.id}>
                            {inst.name} ({inst.code})
                          </option>
                        ))}
                      </Select>
                    </div>
                    <div>
                      <label className="font-mono text-[10px] uppercase font-semibold text-slate-600 block mb-1">
                        Research Domain *
                      </label>
                      <Select value={domain} onChange={(e) => setDomain(e.target.value)} required>
                        <option value="">Select Domain</option>
                        {RESEARCH_DOMAINS.map((d) => (
                          <option key={d} value={d}>
                            {d}
                          </option>
                        ))}
                      </Select>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div>
                      <label className="font-mono text-[10px] uppercase font-semibold text-slate-600 block mb-1">
                        Principal Investigator (PI) *
                      </label>
                      <Input
                        value={piName}
                        onChange={(e) => setPiName(e.target.value)}
                        placeholder="Dr. R. K. Verma"
                        required
                      />
                    </div>
                    <div>
                      <label className="font-mono text-[10px] uppercase font-semibold text-slate-600 block mb-1">
                        Proposed Budget (INR) *
                      </label>
                      <Input
                        type="number"
                        value={budget}
                        onChange={(e) => setBudget(e.target.value)}
                        placeholder="4500000"
                        required
                      />
                    </div>
                  </div>

                  <div className="pt-2 flex justify-end space-x-3">
                    <Link href="/proposals">
                      <Button type="button" variant="outline" size="sm" disabled={isSubmitting}>
                        Cancel
                      </Button>
                    </Link>
                    <Button type="submit" size="sm" disabled={isSubmitting}>
                      {isSubmitting ? (
                        <>
                          <Loader2 className="h-3.5 w-3.5 mr-1.5 animate-spin" />
                          Uploading &amp; Extracting PDF...
                        </>
                      ) : (
                        "Upload &amp; Process Proposal"
                      )}
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </form>
          )}
        </main>
      </div>
    </div>
  );
}
