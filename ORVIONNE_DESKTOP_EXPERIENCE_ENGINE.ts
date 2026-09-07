import type { AgentTask, ApprovalRequest } from "./localAgentOs";
import type { LocalCoreHealth } from "./localCore";
import type { LocalDocumentRecord } from "./localDocumentRuntime";
import type { AssistantSuggestion } from "./localIntelligenceEngine";
import type { TrustReport } from "./localTrustEngine";
import type { LocalWorkspace } from "./localWorkspace";

export type ExperienceEventType =
  | "APP_STARTED"
  | "WORKSPACE_LOCKED"
  | "WORKSPACE_UNLOCKED"
  | "FIRST_RUN_STARTED"
  | "FIRST_RUN_COMPLETED"
  | "LOCAL_MODEL_AVAILABLE"
  | "LOCAL_MODEL_UNAVAILABLE"
  | "NETWORK_OFFLINE"
  | "NETWORK_RESTORED"
  | "DOCUMENT_IMPORTED"
  | "INDEXING_STARTED"
  | "INDEXING_COMPLETED"
  | "CLOUD_CONSENT_REQUIRED"
  | "PERMISSION_REQUIRED"
  | "APPROVAL_PENDING"
  | "AGENT_TASK_STARTED"
  | "AGENT_TASK_BLOCKED"
  | "AGENT_TASK_COMPLETED"
  | "LOCKDOWN_ACTIVATED"
  | "AUDIT_INTEGRITY_FAILED";

export type ExperienceEvent = {
  type: ExperienceEventType;
  at: string;
  message: string;
  severity: "info" | "success" | "warning" | "critical";
  source: "runtime" | "trust" | "agent" | "onboarding" | "network" | "user";
  panel?: ExperiencePanelId;
};

export type ExperiencePanelId = "import" | "knowledge" | "trust" | "memory" | "agent" | "models" | "diagnostics";

export type ExperienceProgressStep = {
  id: string;
  label: string;
  status: "waiting" | "running" | "completed" | "blocked";
};

export type ExperienceSuggestion = {
  id: string;
  label: string;
  description: string;
  panel: ExperiencePanelId;
  priority: "low" | "medium" | "high";
};

export type ExperienceSnapshot = {
  greeting: string;
  subGreeting: string;
  trustSummary: string;
  activePanel: ExperiencePanelId;
  suggestions: ExperienceSuggestion[];
  progress: ExperienceProgressStep[];
  events: ExperienceEvent[];
};

export type ExperienceContext = {
  workspace: LocalWorkspace;
  documents: LocalDocumentRecord[];
  intelligenceSuggestions: AssistantSuggestion[];
  health: LocalCoreHealth;
  trustReport: TrustReport | null;
  agentTask: AgentTask | null;
  approvals: ApprovalRequest[];
  online: boolean;
  busy: boolean;
  status: string;
  now?: Date;
};

export function createExperienceSnapshot(context: ExperienceContext): ExperienceSnapshot {
  const events = deriveEvents(context);
  return {
    greeting: createContextGreeting(context),
    subGreeting: createSubGreeting(context),
    trustSummary: createTrustSummary(context),
    activePanel: choosePanel(context),
    suggestions: createAdaptiveSuggestions(context),
    progress: createProgressSteps(context),
    events,
  };
}

export function createContextGreeting(context: ExperienceContext): string {
  if (!context.online) return "Offline mode is active.";
  if (context.approvals.length > 0) return "An approval is waiting.";
  if (context.busy) return "I am working locally.";
  if (context.documents.length === 0) return `Welcome, ${context.workspace.displayName}.`;
  return "Your private workspace is ready.";
}

export function createSubGreeting(context: ExperienceContext): string {
  if (!context.online) return "Local search, local memory, and local workflows remain available.";
  if (context.approvals.length > 0) return "Review it before ORVIONNE executes the next step.";
  if (context.documents.length === 0) return "Add a document or folder to begin building local knowledge.";
  return `${context.documents.length.toLocaleString()} local source${context.documents.length === 1 ? "" : "s"} indexed. No data has left this device.`;
}

export function createTrustSummary(context: ExperienceContext): string {
  const passports = context.trustReport?.objectCount ?? 0;
  const encrypted = context.workspace.encryptionStatus === "keychain_wrapped";
  if (!context.online) return "Offline · local intelligence active";
  if (context.health.checks.some((check) => check.status === "error")) return "Runtime attention required";
  if (encrypted) return `Stored locally · ${passports} trust passport${passports === 1 ? "" : "s"}`;
  return "Local storage active · encryption needs review";
}

export function createAdaptiveSuggestions(context: ExperienceContext): ExperienceSuggestion[] {
  const suggestions: ExperienceSuggestion[] = [];
  if (context.documents.length === 0) {
    suggestions.push({
      id: "import-first-document",
      label: "Import a document",
      description: "Start a local knowledge base without uploading anything.",
      panel: "import",
      priority: "high",
    });
  }
  if (!context.online) {
    suggestions.push({
      id: "offline-status",
      label: "Review offline status",
      description: "See which capabilities remain available without network access.",
      panel: "diagnostics",
      priority: "medium",
    });
  }
  if (context.approvals.length > 0) {
    suggestions.push({
      id: "review-approval",
      label: "Review pending approval",
      description: "A planned action needs your permission before it can continue.",
      panel: "agent",
      priority: "high",
    });
  }
  if (context.trustReport && context.trustReport.objectCount > 0) {
    suggestions.push({
      id: "inspect-trust",
      label: "Inspect trust activity",
      description: "Review passports, processing location, and local storage claims.",
      panel: "trust",
      priority: "low",
    });
  }
  for (const suggestion of context.intelligenceSuggestions.slice(0, 2)) {
    suggestions.push({
      id: `memory-${suggestion.id}`,
      label: suggestion.title,
      description: suggestion.reason,
      panel: "memory",
      priority: suggestion.priority,
    });
  }
  return suggestions.slice(0, 6);
}

export function createProgressSteps(context: ExperienceContext): ExperienceProgressStep[] {
  if (!context.busy) return [];
  if (context.status.toLowerCase().includes("indexing")) {
    return [
      { id: "read", label: "Reading selected files", status: "completed" },
      { id: "extract", label: "Extracting local text", status: "running" },
      { id: "index", label: "Preparing local index", status: "waiting" },
    ];
  }
  if (context.status.toLowerCase().includes("import")) {
    return [
      { id: "permission", label: "Using selected file permission", status: "completed" },
      { id: "extract", label: "Extracting text locally", status: "running" },
      { id: "trust", label: "Creating trust passport", status: "waiting" },
    ];
  }
  if (context.agentTask) {
    return [
      { id: "plan", label: "Reviewing task plan", status: "completed" },
      { id: "approval", label: context.approvals.length > 0 ? "Waiting for approval" : "Executing approved steps", status: context.approvals.length > 0 ? "blocked" : "running" },
    ];
  }
  return [{ id: "local", label: "Running local intelligence", status: "running" }];
}

export function experienceEvent(type: ExperienceEventType, message: string, source: ExperienceEvent["source"], panel?: ExperiencePanelId): ExperienceEvent {
  return {
    type,
    at: new Date().toISOString(),
    message,
    severity: type === "AUDIT_INTEGRITY_FAILED" || type === "LOCKDOWN_ACTIVATED" ? "critical" : type.includes("COMPLETED") ? "success" : "info",
    source,
    panel,
  };
}

function choosePanel(context: ExperienceContext): ExperiencePanelId {
  if (context.approvals.length > 0 || context.agentTask) return "agent";
  if (context.documents.length === 0) return "import";
  if (!context.online) return "diagnostics";
  return "knowledge";
}

function deriveEvents(context: ExperienceContext): ExperienceEvent[] {
  const events: ExperienceEvent[] = [];
  if (!context.online) events.push(experienceEvent("NETWORK_OFFLINE", "Offline mode is active. Local features remain available.", "network", "diagnostics"));
  if (context.documents.length > 0) events.push(experienceEvent("INDEXING_COMPLETED", `${context.documents.length} local source${context.documents.length === 1 ? "" : "s"} available.`, "runtime", "knowledge"));
  if (context.approvals.length > 0) events.push(experienceEvent("APPROVAL_PENDING", `${context.approvals.length} approval${context.approvals.length === 1 ? "" : "s"} waiting.`, "agent", "agent"));
  if (context.health.checks.some((check) => check.status === "error")) events.push(experienceEvent("AUDIT_INTEGRITY_FAILED", "A runtime health check requires attention.", "trust", "diagnostics"));
  return events;
}
