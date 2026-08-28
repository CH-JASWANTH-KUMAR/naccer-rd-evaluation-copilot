import React from "react";
import { Sliders, Server } from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { appConfig } from "@/lib/config";

export default function SettingsPage() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-slate-200 pb-5">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">Platform Configuration</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            NaCCER R&amp;D Copilot evaluation thresholds, API parameters, and system settings.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Left: General Settings */}
        <div className="md:col-span-2 space-y-6">
          {/* API Backend Connection Settings */}
          <Card>
            <CardHeader>
              <CardTitle className="text-sm flex items-center space-x-2">
                <Server className="h-4 w-4 text-slate-700" />
                <span>Backend REST API Boundary</span>
              </CardTitle>
              <CardDescription>Configure connection parameters for future Python/FastAPI service layer.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4 text-xs">
              <div>
                <label className="font-mono text-[10px] uppercase font-semibold text-slate-600 block mb-1">
                  FastAPI Base Endpoint URL
                </label>
                <Input defaultValue={appConfig.apiBaseUrl} className="font-mono text-xs" />
              </div>
              <div className="flex items-center justify-between p-3 bg-slate-50 rounded border border-slate-200">
                <div>
                  <span className="font-semibold text-slate-800">Connection State:</span>
                  <p className="text-[11px] text-slate-500">Base frontend layout active. REST service layer initialized.</p>
                </div>
                <Badge variant="outline" className="bg-slate-100 font-mono text-[10px]">
                  STUBBED
                </Badge>
              </div>
              <Button size="sm">Save Configuration</Button>
            </CardContent>
          </Card>

          {/* Rubric Weights & Thresholds */}
          <Card>
            <CardHeader>
              <CardTitle className="text-sm flex items-center space-x-2">
                <Sliders className="h-4 w-4 text-slate-700" />
                <span>Evaluation Rubric &amp; Risk Thresholds</span>
              </CardTitle>
              <CardDescription>Configure default evaluation category weightings and risk flags.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3 text-xs">
              <div className="grid grid-cols-2 gap-3 font-mono">
                <div>
                  <label className="text-[10px] text-slate-500 uppercase block">Novelty Weight (%)</label>
                  <Input defaultValue={25} type="number" />
                </div>
                <div>
                  <label className="text-[10px] text-slate-500 uppercase block">Methodology Weight (%)</label>
                  <Input defaultValue={25} type="number" />
                </div>
                <div>
                  <label className="text-[10px] text-slate-500 uppercase block">Financial Weight (%)</label>
                  <Input defaultValue={25} type="number" />
                </div>
                <div>
                  <label className="text-[10px] text-slate-500 uppercase block">Feasibility Weight (%)</label>
                  <Input defaultValue={25} type="number" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Right: Engine Status Disclosure */}
        <div className="md:col-span-1 space-y-4">
          <Card className="bg-slate-900 text-white border-slate-800">
            <CardHeader>
              <CardTitle className="text-sm font-bold">Base Setup Phase Info</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-xs text-slate-300">
              <p className="leading-relaxed">
                This platform is running in <span className="text-emerald-400 font-semibold">Base Foundation Mode</span>.
              </p>
              <div className="space-y-2 border-t border-slate-800 pt-2 text-[11px] font-mono">
                <div className="flex justify-between">
                  <span>Next.js App Router:</span>
                  <span className="text-white">v16.3.3</span>
                </div>
                <div className="flex justify-between">
                  <span>React Architecture:</span>
                  <span className="text-white">v19.2</span>
                </div>
                <div className="flex justify-between">
                  <span>Package Manager:</span>
                  <span className="text-white">pnpm</span>
                </div>
                <div className="flex justify-between">
                  <span>AI Engine State:</span>
                  <span className="text-amber-400">Disconnected</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
