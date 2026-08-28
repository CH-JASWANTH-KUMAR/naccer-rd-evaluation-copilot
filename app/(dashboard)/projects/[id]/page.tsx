import React from "react";
import { notFound } from "next/navigation";
import { projectService } from "@/lib/api/projects";
import { HistoricalProjectDetailViewer } from "@/components/project/HistoricalProjectDetailViewer";

interface ProjectDetailPageProps {
  params: Promise<{ id: string }>;
}

export default async function ProjectDetailPage({ params }: ProjectDetailPageProps) {
  const { id } = await params;
  const project = await projectService.getHistoricalProjectById(id);

  if (!project) {
    notFound();
  }

  return <HistoricalProjectDetailViewer initialProject={project} />;
}
