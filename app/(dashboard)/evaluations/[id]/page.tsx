import { notFound } from "next/navigation";
import { evaluationService } from "@/lib/api/evaluations";
import { EvaluationDetailWorkspace } from "@/components/evaluation/EvaluationDetailWorkspace";

interface EvaluationDetailPageProps {
  params: Promise<{ id: string }>;
}

export default async function EvaluationDetailPage({ params }: EvaluationDetailPageProps) {
  const { id } = await params;
  const evaluation = await evaluationService.getEvaluationById(id);

  if (!evaluation) {
    notFound();
  }

  return <EvaluationDetailWorkspace initialEvaluation={evaluation} />;
}
