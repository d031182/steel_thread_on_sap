# Chat UI: Sticky Input Field Best Practices

**Created**: 2026-02-15  
**Source**: Perplexity research + Industry standards  
**Purpose**: UX guidelines for chat interface input positioning

---

## 🎯 Core Principle

> **Position the input field as a sticky element fixed at the bottom of the viewport to ensure constant accessibility, while allowing the message area above it to scroll independently.**

This mimics native apps like WhatsApp and prevents input from scrolling out of view during message reading.

---

## 📱 Key Implementation Practices

### 1. Fixed Bottom Positioning

**CSS Pattern**:
```css
/* Input container */
.chat-input-container {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: white;
    border-top: 1px solid #e0e0e0;
    padding: 12px;
    z-index: 1000;
}

/* Messages container - reserve space for fixed input */
.chat-messages-container {
    padding-bottom: 80px; /* Height of input container */
    overflow-y: auto;
    max-height: calc(100vh - 140px); /* Dialog header + input */
}
```

**Why**: Keeps input pinned even with virtual keyboards or orientation changes

---

### 2. Multiline Support & Auto-Expansion

**Pattern**:
```css
.chat-input {
    resize: vertical;
    min-height: 44px;
    max-height: 120px;
    overflow-y: auto;
}
```

**Benefits**:
- Users preview full messages without horizontal scroll
- Improves editing accuracy on touch devices
- Better typing visibility

---

### 3. Thumb-Friendly Touch Targets

**Guidelines**:
- ✅ **Minimum size**: 44x44px for buttons/icons
- ✅ **Spacing**: 8px between tap targets
- ✅ **Placement**: Critical actions (Send) on right for right-handed users
- ✅ **Visual feedback**: Tap animations, color changes

**Example**:
```css
.send-button {
    min-width: 44px;
    min-height: 44px;
    padding: 12px;
    /* Large enough for thumb */
}
```

---

### 4. Scrollable Messages Above

**Pattern**:
```css
.messages-scroll-area {
    overflow-y: auto;
    overflow-x: hidden;
    scroll-behavior: smooth;
    -webkit-overflow-scrolling: touch; /* iOS momentum */
}
```

**Features**:
- Auto-scroll to bottom on new messages
- Smooth scrolling animation
- Preserve scroll position when typing
- Show scroll indicator if not at bottom

---

### 5. Visual Feedback

**Requirements**:
- ✅ Placeholder text: "Type a message..."
- ✅ Send button: Color change on tap, disabled when empty
- ✅ Typing indicators: Animated ellipsis for AI responses
- ✅ Loading states: Show progress during API calls
- ✅ Error states: Red border, clear error message

---

## 🚫 Common Pitfalls to Avoid

### ❌ Problem 1: Input Hidden Behind Keyboard
**Solution**: Use `window.visualViewport` or media queries for iOS/Android

### ❌ Problem 2: Floating Input Scrolls Away
**Solution**: `position: fixed` (not `absolute` or `relative`)

### ❌ Problem 3: Messages Hidden Under Input
**Solution**: Add `padding-bottom` to messages container matching input height

### ❌ Problem 4: Layout Shifts
**Solution**: Reserve space upfront, don't dynamically add/remove

### ❌ Problem 5: Poor Performance on Scroll
**Solution**: 
```css
.messages-container {
    will-change: scroll-position;
    transform: translateZ(0); /* GPU acceleration */
}
```

---

## 📐 Layout Structure

**Recommended DOM**:
```
Dialog
├── Header (fixed top)
├── Messages Container (scrollable, flex-grow: 1)
│   └── Message list (auto-scroll bottom)
└── Input Container (fixed bottom)
    ├── Input field
    └── Send button
```

**Flexbox Pattern**:
```css
.dialog-content {
    display: flex;
    flex-direction: column;
    height: 100%;
}

.messages-container {
    flex: 1;
    overflow-y: auto;
    padding-bottom: 80px; /* Input height */
}

.input-container {
    flex-shrink: 0;
    position: fixed;
    bottom: 0;
}
```

---

## 🎨 SAP Fiori Alignment

**Fiori Guidelines Applied**:
- ✅ Clear visual hierarchy
- ✅ Consistent spacing (rem-based)
- ✅ Accessible colors (WCAG AA)
- ✅ Responsive design (mobile-first)
- ✅ Touch-optimized controls

---

## 📊 Industry Examples

**WhatsApp Web**:
- Fixed input at bottom
- Messages scroll above
- Auto-expand textarea
- Clear send button

**Slack**:
- Sticky composer
- Multiline support
- Quick actions (emoji, attach)
- Persistent input state

**Microsoft Teams**:
- Fixed bottom input
- Format toolbar
- @mentions dropdown
- File preview above input

---

## ✅ Implementation Checklist

- [ ] Input fixed at bottom (`position: fixed`)
- [ ] Messages container has padding-bottom (input height)
- [ ] Scroll area uses `overflow-y: auto`
- [ ] Touch targets ≥ 44x44px
- [ ] Auto-scroll on new messages
- [ ] Multiline textarea support
- [ ] Clear visual feedback (placeholder, button states)
- [ ] Keyboard-friendly (Enter to send)
- [ ] Mobile-tested (iOS + Android)
- [ ] Accessible (screen readers, keyboard nav)

---

## 🔗 References

- [CometChat: Chat App Design Best Practices](https://www.cometchat.com/blog/chat-app-design-best-practices)
- [UXPin: Chat User Interface Design](https://www.uxpin.com/studio/blog/chat-user-interface-design/)
- [Nielsen Norman Group: Chat UX](https://www.nngroup.com/articles/chat-ux/)
- [SAP Fiori Design Guidelines](https://experience.sap.com/fiori-design/)

---

## 🎯 Summary

**The Golden Rule**: Keep input always visible and accessible at the bottom, let messages scroll above. This is the standard pattern used by every major chat application because it works.

**Performance**: 60fps scrolling, GPU acceleration, smooth animations  
**Accessibility**: Keyboard nav, screen readers, high contrast  
**Mobile-first**: Touch targets, thumb zones, responsive layout