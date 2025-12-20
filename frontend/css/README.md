# MarketML Frontend Design System

## Overview
Complete responsive design system for MarketML persona builder with mobile-first approach and consistent styling across all screen sizes.

## CSS Architecture

### File Structure
```
frontend/css/
├── base.css        - Core design system with CSS variables
├── mobile.css      - Mobile-specific styles (< 768px)
├── desktop.css     - Desktop/tablet styles (>= 768px)
└── components.css  - Reusable UI components
```

### Import Order
**CRITICAL**: CSS files must be imported in this exact order in HTML:
```html
<link rel="stylesheet" href="css/base.css">
<link rel="stylesheet" href="css/mobile.css">
<link rel="stylesheet" href="css/desktop.css">
<link rel="stylesheet" href="css/components.css">
```

## Design Tokens (CSS Variables)

### Colors
```css
--primary-color: #667eea       /* Main brand color */
--primary-dark: #5568d3        /* Hover states */
--secondary-color: #10b981     /* Success/completion */
--danger-color: #ef4444        /* Errors */
--warning-color: #f59e0b       /* Warnings */
--bg-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%)
```

### Typography
```css
--font-base: 16px              /* Base font size */
--font-size-xs: 0.75rem        /* 12px */
--font-size-sm: 0.875rem       /* 14px */
--font-size-md: 1rem           /* 16px */
--font-size-lg: 1.125rem       /* 18px */
--font-size-xl: 1.25rem        /* 20px */
--font-size-2xl: 1.5rem        /* 24px */
--font-size-3xl: 1.875rem      /* 30px */
--font-size-4xl: 2.25rem       /* 36px */
--font-size-5xl: 3rem          /* 48px */
```

### Spacing System (8px base unit)
```css
--space-xs: 0.25rem            /* 4px */
--space-sm: 0.5rem             /* 8px */
--space-md: 1rem               /* 16px */
--space-lg: 1.5rem             /* 24px */
--space-xl: 2rem               /* 32px */
--space-2xl: 2.5rem            /* 40px */
--space-3xl: 3rem              /* 48px */
```

### Container Widths (Fixed Frame Sizes)
```css
--container-mobile: 100%       /* Full width on mobile */
--container-tablet: 768px      /* Tablet max width */
--container-desktop: 1024px    /* Desktop max width */
--container-wide: 1200px       /* Maximum content width */
```

## Responsive Breakpoints

### Mobile First Strategy
All base styles target mobile devices by default, then progressively enhanced for larger screens.

### Breakpoint System

#### Small Mobile (< 375px)
- 13px base font size
- Single column layout
- Reduced padding (12px)
- Smaller buttons and form controls
```css
@media (max-width: 374px) { ... }
```

#### Mobile (< 768px) - DEFAULT
- 14px base font size
- Single column grids
- Touch-optimized controls (48px min height)
- Stacked layout
- 16px input font size (prevents iOS zoom)
```css
/* No media query - mobile first */
```

#### Mobile Landscape (< 768px height)
- Special handling for horizontal orientation
- 2-column progress steps
- Optimized spacing
```css
@media (max-width: 767px) and (orientation: landscape) { ... }
```

#### Tablet (768px - 1023px)
- 16px base font size
- 2-column score grid
- 4-column progress steps
- Max container: 768px
```css
@media (min-width: 768px) { ... }
```

#### Desktop (1024px - 1279px)
- 16px base font size
- 3-column score grid
- 8-column progress steps
- Max container: 1024px
- Hover effects enabled
```css
@media (min-width: 1024px) { ... }
```

#### Large Desktop (1280px - 1535px)
- 16px base font size
- 4-column grid option
- Max container: **1200px (FIXED)**
- Enhanced spacing
```css
@media (min-width: 1280px) { ... }
```

#### Ultra-Wide (1536px+)
- 18px base font size
- Larger typography (64px h1)
- Max container: **1200px (FIXED)**
- Extra padding for readability
```css
@media (min-width: 1536px) { ... }
```

## Core Components

### Layout Components

#### Container
Fixed-width centered container that adapts to screen size.
```html
<div class="container">
  <!-- Content -->
</div>
```

**Behavior:**
- Mobile: 100% width with 16px padding
- Tablet: Max 768px
- Desktop: Max 1024px
- Wide: **Max 1200px (FIXED)**

#### Header
Centered header with gradient background.
```html
<div class="header">
  <h1>MarketML</h1>
  <p>AI-Powered Marketing Persona Builder</p>
</div>
```

#### Card
White card container with shadow and rounded corners.
```html
<div class="card">
  <!-- Content -->
</div>
```

**Responsive:**
- Mobile: 16px padding, smaller border radius
- Desktop: 32px padding, larger border radius

### Form Components

#### Form Group
Labeled form input container.
```html
<div class="form-group">
  <label for="name" class="form-label">Name *</label>
  <input type="text" id="name" class="form-control" required>
</div>
```

#### Button
Primary action button with gradient background.
```html
<button class="btn btn-primary">Generate Persona</button>
```

**States:**
- `:hover` - Lift effect (desktop only)
- `:disabled` - Reduced opacity, no pointer
- `:focus` - Visible outline for accessibility

**Sizes:**
- Mobile: 44px min height (touch-friendly)
- Desktop: 48px min height

### Progress Components

#### Progress Container
Container for progress tracking during persona generation.
```html
<div class="progress-container active">
  <h3>Generating Persona...</h3>
  <div class="progress-bar-container">
    <div class="progress-bar" style="width: 50%;">50%</div>
  </div>
  <div class="progress-steps">
    <!-- Steps -->
  </div>
</div>
```

**Control with JS:**
```javascript
progressContainer.classList.add('active');    // Show
progressContainer.classList.remove('active'); // Hide
```

#### Progress Steps
Grid of progress step indicators.
```html
<div class="progress-step active">
  <span class="step-icon">🔍</span>
  <span class="step-label">Scraping</span>
</div>
```

**States:**
- `.active` - Currently executing (blue border, pulse animation)
- `.completed` - Finished (green background)

**Responsive Grid:**
- Mobile: 2 columns
- Mobile Landscape: 4 columns
- Tablet: 4 columns
- Desktop: 8 columns

### Score Components

#### Scores Grid
Grid of score cards showing metrics.
```html
<div class="scores-grid">
  <div class="score-card">
    <div class="score-label">Business Maturity</div>
    <div class="score-value">85</div>
    <div class="score-description">out of 100</div>
  </div>
  <!-- More cards -->
</div>
```

**Responsive Grid:**
- Mobile: 1 column (stacked)
- Tablet: 2 columns
- Desktop: 3 columns
- Wide: 4 columns (optional)

### Badge Components

#### Confidence Badge
Translucent badge showing confidence score.
```html
<span class="confidence-badge">Confidence: 92%</span>
```

#### Tier Badge
Prominent badge showing business tier.
```html
<span class="tier-badge">Growth Stage</span>
```

### List Components

#### Insights List
List of insights with icons.
```html
<ul class="insights-list">
  <li>High social media presence indicates digital maturity</li>
  <li>Location in tech hub suggests innovation focus</li>
</ul>
```

#### Actions List
List of recommended actions with checkmarks.
```html
<ul class="actions-list">
  <li>Implement SEO optimization for local search</li>
  <li>Develop content marketing strategy</li>
</ul>
```

### Alert Components

#### Error Message
Error alert with red styling.
```html
<div class="error-message active">
  Error: Failed to generate persona
</div>
```

**Control with JS:**
```javascript
errorMessage.classList.add('active');    // Show
errorMessage.classList.remove('active'); // Hide
```

## JavaScript Integration

### Toggle Visibility
```javascript
// Show/hide with active class
element.classList.add('active');
element.classList.remove('active');

// Or direct style manipulation for cards
element.style.display = 'block';
element.style.display = 'none';
```

### Smooth Scrolling
```javascript
element.scrollIntoView({ behavior: 'smooth' });
window.scrollTo({ top: 0, behavior: 'smooth' });
```

## Accessibility Features

### Touch Optimization
- Minimum 44px touch targets on mobile
- 48px button height on desktop
- No hover effects on touch devices

### Keyboard Navigation
- Visible focus indicators
- Proper tab order
- Semantic HTML structure

### Screen Readers
- Proper heading hierarchy (h1 → h2 → h3)
- ARIA labels where needed
- Alt text for icons

### Motion Reduction
```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

## Dark Mode Support

Dark mode styles are included for system preference:
```css
@media (prefers-color-scheme: dark) {
  :root {
    --bg-primary: #1a1a1a;
    --bg-secondary: #2d2d2d;
    --text-primary: #f5f5f5;
    /* More dark mode variables */
  }
}
```

## Print Styles

Optimized for printing:
```css
@media print {
  /* Remove buttons and interactive elements */
  .btn { display: none; }
  
  /* Ensure content fits on page */
  .container { max-width: 100%; }
  
  /* Remove backgrounds to save ink */
  body { background: white; }
}
```

## Best Practices

### Fixed Frame Size
- Maximum container width is **1200px** on all large screens
- This ensures consistency: "Size of frame must be fixed on all screens" ✓

### Button Position Consistency
- Buttons use consistent spacing: `var(--space-md)` margins
- Full width on mobile, centered on desktop
- Same position relative to content across breakpoints ✓

### Content Adaptation
- Grid columns reduce from 4 → 3 → 2 → 1 as screen shrinks
- Typography scales: 18px → 16px → 14px → 13px
- Spacing reduces proportionally ✓

### Performance
- CSS variables for efficient updates
- Hardware-accelerated animations (transform, opacity)
- Minimal repaints/reflows

### Maintainability
- Centralized design tokens
- Consistent naming conventions
- Modular component structure
- Comments explaining complex sections

## Testing Responsive Design

### Browser DevTools
1. Open Chrome/Firefox DevTools (F12)
2. Click device toolbar icon (Ctrl+Shift+M)
3. Test these viewports:
   - iPhone SE (375px width)
   - iPhone 12/13 (390px width)
   - Pixel 5 (393px width)
   - iPad (768px width)
   - iPad Pro (1024px width)
   - Desktop (1280px width)
   - Large Desktop (1536px width)

### Verification Checklist
- [ ] Frame stays fixed at 1200px max width
- [ ] Buttons in same position relative to content
- [ ] Score cards stack properly on mobile
- [ ] Progress steps adapt grid columns
- [ ] Touch targets meet 44px minimum
- [ ] Text remains readable at all sizes
- [ ] No horizontal scrolling
- [ ] Smooth animations (not jerky)
- [ ] Dark mode switches correctly
- [ ] Print layout looks clean

## Adding New Pages

To create a new page with consistent styling:

1. **Include CSS files** in same order:
```html
<link rel="stylesheet" href="css/base.css">
<link rel="stylesheet" href="css/mobile.css">
<link rel="stylesheet" href="css/desktop.css">
<link rel="stylesheet" href="css/components.css">
```

2. **Use standard layout structure**:
```html
<div class="container">
  <div class="header">
    <h1>Page Title</h1>
    <p>Description</p>
  </div>
  
  <div class="card">
    <!-- Content -->
  </div>
</div>
```

3. **Apply consistent spacing**:
```css
margin: var(--space-lg);
padding: var(--space-xl);
gap: var(--space-md);
```

4. **Use existing components**:
- `.btn .btn-primary` for buttons
- `.form-group` for forms
- `.score-card` for metrics
- `.section` for content sections

## Common Issues & Solutions

### Issue: CSS not loading
**Solution:** Check import order and relative paths. Files must be in `css/` directory.

### Issue: Layout breaks on mobile
**Solution:** Verify viewport meta tag: `<meta name="viewport" content="width=device-width, initial-scale=1.0">`

### Issue: Buttons too small on mobile
**Solution:** Use `.btn` class which includes 44px min height for touch targets.

### Issue: Content overflows container
**Solution:** Container has max-width 1200px. Use `.container` class properly.

### Issue: Hover effects on mobile
**Solution:** Desktop CSS only applies hover at 1024px+. Mobile gets touch-optimized styles.

### Issue: Font size too small
**Solution:** Check breakpoint - mobile uses 14px, desktop 16px. Adjust if needed.

## Version History

### v1.0.0 (Current)
- Complete responsive design system
- Mobile-first approach
- 7 breakpoints (small mobile to ultra-wide)
- 80+ CSS variables
- Touch optimization
- Dark mode support
- Print styles
- Accessibility features

## Support

For issues or questions about the design system:
1. Check this README
2. Review CSS comments in source files
3. Test in multiple viewports using DevTools
4. Verify CSS import order

---

**Last Updated:** 2024
**Maintainer:** MarketML Team
**License:** MIT
