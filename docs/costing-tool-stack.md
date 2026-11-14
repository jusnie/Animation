# Costing tool with AI + Google Sheets — what GitHub already gives us

Researched 2026-11-10 for the sellable product: a quotation/costing app that knows the
margin, with an AI assistant and a Google Sheets connection. Everything below is MIT
unless marked. Nothing here was built — this is the parts list.

## The licence trap to avoid up front

| Repo | ★ | Licence | Verdict |
|---|---|---|---|
| `midday-ai/midday` | 15,125 | **AGPL-3.0** | Best-looking invoicing/quoting app on GitHub. AGPL means if you host a modified version you must publish your source. **Do not build a paid SaaS on it.** |
| `VladSez/easy-invoice-pdf` | 1,124 | **AGPL-3.0** | Same problem. |
| `invoicerr-app/invoicerr` | 731 | **AGPL-3.0** | Same problem. |
| `al1abb/invoify` | **6,391** | **MIT** | ✅ The one to actually reuse. Next.js invoice/quotation builder with PDF export. |
| `tuanpham-dev/react-invoice-generator` | 682 | MIT | ✅ Drop-in React invoice form + PDF. Dormant since 2024 but small and clean. |
| `htmldocs-js/htmldocs` | 750 | MIT | ✅ Modern HTML→PDF for the quote itself; the non-LaTeX path. |
| `pdovhomilja/nextcrm-app` | 741 | MIT | Next.js CRM — useful if you ever want deals/contacts. |
| `imbhargav5/nextbase-nextjs-supabase-starter` | 833 | MIT | Next.js 16 + Supabase + auth + Stripe boilerplate. The scaffold, if you don't want to start empty. |

**Takeaway:** the three most impressive invoicing repos are all AGPL and would poison a
paid product. `invoify` (MIT, 6.4k★, actively pushed) is the base to study.

## Spreadsheet access — both halves, both MIT, both verified here

**Excel (.xlsx) — `haris-musa/excel-mcp-server` 4,301★ MIT.** This is the real find. It is
pip-installable and I ran it in this workspace:

```
pip install excel-mcp-server        # 2.3.0
excel-mcp-server stdio              # with EXCEL_FILES_PATH=/tmp
```

Handshake succeeded, **44 tools** registered, and `list_workbooks` read a workbook that
openpyxl had just written. The tool list is more than file I/O — note these three:

- `goal_seek` — brute-force the input that hits a target. This is *backwards costing*:
  "what do I charge to make 30%?"
- `trace_formula` — walk a formula's dependency chain. This is how you explain a quote.
- `create_pivot_table`, `add_conditional_format`, `add_data_validation`, `create_chart`,
  `find_cells`/`replace_cells`, `transform_range`, `import_csv`/`export_csv`,
  `insert_image`, `read_vba`.

So Excel support is not a "maybe later" — it works today, and `goal_seek` alone is a
feature most costing tools don't have.

**Google Sheets — `taylorwilsdon/google_workspace_mcp` 3,515★ MIT.** Gmail, Calendar,
Docs, Sheets, Slides, Chat under one OAuth. Far more than needed, but the Sheets part is
mature and the OAuth handling is exactly the part you'd otherwise get wrong. Lighter
options: `xing5/mcp-google-sheets` (1,019★ MIT), `freema/mcp-gsheets` (105★ MIT, pushed
Nov 2026), `isaacphi/mcp-gdrive` (283★ MIT).

Caveat that still applies: **the OAuth flow has to be tested on Vercel**, because
`googleapis.com` and `accounts.google.com` are unreachable from this sandbox.

## The AI layer

- `vercel/ai` (29.6k★) — the AI SDK. One `generateObject` call with a Zod schema turns
  "500 flyers, 3 days, rush" into `{qty, unit_cost, labour, lead_time}` typed and validated.
  This is the whole "AI assistant" feature; don't hand-roll it.
- Keep it to **one endpoint**. The AI's only jobs: parse messy input into line items,
  suggest rates from the library, and write the one-sentence "you're losing ₱3.20 per
  unit" warning. Anything more becomes a chatbot nobody asked for.

## Recommended assembly

```
al1abb/invoify  ── study the quote UI + PDF (MIT)
      +
nextbase or plain create-next-app  ── Next.js 16 + Supabase auth + Stripe
      +
vercel/ai generateObject  ── paste-text → line items → margin check
      +
haris-musa/excel-mcp-server  ── .xlsx import/export + goal_seek   (works now, here)
      +
google_workspace_mcp or drive.file OAuth  ── live Sheet sync      (test on Vercel)
      +
htmldocs / react-pdf  ── branded quotation PDF
```

Supabase stays the database. Sheets/Excel are import-export and the "my data in a
spreadsheet" escape hatch — do not use either as the primary store (Sheets quota is
~300 req/min per project, 60/min per user; a live calculator will hit that).

## What still needs building (nothing on GitHub does it)

The **trade-specific rate library** — printing, catering, construction, tailoring. That is
the moat, it is data not code, and no repo will hand it to you. Also the margin rules
(rush surcharge, waste factor, overhead allocation) and the Tagalog/Bisaya explanations of
a loss. That is the product; everything above is scaffolding.

## Order of work I'd suggest

1. Pick one trade. Write its cost formula on paper first.
2. `create-next-app` in `site/` style + Supabase schema: `materials`, `labour_rates`,
   `quotes`, `quote_lines`, `orgs`.
3. `generateObject` endpoint → line items.
4. Quote PDF from `invoify`'s approach.
5. `.xlsx` import/export with the Excel MCP server (works today).
6. Google Sheets OAuth with `drive.file` scope + Picker, deployed to Vercel.
7. Charge ₱1,500–3,000/month before adding trade #2.
