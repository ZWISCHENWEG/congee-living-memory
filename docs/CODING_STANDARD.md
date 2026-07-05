# Congee Frontend Coding Standards

## 1. Tech Stack (FROZEN)
- React 19, Vite, TypeScript
- TailwindCSS v4
- Shadcn UI
- React Router v7
- TanStack Query v5
- Axios, Zustand, Zod, React Hook Form
- Framer Motion, next-themes
- Lucide, Iconify, clsx, tailwind-merge, dayjs

*No adding libraries midway unless absolutely necessary.*

## 2. Core Rules
- **Strict TypeScript**: No `any`.
- **Styling**: No inline CSS, no inline styles.
- **DRY**: No duplicated logic.
- **Component Size**: Every component < 250 lines.
- **Hook Size**: Every hook < 150 lines.
- **Single Responsibility**: Every file has one responsibility.
- **Architecture**: Prefer composition over inheritance. Prefer reusable hooks and UI.
- **API**: Every API call must be typed. Every API validated with Zod.
- **Feature Isolation**: Every feature is isolated in `features/<name>`.
- **Quality**: ESLint must pass. No warnings.

## 3. Component Architecture
- `components/ui/`: ONLY for reusable primitives (Shadcn).
- Everything else belongs inside its feature (e.g., `features/chat/components`). This keeps the project clean.

## 4. UI Philosophy
- **Never design like a dashboard template.**
- **Follow:** Apple, Linear, Notion, Raycast, Arc Browser, Cursor, ChatGPT.
- **Principles:**
  - Lots of whitespace.
  - Large typography.
  - Minimal borders.
  - Soft shadows.
  - Subtle gradients.
  - Glass only when necessary.
  - Smooth motion.
  - Zero visual clutter.

## 5. Most Important Rule
- **Never generate placeholder-quality UI.**
- Every component should be production-ready.
- Every screen should feel like it could ship tomorrow.
- Do not leave TODOs. Do not use dummy layouts.
- Build every component as if this is the final production version.

## 6. Design Tokens
Everything must reference design tokens (Spacing, Radius, Elevation, Animation, Duration, Blur, Typography, Breakpoints, Container, Z-index, Opacity). Never hardcode utility values everywhere.

## 7. Performance
- **Optimize while building. Never optimize later.**
- Lazy load routes and heavy components.
- Dynamic imports.
- Memoize expensive lists.
- Virtualize long lists.
- Image optimization & SVG icons.
- Tree shaking & Code splitting.

## 8. Error Handling & State Transitions
- Every feature must contain: `ErrorBoundary`, `Loading`, `Empty`, `Skeleton`.
- Never directly render data without handling intermediate states.
- Follow State Transition flow: Request -> Loading -> Success -> Empty -> Error -> Unauthorized -> Retry.

## 9. Accessibility (Mandatory)
- Keyboard navigation, ARIA labels, Focus rings, Tab order, Screen reader labels, Reduced motion, Contrast.
