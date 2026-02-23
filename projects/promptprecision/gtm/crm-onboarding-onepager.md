# PromptPrecision — Onboarding Intake → CRM JSON (One-pager)

## One-liner
Turn onboarding intake (forms, PDFs, emails) into **clean, validated CRM records** (HubSpot/Salesforce) with confidence + missing-fields questions.

## Who it’s for (ICP)
- RevOps agencies & HubSpot/Salesforce consultants
- B2B services firms with heavy onboarding
- SMB B2B SaaS inbound sales teams (SDRs)

## The wedge
- Validation + mapping + audit trail (evidence)
- Confidence scoring + “missing/ambiguous fields” + suggested follow-ups
- Reduces manual re-typing + improves CRM hygiene

## MVP scope
- Input: paste/file upload/webhook
- Output: canonical JSON + CRM-specific payload
- One CRM connector (start with HubSpot)
- Review UI for low confidence

## Success metrics
- Type validity + required-field completion rate
- Human edits per intake (target <3)
- Time-to-CRM record (minutes → seconds)
- Hallucination rate (unsupported values)

## Pricing hypothesis
Tiered by intakes/month + seats:
- Starter $99/mo (100 intakes)
- Pro $299/mo (500)
- Business $799/mo (2,000) + audit logs
