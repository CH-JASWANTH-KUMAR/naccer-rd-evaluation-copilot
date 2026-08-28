import { NextResponse } from "next/server";
import { appConfig } from "@/lib/config";

export async function GET() {
  return NextResponse.json(
    {
      status: "ok",
      application: appConfig.name,
      version: appConfig.version,
      timestamp: new Date().toISOString(),
      environment: appConfig.environment,
      features: appConfig.features,
    },
    { status: 200 }
  );
}
