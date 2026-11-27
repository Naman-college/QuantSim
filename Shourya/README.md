# Shourya — ShadCN UI Workstation (React + TypeScript + Tailwind CSS + Radix UI)

**Team Member:** Shourya  
**Assigned Module:** Modern ShadCN UI Design System, Dashboard Components, Command Search Palette & Responsive Layout

---

## 📁 Folder Contents

| File / Folder | Purpose |
| :--- | :--- |
| `package.json`, `vite.config.ts`, `tsconfig.json`, `tailwind.config.js` | Frontend toolchain (React 18, TypeScript, Vite, Tailwind CSS, Radix UI, Lucide Icons, `cmdk`, `sonner`). |
| `src/index.css` | Authentic ShadCN CSS variables (`--background`, `--card`, `--primary`, `--border`, etc.) for both **Dark (Zinc-950)** and **Light** modes. |
| `src/lib/utils.ts` | `cn()` utility (`clsx` + `tailwind-merge`) used by all ShadCN components. |
| `src/components/ui/` | Reusable **ShadCN UI primitives**: `button.tsx`, `card.tsx`, `badge.tsx`, `tabs.tsx`, `select.tsx`, `input.tsx`, `label.tsx`, `switch.tsx`, `slider.tsx`, `dialog.tsx`, `command.tsx`, `tooltip.tsx`, `table.tsx`, `accordion.tsx`, `separator.tsx`, `skeleton.tsx`, `scroll-area.tsx`. |
| `src/components/dashboard/TopNavbar.tsx` | Sticky glass header with QuantSim logo, `Ctrl+K` Search button, 1-click quick ticker pills, Dark/Light theme switcher, and Run CTA. |
| `src/components/dashboard/StockCommandPalette.tsx` | `Ctrl+K` ShadCN Command Dialog querying `/api/search`, grouped cleanly into **US & Global** and **Indian Markets (NSE/BSE)**. |
| `src/components/dashboard/SidebarPanel.tsx` | Active asset card, Radix `Select` strategy picker, `Slider` controls, collapsible `Accordion` for advanced risk/fee settings, and Capital/Date controls. |
| `src/components/dashboard/KpiGrid.tsx` | 4 ShadCN KPI Cards with Radix `Tooltip` formula explanations on hover and animated `Skeleton` loading states. |
| `src/components/dashboard/TradeLogPanel.tsx` | Trade Activity Log with `ALL` / `BUY` / `SELL` filter pills and color-coded ShadCN Badges inside a `ScrollArea`. |
| `src/components/dashboard/ComparisonDashboard.tsx` | Tab 2 combining 4 summary cards, Prakshat's `ComparisonChart`, a ranked Leaderboard `Table`, and a Key Quant Takeaway card. |
| `src/App.tsx` | Main state coordinator calling Naman's FastAPI `/api/*` endpoints with `sonner` toast notifications. |
| `dist/` | Pre-built static bundle served offline by `Naman/api.py` inside the native PySide6 desktop window. |

---

## 🎨 How ShadCN UI Was Built & Customized

1. **Design Tokens (`src/index.css`)**: Uses HSL semantic CSS variables (`--background`, `--card`, `--popover`, `--primary`, `--border`) so toggling `.dark` on `<html>` smoothly switches the entire app—including Prakshat's TradingView charts—between Obsidian Dark and Crisp Light mode.
2. **Accessible Radix Primitives (`src/components/ui/`)**: Every dropdown (`Select`), modal (`CommandDialog`), toggle (`Switch`), slider (`Slider`), tooltip (`Tooltip`), and collapsible section (`Accordion`) uses headless `@radix-ui` primitives for keyboard accessibility and clean animations.
3. **Offline Production Bundle (`dist/`)**: Running `npm run build` compiles TypeScript (`tsc --noEmit`) and bundles all CSS/JS into `Shourya/dist/` so Python serves the entire UI locally without needing Node.js running.

---

## 🔗 Integration With Other Team Members
- **Embeds from Prakshat:** Imports `SingleStrategyChart` and `ComparisonChart` from `@prakshat/*` (`../Prakshat/charts/*`) via Vite & TypeScript path aliases.
- **Communicates with Naman:** Calls `/api/search`, `/api/backtest`, and `/api/compare` served by `Naman/api.py`, and is hosted natively inside `Naman/app.py` (`QWebEngineView`).
- **Configures Rounak's Strategies:** Exposes all hyperparameters for Rounak's 5 strategies inside `SidebarPanel.tsx`.

---

## 🎓 Teacher Viva / Oral Exam Prep (Likely Questions & Answers)

1. **Q: What is ShadCN UI and why is it different from Bootstrap or Material UI?**  
   **A:** ShadCN UI isn't a monolithic black-box library—each component (`Button`, `Card`, `Select`, `Command`, `Tabs`) is owned directly inside `Shourya/src/components/ui/`, built on accessible **Radix UI** primitives and styled via **Tailwind CSS** + **CVA (`class-variance-authority`)** + `cn()`.
2. **Q: How does the `Ctrl+K` Stock Search Command Palette work?**  
   **A:** A global `keydown` listener in `App.tsx` toggles `StockCommandPalette` (`cmdk` + Radix `Dialog`). Typing debounces for 160ms and calls Naman's `GET /api/search?q=...`, grouping US (`$ USD`) and Indian (`₹ INR`) matches.
3. **Q: Does the user need Node.js running to launch `python main.py`?**  
   **A:** No. Vite compiles `Shourya/src/` and `Prakshat/charts/` into static files inside `Shourya/dist/`. FastAPI serves `dist/` directly on `127.0.0.1` inside PySide6's Chromium `QWebEngineView`.
4. **Q: Why do you use `Skeleton` placeholders in `KpiGrid.tsx`?**  
   **A:** Skeleton loaders preserve card layout geometry while `/api/backtest` computes in the background, preventing layout shift and providing immediate visual feedback.
