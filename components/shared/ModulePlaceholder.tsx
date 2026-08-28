import React from "react";
import { Cpu, AlertCircle } from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface ModulePlaceholderProps {
  moduleName: string;
  phase: string;
  description: string;
  plannedFeatures?: string[];
}

export function ModulePlaceholder({
  moduleName,
  phase,
  description,
  plannedFeatures,
}: ModulePlaceholderProps) {
  return (
    <Card className="border-dashed border-slate-300 bg-slate-50/50">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Cpu className="h-5 w-5 text-slate-600" />
            <CardTitle className="text-sm font-bold text-slate-800">{moduleName}</CardTitle>
          </div>
          <Badge variant="outline" className="bg-slate-100 text-slate-700 text-[10px] font-mono">
            {phase} Planned
          </Badge>
        </div>
        <CardDescription className="text-xs text-slate-600 font-normal">
          {description}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="rounded-md bg-amber-50/80 border border-amber-200 p-3 text-xs text-amber-900 flex items-start space-x-2">
          <AlertCircle className="h-4 w-4 text-amber-600 flex-shrink-0 mt-0.5" />
          <div>
            <span className="font-semibold">Development Phase Disclosure:</span>{" "}
            Analysis module will be connected in the next development phase ({phase}). AI engine outputs, vector embeddings, and real-time proposal evaluation algorithms are intentionally omitted in this base frontend setup.
          </div>
        </div>

        {plannedFeatures && plannedFeatures.length > 0 && (
          <div className="mt-4">
            <h4 className="text-xs font-semibold text-slate-700 uppercase tracking-wider mb-2">
              Planned Engine Scope:
            </h4>
            <ul className="space-y-1.5 text-xs text-slate-600">
              {plannedFeatures.map((feat, idx) => (
                <li key={idx} className="flex items-center space-x-2">
                  <span className="h-1.5 w-1.5 rounded-full bg-slate-400" />
                  <span>{feat}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
