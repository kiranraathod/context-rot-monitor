
# Prompt templates for Phase 3/4 remediation and diagnosis tools

DIAGNOSE_ROT_PROMPT = """
Analyze the following context usage metrics and identify the root cause of context rot.
Focus on:
1. Is the rot improved by removing specific sections?
2. Is the rot caused by topic drift (relevance)?
3. Is the rot caused by repetitive information (redundancy)?

Metrics:
{metrics_json}

Provide a concise diagnosis and 3 actionable steps to improve context health.
"""

OPTIMIZE_CONTEXT_PROMPT = """
Rewrite the following context to be more concise while preserving all key information.
Target reduction: 30%.

Context:
{context_text}
"""
