/**
 * Clarity Trial Architect — Guild AI Agent TypeScript SDK
 *
 * This is the Guild SDK agent definition that manages the agent's
 * lifecycle: build, deploy, version, govern, and monitor.
 *
 * Build with: npx guild build
 * Deploy with: guild deploy
 */

import { llmAgent } from "@guildai/agents-sdk";
import { pioneerTools } from "@guildai-services/clarity~pioneer";
import { deepmindTools } from "@guildai-services/clarity~deepmind";
import { actianTools } from "@guildai-services/clarity~actian";
import { bandTools } from "@guildai-services/clarity~band";

export default llmAgent({
  name: "clarity-trial-architect",
  description: "Self-evolving clinical trial design agent that simulates patient populations and learns from every design",

  tools: {
    ...pioneerTools,    // Routine inference (summarization, comparison)
    ...deepmindTools,   // Advanced reasoning (edge cases, regulatory)
    ...actianTools,     // Vector memory (store & search trial patterns)
    ...bandTools,       // Human escalation (collaboration rooms)
  },

  // Governance: what this agent can access
  credentials: {
    pioneer: ["inference:write"],
    deepmind: ["reasoning:read"],
    actian: ["vectors:read", "vectors:write"],
    band: ["rooms:create", "messages:send"],
  },

  version: {
    strategy: "semver",
    autoPublish: true,
    changelog: true,
  },

  monitoring: {
    metrics: [
      "designs_evaluated",
      "patterns_stored",
      "power_improvement",
      "human_escalations",
    ],
  },
});
