# Invoice MVP TaskSpec — Notes (Validation & Defaults)

## Chosen schema version
- JSON Schema **2020-12** (`$schema: https://json-schema.org/draft/2020-12/schema`)

## Minimal required fields
Top-level `required`:
- `invoiceNumber` (string, non-empty)
- `issueDate` (string, `format: date`, `YYYY-MM-DD`)
- `dueDate` (string, `format: date`, `YYYY-MM-DD`)
- `currency` (string, `^[A-Z]{3}$`, intended ISO-4217)
- `seller` (party object, requires `name`)
- `buyer` (party object, requires `name`)
- `lineItems` (array, `minItems: 1`)

## Parties
- `seller` and `buyer` use the same `party` definition.
- `party.name` is required.
- Optional `party.address.country` is validated as ISO-3166-1 alpha-2 (`^[A-Z]{2}$`).

## Line items
- Each `lineItem` requires: `description`, `quantity`, `unitPrice`.
- `quantity` must be `> 0` (`exclusiveMinimum: 0`).
- `unitPrice` is a non-negative number (`money`).
- `taxable` default: `true`.

## Taxes
- `taxes` is optional; default is `[]`.
- Each tax object requires `name` and enforces **exactly one of**:
  - `rate` (0..1), OR
  - `amount` (>= 0)
- `appliesTo` default: `taxableLineItems`.

## Metadata
- `metadata` is optional; default is `{}`.
- Values restricted to primitive JSON types (`string|number|boolean|null`) to keep ingestion simple.

## Defaults (informational)
Defaults are included for:
- `taxes`: `[]`
- `notes`: `""`
- `paymentInstructions`: `""`
- `metadata`: `{}`
- `lineItem.quantity`: `1`
- `lineItem.unit`: `""`
- `lineItem.taxable`: `true`
- `tax.appliesTo`: `"taxableLineItems"`

> Reminder: JSON Schema defaults are annotations; they are **not** applied automatically unless your validator/processor applies them.

## Intentionally not enforced (MVP)
- `dueDate` after `issueDate` (cross-field date comparison)
- Computed totals/subtotals consistency (requires arithmetic)
- Currency-specific decimal precision (e.g., 2 decimals)
- Uniqueness constraints (invoiceNumber uniqueness, SKU uniqueness)
