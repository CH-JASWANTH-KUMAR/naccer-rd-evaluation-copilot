export const appConfig = {
  name: "NaCCER R&D Evaluation Copilot",
  version: "1.0.0-base",
  apiBaseUrl: process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api/v1",
  environment: process.env.NODE_ENV || "development",
  features: {
    aiEngineConnected: false, // Explicit feature flag showing base phase status
    ragBenchmarkConnected: false,
    financialCheckConnected: false,
  },
};
