# Ravi's Machine Safety – Electrical & Control Circuit App

A single-page web app that reads electrical drawings: IEC and NEMA/JIC control circuits, safety circuits, PLC I/O and single-line diagrams. It is built for machine safety consultants and styled in Tesseract colours (graphite with safety amber, Sora headings). It has a light/dark switch.

## Two versions

- `schematic-reader/index.html`: the claude.ai artifact. It can't send images to Claude on every account, so it is kept for Learn, Ask and quizzes only.
- `docs/index.html`: the standalone website (the main version). It reads drawings through an **OpenRouter** API key that you paste into Setup. Publish it with GitHub Pages: Settings → Pages → Source "Deploy from a branch" → branch `claude/schematic-reader-mobile-app-in59pe` → folder `/docs` → Save. The site appears at https://gitravi1987.github.io/claude-code-sandbox/.
  - The key and chosen model stay in the browser (localStorage). Saved reports and quiz scores stay in the browser (IndexedDB), per device.
  - The model list is loaded live from OpenRouter (vision models only). Compare two or three models on the same sheet: each saved report records which model read it.
  - Give the key a monthly spending limit in OpenRouter.

## Sharing a report (docs version)

- **Save as PDF** builds an A4 report (summary, observations and recommendations, safety functions, how it works, marked drawings, components, connections, to-verify list) and opens the browser print window. Choose "Save as PDF" as the destination. The report is built into a hidden `#printRoot` element that is only visible when printing, so no PDF library is needed and the text stays selectable. The page title is set to the report name, which Chrome suggests as the file name.
- **Share summary** opens the phone's share sheet (WhatsApp, email, etc.) with a short text: title, summary, observations by severity with recommendations, safety functions and the to-verify list. If the browser has no share sheet it copies the text instead.
- **Download Excel / HTML / JSON** are still available. The HTML file is a standalone version of the same report and prints cleanly too.

## Marked drawing (docs version)

After reading a sheet, the app sends the full image to the vision model once more and asks it to box every symbol with a short label such as `K1 Contactor NC`, `M1 Motor 3~` or `S1 E-stop NC`. The **Marked drawing** tab draws the boxes on your image.

- Labels or numbers view, zoom 1–4×, filter by type (power, control, safety, load, signal), download as JPEG.
- Boxes come back as 0–1000 coordinates and are stored as fractions, so they scale with the image. **Swap X/Y** fixes models that answer in y,x order.
- An optional marking model (Setup is not needed) can differ from the reading model, because pointing accuracy varies by model.
- The image (max 1600 px) and marks are saved with the report, so a marked drawing can be reopened later. Marks are also included in the Excel and HTML exports.
- Turn off "Mark components on the drawing after reading" in Settings to skip the extra call.

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
