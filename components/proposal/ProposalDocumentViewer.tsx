"use client";

import React, { useEffect, useState } from "react";
import { FileText, Layers, FileCode, AlertCircle, Loader2 } from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Select } from "@/components/ui/select";
import { documentService, ApiDocumentDetail, ApiDocumentPage, ApiProposalSection } from "@/lib/api/documents";

interface ProposalDocumentViewerProps {
  proposalId: string;
}

export function ProposalDocumentViewer({ proposalId }: ProposalDocumentViewerProps) {
  const [loading, setLoading] = useState(true);
  const [document, setDocument] = useState<ApiDocumentDetail | null>(null);
  const [pages, setPages] = useState<ApiDocumentPage[]>([]);
  const [sections, setSections] = useState<ApiProposalSection[]>([]);
  const [selectedPageNum, setSelectedPageNum] = useState<number>(1);

  useEffect(() => {
    async function loadDocumentData() {
      setLoading(true);
      try {
        const docs = await documentService.getProposalDocuments(proposalId);
        if (docs.length > 0) {
          const mainDoc = docs[0];
          setDocument(mainDoc);

          const [docPages, docSections] = await Promise.all([
            documentService.getDocumentPages(mainDoc.id),
            documentService.getDocumentSections(mainDoc.id),
          ]);
          setPages(docPages);
          setSections(docSections);
          if (docPages.length > 0) {
            setSelectedPageNum(docPages[0].page_number);
          }
        }
      } catch {
        // Fallback
      } finally {
        setLoading(false);
      }
    }
    loadDocumentData();
  }, [proposalId]);

  if (loading) {
    return (
      <Card>
        <CardContent className="p-8 flex items-center justify-center space-x-2 text-slate-500 text-xs">
          <Loader2 className="h-4 w-4 animate-spin text-blue-600" />
          <span>Loading extracted document provenance &amp; section data...</span>
        </CardContent>
      </Card>
    );
  }

  if (!document) {
    return (
      <Card>
        <CardContent className="p-8 text-center space-y-3">
          <FileText className="h-10 w-10 text-slate-300 mx-auto" />
          <h3 className="text-sm font-bold text-slate-800">No Processed PDF Document Found</h3>
          <p className="text-xs text-slate-500 max-w-sm mx-auto">
            Upload a technical proposal PDF to initiate page-by-page text extraction and section detection.
          </p>
        </CardContent>
      </Card>
    );
  }

  const selectedPage = pages.find((p) => p.page_number === selectedPageNum);

  return (
    <div className="space-y-6">
      {/* Document Summary Card */}
      <Card className="bg-white border-slate-200">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <FileText className="h-4 w-4 text-blue-600" />
              <CardTitle className="text-sm">{document.filename}</CardTitle>
            </div>
            <Badge variant={document.processing_status === "PROCESSED" ? "success" : "warning"}>
              {document.processing_status}
            </Badge>
          </div>
          <CardDescription className="text-xs">
            Storage Path: <code className="font-mono text-[11px] bg-slate-100 px-1 py-0.5 rounded text-slate-700">{document.storage_path}</code>
          </CardDescription>
        </CardHeader>
        <CardContent className="pt-0 text-xs">
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 bg-slate-50 p-3 rounded-md border border-slate-200">
            <div>
              <span className="text-[10px] text-slate-400 uppercase font-mono block">Extracted Pages</span>
              <span className="font-semibold text-slate-900">{document.pages_count} Pages</span>
            </div>
            <div>
              <span className="text-[10px] text-slate-400 uppercase font-mono block">Sections Detected</span>
              <span className="font-semibold text-slate-900">{document.sections_count} Sections</span>
            </div>
            <div>
              <span className="text-[10px] text-slate-400 uppercase font-mono block">File Size</span>
              <span className="font-semibold text-slate-900">
                {(document.file_size / (1024 * 1024)).toFixed(2)} MB
              </span>
            </div>
            <div>
              <span className="text-[10px] text-slate-400 uppercase font-mono block">Ingestion Date</span>
              <span className="font-semibold text-slate-900">
                {new Date(document.created_at).toLocaleDateString()}
              </span>
            </div>
          </div>

          {document.processing_error && (
            <div className="mt-3 p-3 bg-amber-50 border border-amber-200 rounded text-amber-800 text-xs flex items-center space-x-2">
              <AlertCircle className="h-4 w-4 text-amber-600 flex-shrink-0" />
              <span>{document.processing_error}</span>
            </div>
          )}
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Page-Aware Text Viewer (2 cols) */}
        <Card className="lg:col-span-2">
          <CardHeader className="pb-3 border-b border-slate-200">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm flex items-center space-x-2">
                <FileCode className="h-4 w-4 text-slate-500" />
                <span>Extracted Page Provenance</span>
              </CardTitle>
              <div className="flex items-center space-x-2">
                <label className="text-xs text-slate-500 font-mono">Page:</label>
                <Select
                  value={selectedPageNum.toString()}
                  onChange={(e) => setSelectedPageNum(parseInt(e.target.value))}
                  className="w-24 h-8 text-xs"
                >
                  {pages.map((p) => (
                    <option key={p.id} value={p.page_number}>
                      Page {p.page_number}
                    </option>
                  ))}
                </Select>
              </div>
            </div>
          </CardHeader>
          <CardContent className="p-4">
            {selectedPage ? (
              <div className="space-y-2">
                <div className="flex items-center justify-between text-[11px] font-mono text-slate-500 border-b border-slate-100 pb-1">
                  <span>DOCUMENT ID: {selectedPage.document_id}</span>
                  <span>PAGE {selectedPage.page_number} OF {pages.length}</span>
                </div>
                <pre className="p-4 bg-slate-900 text-slate-100 font-mono text-xs rounded-md whitespace-pre-wrap overflow-x-auto min-h-[300px] leading-relaxed">
                  {selectedPage.text || "(No text extracted on this page)"}
                </pre>
              </div>
            ) : (
              <p className="text-xs text-slate-500 p-4 text-center">No page text available.</p>
            )}
          </CardContent>
        </Card>

        {/* Detected Proposal Sections Panel (1 col) */}
        <Card>
          <CardHeader className="pb-3 border-b border-slate-200">
            <CardTitle className="text-sm flex items-center space-x-2">
              <Layers className="h-4 w-4 text-slate-500" />
              <span>Detected Proposal Sections</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="p-4 space-y-3">
            {sections.length > 0 ? (
              sections.map((sec) => (
                <div key={sec.id} className="p-3 bg-slate-50 rounded-md border border-slate-200 text-xs space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-slate-900">{sec.section_title}</span>
                    <Badge variant="secondary" className="text-[10px] font-mono">
                      Pp. {sec.start_page}-{sec.end_page}
                    </Badge>
                  </div>
                  <div className="flex items-center space-x-2 text-[10px] font-mono text-slate-500">
                    <Badge variant="outline" className="text-[10px]">
                      {sec.section_type}
                    </Badge>
                    <span>Confidence: {(sec.confidence * 100).toFixed(0)}%</span>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-xs text-slate-500 text-center py-4">No sections detected in this document.</p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
