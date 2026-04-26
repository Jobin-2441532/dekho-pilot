# Design System: The Editorial Reflection

This design system is a bespoke framework crafted for high-end financial storytelling. It moves away from the clinical, data-heavy density of traditional fintech and toward an "Editorial Reflection" aesthetic. The goal is to make the user feel like they are reading a premium, personalized journal of their financial life.

---

## 1. Creative North Star: "The Digital Curator"
The system is built on the philosophy of **The Digital Curator**. Unlike standard dashboards that merely *display* data, this system *curates* meaning. 

To achieve this, we reject the rigid, "boxed-in" grid. We use intentional asymmetry, overlapping elements, and generous white space to create a sense of calm and luxury. Information is presented in "chapters," utilizing large-scale typography and layered surfaces to guide the user through a reflective narrative journey.

---

## 2. Color & Texture Strategy
Our palette is rooted in organic, earthy tones that evoke stability and warmth.

### The "No-Line" Rule
**Prohibit 1px solid borders for sectioning.** To maintain a premium feel, boundaries must be defined solely through background color shifts. For example, a `surface-container-low` section sitting on a `surface` background creates a soft, sophisticated edge that a line cannot replicate.

### Surface Hierarchy & Nesting
Treat the UI as a series of physical layers—like stacked sheets of fine heavy-stock paper.
- **Base:** `surface` (#fef8f2) acts as the desk.
- **Sections:** `surface-container` (#f3ede7) defines large content areas.
- **Focus Cards:** `surface-container-lowest` (#ffffff) creates a crisp, high-contrast lift for key insights.

### Signature Textures & Gradients
Flat colors are for utilities; storytelling requires soul.
- **The Narrative Gradient:** Use a linear gradient from `primary` (#6f4627) to `primary-container` (#8b5e3c) for hero elements and main CTAs. 
- **Glassmorphism:** For floating navigation or modal overlays, use `surface` at 80% opacity with a `24px` backdrop-blur. This allows the "warm beige" warmth to bleed through, maintaining a cohesive atmosphere.

---

## 3. Typography: The Editorial Voice
We pair the geometric confidence of **Manrope** with the functional clarity of **Public Sans**.

| Role | Token | Font | Size | Character |
| :--- | :--- | :--- | :--- | :--- |
| **Display** | `display-lg` | Manrope | 3.5rem | Bold, tight tracking. For "Monthly Wrap" titles. |
| **Headline**| `headline-lg`| Manrope | 2rem | Expressive. Used for key financial takeaways. |
| **Title**   | `title-lg`   | Public Sans | 1.375rem | Semibold. For card headings. |
| **Body**    | `body-lg`    | Public Sans | 1rem | High readability for narrative descriptions. |
| **Label**   | `label-md`   | Public Sans | 0.75rem | All-caps, slightly tracked out for metadata. |

**Editorial Rule:** Use `display-lg` typography as a design element itself. Don't be afraid to let a large "80%" or "Total" overlap the edge of a card to create depth.

---

## 4. Elevation & Depth
Depth is achieved through **Tonal Layering**, not structural lines.

- **The Layering Principle:** Place a `surface-container-lowest` card on a `surface-container-low` section. This creates a natural "lift" based on color value rather than artificial shadows.
- **Ambient Shadows:** When a card must "float" (e.g., a celebratory Monthly Wrap summary), use an extra-diffused shadow:
  - `Y: 20px, Blur: 40px, Color: on-surface @ 6% opacity`.
- **The Ghost Border:** If accessibility requires a stroke, use `outline-variant` at 15% opacity. Never use 100% opaque borders.

---

## 5. Components

### Cards (The "Story Chapter")
- **Style:** Use `xl` (3rem) or `lg` (2rem) corner radius.
- **Separation:** Forbid dividers. Use `32px` to `48px` of vertical white space to separate content blocks.
- **Interaction:** On hover/tap, cards should subtly scale (1.02x) rather than darken.

### Narrative Buttons
- **Primary:** Gradient fill (`primary` to `primary-container`), `full` roundedness, with `on-primary` text.
- **Secondary:** `surface-container-highest` background, no border, `on-surface` text.

### Progress Patterns (The "Growth Path")
Instead of standard bar charts, use "Curved Paths." Utilize the **Secondary** (#4e644d) color for positive growth trends, rendered as a soft, thick-stroke spline (4px) with a subtle outer glow.

### Interactive Chips
- **Style:** `surface-container-high` background. When selected, transition to `primary` with `on-primary` text. Use `sm` (0.5rem) radius for a "tab" feel.

---

## 6. Do’s and Don’ts

### Do:
- **Do** use asymmetrical layouts. A chart on the left balanced by large-scale text on the right feels more premium than a centered stack.
- **Do** use "Warmth" as a metric. If a screen feels too "white," increase the use of `surface-container-low` (#f9f3ed).
- **Do** treat "Positive Growth" (`secondary`) with a soft touch. It should feel like a flourishing plant, not a neon "buy" signal.

### Don't:
- **Don't** use 1px dividers. If you need to separate elements, use a `12px` gap or a tonal shift.
- **Don't** use pure black (#000000) for text. Always use `on-surface` (#1d1b18) to maintain the "warm" ink-on-paper feel.
- **Don't** cram data. If a screen feels busy, break it into two screens. The "Monthly Wrap" is a gallery, not a spreadsheet.
- **Don't** use standard Material Design drop shadows. They are too "software-like." Use the wide, tinted Ambient Shadows defined in Section 4.