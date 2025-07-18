# Raposa Brand Style Guide

## 🎨 Brand Overview

**Raposa** is a professional cybersecurity and domain analysis platform with a focus on modern, sophisticated design that conveys trust, technical expertise, and reliability.

### Brand Personality
- **Professional & Trustworthy**: Clean, sophisticated design
- **Technical & Modern**: Cutting-edge feel with subtle tech elements
- **Accessible & Clear**: User-friendly while maintaining technical credibility
- **Secure & Reliable**: Conveys safety and dependability

---

## 🌈 Color Palette

### Primary Colors
```css
/* Primary Blue */
--primary-50: #eff6ff
--primary-100: #dbeafe
--primary-400: #60a5fa
--primary-500: #3b82f6  /* Main Brand Blue */
--primary-600: #2563eb
--primary-700: #1d4ed8
--primary-800: #1e40af
--primary-900: #1e3a8a
```

### Secondary Colors
```css
/* Success Green */
--success-50: #f0fdf4
--success-100: #dcfce7
--success-400: #4ade80
--success-500: #22c55e  /* Main Success */
--success-600: #16a34a
--success-700: #15803d
--success-800: #166534
--success-900: #14532d

/* Warning Yellow */
--warning-50: #fffbeb
--warning-100: #fef3c7
--warning-400: #fbbf24
--warning-500: #f59e0b  /* Main Warning */
--warning-600: #d97706
--warning-700: #b45309

/* Danger Red */
--danger-50: #fef2f2
--danger-100: #fee2e2
--danger-400: #f87171
--danger-500: #ef4444   /* Main Danger */
--danger-600: #dc2626
--danger-700: #b91c1c
--danger-800: #991b1b
--danger-900: #7f1d1d
```

### Neutral Colors (Dark Theme)
```css
/* Background & Surface */
--background-primary: #000000     /* Pure black backgrounds */
--background-secondary: #0f172a   /* Dark slate backgrounds */
--background-card: #1e293b        /* Card backgrounds */
--background-elevated: #374151    /* Elevated elements */

/* Gray Scale */
--gray-50: #f9fafb
--gray-100: #f3f4f6
--gray-200: #e5e7eb
--gray-300: #d1d5db   /* Light text on dark */
--gray-400: #9ca3af   /* Secondary text */
--gray-500: #6b7280
--gray-600: #4b5563
--gray-700: #374151   /* Border colors */
--gray-800: #1f2937   /* Card backgrounds */
--gray-900: #111827   /* Main dark background */

/* Text Colors */
--text-primary: #ffffff        /* Primary white text */
--text-secondary: #d1d5db      /* Gray-300 secondary text */
--text-muted: #9ca3af         /* Gray-400 muted text */
--text-disabled: #6b7280      /* Gray-500 disabled text */
```

### Gradient Colors
```css
/* Primary Gradient */
background: linear-gradient(to right, #3b82f6, #8b5cf6, #06b6d4)

/* Hero Gradient */
background: linear-gradient(to right, #60a5fa, #a855f7, #22d3ee)

/* Accent Gradients */
--gradient-blue-purple: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%)
--gradient-blue-cyan: linear-gradient(135deg, #3b82f6 0%, #06b6d4 100%)
--gradient-purple-pink: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%)
```

---

## 🔤 Typography

### Font Stack
```css
/* Primary Font Family */
font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont,
             "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans",
             sans-serif, "Apple Color Emoji", "Segoe UI Emoji",
             "Segoe UI Symbol", "Noto Color Emoji"
```

### Font Sizes & Weights
```css
/* Headings */
.text-6xl { font-size: 3.75rem; line-height: 1; }      /* Hero titles */
.text-5xl { font-size: 3rem; line-height: 1; }        /* Page titles */
.text-4xl { font-size: 2.25rem; line-height: 2.5rem; } /* Section titles */
.text-3xl { font-size: 1.875rem; line-height: 2.25rem; } /* Card titles */
.text-2xl { font-size: 1.5rem; line-height: 2rem; }    /* Component titles */
.text-xl { font-size: 1.25rem; line-height: 1.75rem; } /* Large text */
.text-lg { font-size: 1.125rem; line-height: 1.75rem; } /* Body large */
.text-base { font-size: 1rem; line-height: 1.5rem; }   /* Body text */
.text-sm { font-size: 0.875rem; line-height: 1.25rem; } /* Small text */
.text-xs { font-size: 0.75rem; line-height: 1rem; }    /* Tiny text */

/* Font Weights */
.font-bold { font-weight: 700; }    /* Headings, important text */
.font-semibold { font-weight: 600; } /* Subheadings, labels */
.font-medium { font-weight: 500; }   /* Buttons, navigation */
.font-normal { font-weight: 400; }   /* Body text */
```

### Typography Hierarchy
```css
/* Hero Title */
.hero-title {
  font-size: 3.75rem;        /* text-6xl */
  font-weight: 700;          /* font-bold */
  line-height: 1.1;
  letter-spacing: -0.025em;  /* tracking-tight */
}

/* Page Title */
.page-title {
  font-size: 3rem;           /* text-5xl */
  font-weight: 700;          /* font-bold */
  line-height: 1.2;
}

/* Section Title */
.section-title {
  font-size: 1.875rem;       /* text-3xl */
  font-weight: 700;          /* font-bold */
  line-height: 1.3;
}

/* Card Title */
.card-title {
  font-size: 1.5rem;         /* text-2xl */
  font-weight: 600;          /* font-semibold */
  line-height: 1.4;
}

/* Body Text */
.body-text {
  font-size: 1rem;           /* text-base */
  font-weight: 400;          /* font-normal */
  line-height: 1.6;
}
```

---

## 🎯 Logo & Brand Assets

### Logo Usage
- **Primary Logo**: `/raposa_logo.svg` (40x40px standard size)
- **Logo Placement**: Always pair with "Raposa" text and "DOMAIN CHECKER" subtitle
- **Minimum Size**: 32px width minimum for digital use
- **Clear Space**: Minimum 1x logo width of clear space around logo

### Brand Name Hierarchy
```html
<!-- Standard Brand Layout -->
<div class="flex items-center space-x-3">
  <img src="/raposa_logo.svg" alt="Raposa Logo" class="h-10 w-auto" />
  <div>
    <h1 class="text-xl font-bold text-white">Raposa</h1>
    <p class="text-xs text-gray-400 uppercase tracking-wider">domain checker</p>
  </div>
</div>
```

---

## 🧩 Component Styles

### Buttons
```css
/* Primary Button */
.btn-primary {
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  color: white;
  padding: 0.75rem 2rem;
  border-radius: 0.75rem;    /* rounded-xl */
  font-weight: 600;         /* font-semibold */
  font-size: 1.125rem;      /* text-lg */
  transition: all 0.2s ease;
  border: none;
  cursor: pointer;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(59, 130, 246, 0.3);
}

/* Secondary Button */
.btn-secondary {
  background: rgba(59, 130, 246, 0.1);
  color: #60a5fa;
  border: 1px solid rgba(59, 130, 246, 0.3);
  padding: 0.75rem 2rem;
  border-radius: 0.75rem;
  font-weight: 600;
  transition: all 0.2s ease;
}

/* Ghost Button */
.btn-ghost {
  background: transparent;
  color: #d1d5db;
  border: 1px solid #374151;
  padding: 0.5rem 1.5rem;
  border-radius: 0.5rem;
  font-weight: 500;
}
```

### Cards
```css
/* Primary Card */
.card-primary {
  background: #1e293b;         /* bg-gray-800 */
  border: 1px solid #374151;   /* border-gray-700 */
  border-radius: 0.75rem;      /* rounded-xl */
  padding: 2rem;               /* p-8 */
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}

/* Elevated Card */
.card-elevated {
  background: #1e293b;
  border: 1px solid #4b5563;   /* border-gray-600 */
  border-radius: 0.75rem;
  padding: 2rem;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1),
              0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

/* Status Cards */
.card-success {
  background: rgba(34, 197, 94, 0.1);   /* bg-green-500/10 */
  border: 1px solid rgba(34, 197, 94, 0.3);
  border-radius: 0.5rem;
}

.card-warning {
  background: rgba(245, 158, 11, 0.1);  /* bg-yellow-500/10 */
  border: 1px solid rgba(245, 158, 11, 0.3);
  border-radius: 0.5rem;
}

.card-danger {
  background: rgba(239, 68, 68, 0.1);   /* bg-red-500/10 */
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 0.5rem;
}
```

### Form Elements
```css
/* Input Fields */
.input-primary {
  background: #374151;         /* bg-gray-700 */
  border: 1px solid #4b5563;   /* border-gray-600 */
  border-radius: 0.75rem;      /* rounded-xl */
  padding: 1rem 1.5rem;        /* px-6 py-4 */
  color: white;
  font-size: 1.125rem;         /* text-lg */
  transition: all 0.2s ease;
}

.input-primary:focus {
  outline: none;
  border-color: #3b82f6;       /* border-blue-500 */
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.input-primary::placeholder {
  color: #9ca3af;              /* text-gray-400 */
}
```

### Status Indicators
```css
/* Status Colors */
.status-valid {
  color: #4ade80;              /* text-green-400 */
}

.status-warning {
  color: #fbbf24;              /* text-yellow-400 */
}

.status-invalid {
  color: #f87171;              /* text-red-400 */
}

.status-missing {
  color: #9ca3af;              /* text-gray-400 */
}

/* Grade Colors */
.grade-a { color: #22c55e; }    /* Green */
.grade-b { color: #3b82f6; }    /* Blue */
.grade-c { color: #f59e0b; }    /* Yellow */
.grade-d { color: #ef4444; }    /* Red */
.grade-f { color: #dc2626; }    /* Dark Red */
```

---

## ✨ Animations & Effects

### Custom Animations
```css
/* Gradient Animation */
@keyframes gradient-x {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}

.animate-gradient-x {
  background-size: 200% 200%;
  animation: gradient-x 6s ease infinite;
}

/* Blob Animation */
@keyframes blob {
  0% { transform: translate(0px, 0px) scale(1); }
  33% { transform: translate(30px, -50px) scale(1.1); }
  66% { transform: translate(-20px, 20px) scale(0.9); }
  100% { transform: translate(0px, 0px) scale(1); }
}

.animate-blob {
  animation: blob 7s infinite;
}

/* Pulse Variants */
.animate-pulse-slow {
  animation: pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

.animate-bounce-slow {
  animation: bounce 2s infinite;
}
```

### Hover Effects
```css
/* Button Hover */
.hover-lift:hover {
  transform: translateY(-2px);
  transition: transform 0.2s ease;
}

/* Card Hover */
.hover-card:hover {
  border-color: #4b5563;       /* border-gray-600 */
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
}

/* Glow Effect */
.glow-blue {
  box-shadow: 0 0 20px rgba(59, 130, 246, 0.3);
}

.glow-green {
  box-shadow: 0 0 20px rgba(34, 197, 94, 0.3);
}
```

---

## 🎨 Background Patterns

### Grid Pattern
```css
/* Animated Grid Background */
.bg-grid {
  background-image:
    linear-gradient(to right, #1f2937 1px, transparent 1px),
    linear-gradient(to bottom, #1f2937 1px, transparent 1px);
  background-size: 4rem 4rem;
  mask-image: radial-gradient(ellipse 60% 50% at 50% 0%, #000 70%, transparent 110%);
}
```

### Gradient Orbs
```css
/* Background Orbs */
.orb-blue {
  width: 18rem;
  height: 18rem;
  background: #2563eb;
  border-radius: 50%;
  mix-blend-mode: multiply;
  filter: blur(40px);
  opacity: 0.2;
  animation: blob 7s infinite;
}

.orb-purple {
  width: 18rem;
  height: 18rem;
  background: #7c3aed;
  border-radius: 50%;
  mix-blend-mode: multiply;
  filter: blur(40px);
  opacity: 0.2;
  animation: blob 7s infinite;
  animation-delay: 2s;
}
```

---

## 📱 Responsive Design

### Breakpoints
```css
/* Mobile First Approach */
/* xs: 0px */
/* sm: 640px */
/* md: 768px */
/* lg: 1024px */
/* xl: 1280px */
/* 2xl: 1536px */

/* Typography Scaling */
@media (max-width: 768px) {
  .hero-title { font-size: 2.5rem; }    /* text-4xl */
  .page-title { font-size: 2rem; }      /* text-3xl */
  .section-title { font-size: 1.5rem; } /* text-2xl */
}

/* Container Sizes */
.container-sm { max-width: 640px; }
.container-md { max-width: 768px; }
.container-lg { max-width: 1024px; }
.container-xl { max-width: 1280px; }
.container-2xl { max-width: 1536px; }
```

---

## 🔧 Usage Guidelines

### Do's
✅ Use the primary blue (#3b82f6) for call-to-action elements
✅ Maintain consistent 12px spacing grid (space-3, space-6, space-12)
✅ Use gradient text for hero titles and important highlights
✅ Apply subtle animations to enhance user experience
✅ Use proper contrast ratios for accessibility
✅ Maintain dark theme consistency throughout

### Don'ts
❌ Don't use bright colors on light backgrounds
❌ Don't mix border radius styles (stick to rounded-xl for cards)
❌ Don't use more than 3 colors in a single component
❌ Don't animate essential UI elements excessively
❌ Don't break the typography hierarchy
❌ Don't use colors outside the defined palette

---

## 🎯 Brand Voice & Messaging

### Tone
- **Professional**: Clear, authoritative, trustworthy
- **Technical**: Knowledgeable without being intimidating
- **Helpful**: Solution-focused, educational
- **Confident**: Assertive about security expertise

### Key Messages
- "Professional Email Security Analysis"
- "Comprehensive DNS Record Analysis"
- "Enterprise-Grade Security Insights"
- "Protect Your Domain's Reputation"

### Call-to-Action Language
- "Analyze Your Domain"
- "Check Security Now"
- "Get Detailed Report"
- "Secure Your Email"

---

## 🛠 Implementation

### Tailwind Classes Reference
```html
<!-- Primary Brand Colors -->
<div class="bg-blue-500 text-white">         <!-- Primary Blue -->
<div class="bg-green-500 text-white">        <!-- Success Green -->
<div class="bg-yellow-500 text-black">       <!-- Warning Yellow -->
<div class="bg-red-500 text-white">          <!-- Danger Red -->

<!-- Background Classes -->
<div class="bg-black">                       <!-- Pure black -->
<div class="bg-gray-900">                    <!-- Dark background -->
<div class="bg-gray-800">                    <!-- Card background -->
<div class="bg-gray-700">                    <!-- Input background -->

<!-- Text Classes -->
<div class="text-white">                     <!-- Primary text -->
<div class="text-gray-300">                  <!-- Secondary text -->
<div class="text-gray-400">                  <!-- Muted text -->

<!-- Gradient Text -->
<span class="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-purple-400 to-cyan-400">

<!-- Rounded Corners -->
<div class="rounded-xl">                     <!-- Cards, buttons -->
<div class="rounded-lg">                     <!-- Smaller elements -->
<div class="rounded-full">                   <!-- Pills, avatars -->
```

This style guide provides everything needed to maintain consistent Raposa branding across all projects, including the upcoming coming soon page for raposa.tech!
