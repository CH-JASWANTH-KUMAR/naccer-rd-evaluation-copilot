# NaCCER R&D Evaluation Copilot - Development Guidelines

## 💻 Environment Requirements
- **Node.js**: 20.9.0 or higher (Tested with Node v24.18.0)
- **Package Manager**: `pnpm` 11.x (Do not use `npm` or `yarn` to prevent duplicate lockfiles)

---

## 🛠️ Essential Development Workflow

### Installing Dependencies
```bash
pnpm install
```

### Running Local Development Server
```bash
pnpm dev
```
Access the application at `http://localhost:3000`.

### Type Checking
```bash
npx tsc --noEmit
```
Strict mode is enabled in `tsconfig.json`. Do not introduce `any` types.

### Linting
```bash
pnpm lint
```
Ensures ESLint rules and Next.js best practices are respected.

### Production Build Verification
```bash
pnpm build
```

---

## 🎨 UI & Design Guidelines
- Use curated enterprise slate/zinc color tokens (`bg-slate-50`, `text-slate-900`, `border-slate-200`).
- Keep tables information-dense, high-contrast, and clean.
- Ensure all interactive buttons, inputs, and links have explicit hover/focus states.
- Do not use arbitrary gradients or glassmorphism effects. Maintain professional government/enterprise aesthetic.
