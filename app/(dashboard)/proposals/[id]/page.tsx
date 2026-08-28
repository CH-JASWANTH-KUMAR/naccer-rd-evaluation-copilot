import { notFound } from "next/navigation";
import { proposalService } from "@/lib/api/proposals";
import { ProposalDetailWorkspace } from "@/components/proposal/ProposalDetailWorkspace";

interface ProposalDetailPageProps {
  params: Promise<{ id: string }>;
}

export default async function ProposalDetailPage({ params }: ProposalDetailPageProps) {
  const { id } = await params;
  const proposal = await proposalService.getProposalById(id);

  if (!proposal) {
    notFound();
  }

  return <ProposalDetailWorkspace initialProposal={proposal} />;
}
