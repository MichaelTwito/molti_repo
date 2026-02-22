# Music Agents — High-level design (Python/Django)

## Architecture (shared core)
- **Django + DRF** API-first
- **Postgres** multi-tenant (org_id on all tables)
- **Celery + Redis** background jobs (enrichment, sequences, parsing)
- **S3-compatible storage** for uploads/attachments (contracts, statements)
- Search: start with Postgres FTS/trigram → OpenSearch later

## Common entities
- Organization (tenant)
- User (role)
- Artist
- Track/Release
- FileAsset
- ActivityEvent (append-only audit)

## Wedge A: outreach-specific entities
- Campaign
- Curator
- Playlist
- Prospect (campaign↔curator/playlist)
- OutboundMessage / MessageThread
- SequenceStep
- Outcome

## Wedge A workflows
- curator discovery + scoring
- draft generation
- throttled send
- follow-up scheduler
- reply detection (Gmail)

## Wedge B: rights/royalties entities
- Work vs Recording
- Party, Identifier
- Split, Contract
- ValidationIssue
- Task/checklist

## Scalability
- composite indexes by (org_id, status, created_at)
- partition append-only tables later
- idempotency keys for sends/ingestion
- strong audit logs; encryption-at-rest for sensitive docs
