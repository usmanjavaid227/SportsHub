# Contact Page Design Documentation

## Overview
The contact page features a professional, collapsible design with sidebar navigation and three main sections. It provides multiple ways for users to get in touch with SportsHub.

## Design Structure

### Layout
- **Sidebar Navigation** (3 columns on large screens, stacked on mobile)
- **Main Content Area** (9 columns on large screens, full width on mobile)
- **Responsive Design** with Bootstrap grid system

### Color Scheme
- **Primary Orange**: `var(--sh-orange)` (#ff9900)
- **Background**: Dark theme with gradient overlays
- **Cards**: Semi-transparent with orange borders
- **Text**: White primary, secondary text for descriptions

## Sidebar Navigation

### Features
- **Sticky positioning** - stays in place while scrolling
- **Active state highlighting** - shows current section
- **Quick contact info** - email, phone, response time
- **Smooth animations** - hover effects and transitions

### Navigation Items
1. **Contact Us** (fa-paper-plane icon)
   - Opens contact form section
   - Active by default
   - Orange highlight when active

2. **FAQ** (fa-question-circle icon)
   - Opens frequently asked questions
   - Nested accordion structure
   - 6 comprehensive Q&A items

3. **Contact Details** (fa-map-marker-alt icon)
   - Opens contact information
   - Location details and social media
   - Map section with ground locations

### Quick Info Section
- **Email**: info@sportshub.fi
- **Phone**: +358 40 123 4567
- **Response Time**: 24h response
- **Icons**: Small orange icons with consistent spacing

## Main Content Sections

### 1. Contact Us Form
**Purpose**: Primary contact method with form validation

**Features**:
- **Form Fields**: Name, Email, Subject, Message
- **Validation**: Required fields with visual feedback
- **Styling**: Orange theme with focus states
- **Submit Button**: "Send Message" with paper plane icon

**Form Styling**:
```css
background: rgba(255, 255, 255, 0.05)
border: 1px solid rgba(255, 153, 0, 0.3)
color: var(--sh-white)
```

**Focus States**:
- Background: `rgba(255, 255, 255, 0.08)`
- Border: `var(--sh-orange)`
- Box Shadow: `0 0 0 0.2rem rgba(255, 153, 0, 0.25)`

### 2. Frequently Asked Questions
**Purpose**: Self-service support with common questions

**Structure**:
- **Nested Accordion**: Main section contains FAQ accordion
- **6 FAQ Items**: Comprehensive coverage of common questions
- **Icons**: Each question has relevant icon

**FAQ Topics**:
1. **Joining Challenges** (fa-question-circle)
2. **Creating Challenges** (fa-plus-circle)
3. **Leaderboard System** (fa-trophy)
4. **Ground Locations** (fa-location-dot)
5. **Account Registration** (fa-user-plus)
6. **Data Security** (fa-shield-halved)

**Styling**:
- Accordion items with semi-transparent backgrounds
- Orange icons for visual hierarchy
- Smooth collapse/expand animations

### 3. Contact Details & Find Us
**Purpose**: Alternative contact methods and location information

**Components**:

#### Contact Information Grid
- **Email**: info@sportshub.fi (fa-envelope)
- **Phone**: +358 40 123 4567 (fa-phone)
- **Location**: Tampere, Finland (fa-location-dot)
- **Response Time**: Within 24 hours (fa-clock)
- **Community Support**: Active 24/7 (fa-users)

#### Map Section
- **Visual Map**: Icon-based representation
- **Ground Locations**: Main Ground (Ratina Stadium), Training (Tullikamari Park)
- **Access Info**: Public transport accessibility

#### Social Media Links
- **Facebook** (fab fa-facebook-f)
- **Twitter** (fab fa-twitter)
- **Instagram** (fab fa-instagram)
- **LinkedIn** (fab fa-linkedin-in)
- **YouTube** (fab fa-youtube)

## Icon System

### Icon Consistency
- **Functional Icons**: `fa-solid` class
- **Social Media Icons**: `fab` class (brand icons)
- **Spacing**: Consistent `me-2` margin
- **Color**: All icons use `var(--sh-orange)`
- **Sizes**: Responsive sizing (0.9rem to 3rem)

### Icon Inventory
- **Navigation**: fa-bars, fa-paper-plane, fa-question-circle, fa-map-marker-alt
- **Contact Info**: fa-envelope, fa-phone, fa-clock, fa-users
- **FAQ Topics**: fa-question-circle, fa-plus-circle, fa-trophy, fa-location-dot, fa-user-plus, fa-shield-halved
- **Social Media**: fab fa-facebook-f, fab fa-twitter, fab fa-instagram, fab fa-linkedin-in, fab fa-youtube

## Interactive Features

### JavaScript Functionality
- **Sidebar Navigation**: Click to open corresponding accordion sections
- **Accordion Sync**: Clicking accordion headers updates sidebar active state
- **Smooth Transitions**: Bootstrap collapse animations
- **Active State Management**: Visual feedback for current section

### Hover Effects
- **Sidebar Links**: Background color change and translateX animation
- **Social Media**: Transform translateY and text shadow
- **Form Fields**: Focus states with orange glow

## Responsive Design

### Breakpoints
- **Large Screens** (lg+): Sidebar + main content layout
- **Mobile/Tablet**: Stacked layout with full-width sections
- **Sticky Sidebar**: Only on large screens

### Mobile Optimizations
- **Touch-friendly**: Larger tap targets
- **Readable Text**: Appropriate font sizes
- **Smooth Scrolling**: Native mobile behavior

## CSS Classes and Styling

### Custom Classes
```css
.contact-nav-link {
    /* Sidebar navigation styling */
    transition: all 0.3s ease;
}

.contact-nav-link:hover {
    background: rgba(255, 153, 0, 0.15);
    transform: translateX(5px);
}

.contact-nav-link.active {
    background: rgba(255, 153, 0, 0.1);
    border-left: 3px solid var(--sh-orange);
}

.social-link {
    /* Social media link styling */
    transition: all 0.3s ease;
}

.social-link:hover {
    color: var(--sh-orange-dark);
    transform: translateY(-3px);
    text-shadow: 0 4px 8px rgba(255, 153, 0, 0.3);
}
```

### Accordion Styling
```css
.accordion-button:not(.collapsed) {
    background: rgba(255, 153, 0, 0.1);
    color: var(--sh-orange);
}

.accordion-button:focus {
    box-shadow: 0 0 0 0.2rem rgba(255, 153, 0, 0.25);
    border-color: var(--sh-orange);
}
```

## User Experience Features

### Navigation Flow
1. **Default State**: Contact form open, sidebar shows active state
2. **FAQ Access**: Click sidebar or accordion header
3. **Contact Details**: Access via sidebar or accordion
4. **Synchronized States**: Sidebar and accordion stay in sync

### Visual Feedback
- **Active States**: Orange highlighting for current section
- **Hover Effects**: Smooth transitions and transforms
- **Focus States**: Form fields with orange glow
- **Loading States**: Smooth accordion animations

### Accessibility
- **ARIA Labels**: Proper accessibility attributes
- **Keyboard Navigation**: Full keyboard support
- **Screen Reader**: Semantic HTML structure
- **Color Contrast**: High contrast for readability

## Technical Implementation

### Dependencies
- **Bootstrap 5**: Accordion, grid system, utilities
- **Font Awesome**: Icon system
- **Custom CSS**: Theme-specific styling
- **JavaScript**: Interactive functionality

### File Structure
```
templates/contact.html
├── Sidebar Navigation
├── Main Content Accordion
│   ├── Contact Form Section
│   ├── FAQ Section
│   └── Contact Details Section
├── Custom CSS
└── JavaScript Functionality
```

### Performance Considerations
- **Minimal JavaScript**: Lightweight interactions
- **CSS Optimizations**: Efficient selectors
- **Icon Loading**: Font Awesome CDN
- **Responsive Images**: Optimized for all devices

## Future Enhancements

### Potential Improvements
1. **Contact Form Validation**: Real-time validation
2. **AJAX Form Submission**: No page reload
3. **Live Chat Integration**: Real-time support
4. **Map Integration**: Interactive Google Maps
5. **Multi-language Support**: Internationalization

### Maintenance Notes
- **Icon Updates**: Keep Font Awesome current
- **Content Updates**: Regular FAQ maintenance
- **Contact Info**: Keep information current
- **Social Links**: Verify all links work

## Design Principles

### Consistency
- **Color Scheme**: Orange theme throughout
- **Typography**: Consistent font weights and sizes
- **Spacing**: Uniform margins and padding
- **Icons**: Consistent sizing and spacing

### Usability
- **Clear Navigation**: Obvious section access
- **Multiple Contact Methods**: Various ways to reach support
- **Self-Service**: FAQ section reduces support load
- **Mobile-First**: Responsive design principles

### Professional Appearance
- **Clean Layout**: Organized, uncluttered design
- **Visual Hierarchy**: Clear information structure
- **Brand Consistency**: Matches site theme
- **Modern Design**: Contemporary UI patterns

---

**Last Updated**: December 2024
**Version**: 1.0
**Status**: Production Ready
