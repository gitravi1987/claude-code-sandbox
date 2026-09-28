# Ravi's Machine Safety – Electrical & Control Circuit App

A single-page web app that reads electrical drawings: IEC and NEMA/JIC control circuits, safety circuits, PLC I/O and single-line diagrams. It is built for machine safety consultants and styled in Tesseract colours (graphite with safety amber, Sora headings). It has a light/dark switch.

## Learn mode

- **Explain** on any component: Claude teaches that device, covering its symbol in IEC and NEMA, its terminal numbers, its role in this circuit and its failure modes.
- **Quiz**: 5 or 10 multiple-choice questions written from the current drawing, at Beginner, Intermediate or Advanced level. Scores are saved to `learn/progress`, and new quizzes focus on your weakest topics.
- **Symbol guide**: IEC vs NEMA/JIC sketches, plus tables of terminal numbers and letter codes.

Live app (private to the owner): https://claude.ai/artifact/8TxERiN6qyXeTycq4aUcoM

## How it works

- The page runs as a claude.ai artifact. It calls Claude through the artifact `sample` capability, so it uses the signed-in user's own Claude plan. No API key is needed.
- Each sheet is sent as a full view plus overlapping zoomed sections (2×2 or 3×3). This helps with small text, because images are downsized before Claude sees them.
- PDFs are rendered page by page in the browser with pdf.js.
- Claude returns structured JSON:
  - components, with tag, symbol, function, ratings and confidence
  - connections
  - circuit sequences
  - safety functions, with channels, EDM, cross-fault detection, reset, stop category and a suggested ISO 13849 category
  - findings
  - SLD data
  - items to verify
- For multi-sheet sets, a second pass joins cross-references and safety functions across sheets.
- Reports are saved in the artifact database (`reports` collection), so they appear on both phone and desktop.
- You can ask follow-up questions in the Ask tab, optionally with the drawing images attached.
- Reports export to Excel (SheetJS), a standalone HTML report, or JSON.

## Files

- `index.html`: the whole app (published as the artifact page).

## Limits

- The safety review is advisory. It reads the drawing only, so confirm PL/category with device data and a site inspection.
- Photos forwarded through WhatsApp lose detail. Use original photos or PDFs.
