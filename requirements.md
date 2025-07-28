# DogPuter V3 – MVP Task Breakdown

> **Target Platform:** Flutter (Windows for testing, Android for deployment)  
> **Input:** Xbox Adaptive Controller (2-button only)  
> **Display:** Landscape-only Android device  
> **User:** 6mo Cavalier puppy using two physical buttons  

---

## 📱 App Structure

- [ ] **Landscape-only app**
- [ ] Fullscreen (no system nav/status bar)
- [ ] Two screens:
  - [ ] Reward Game
  - [ ] Activity Menu
- [ ] Navigation bar at top (human-usable only)
  - [ ] Two tabs/buttons: `Game`, `Menu`
  - [ ] Large text, tap-safe, not reachable by dog

---

## 🎮 Mode 1 – Reward Game (Target-the-Button)

**Description:** Highlight left or right. Dog must press matching button.

### UI
- [ ] Split screen left/right
- [ ] Highlight one side using:
  - [ ] Blinking animated border (blue or yellow)
  - [ ] High contrast design

### Game Logic
- [ ] On load/reset:
  - [ ] Pick random target side
  - [ ] Apply highlight to that side
- [ ] If correct button is pressed:
  - [ ] Play "Good boy!" audio
  - [ ] Reset (new target)
- [ ] If incorrect button:
  - [ ] No feedback

### Input Handling
- [ ] Button A = Left
- [ ] Button B = Right

### Audio
- [ ] Play `good_boy.mp3` or TTS immediately on success
- [ ] No sound on failure
- [ ] Audio must play <500ms after press

---

## 🧭 Mode 2 – Activity Selector (Menu)

**Description:** Dog scrolls through 5 options using Button A, selects with Button B.

### UI
- [ ] Horizontal carousel (center-aligned)
- [ ] Items:
  - [ ] `Play`, `Eat`, `Cuddle`, `Sleep`, `Outside`
  - [ ] Each has:
    - [ ] Large image/icon
    - [ ] Large label text
- [ ] Selected item = center item

### Input
- [ ] Button A:
  - [ ] Scrolls to next item (wraps around)
  - [ ] Optional: subtle scroll feedback
- [ ] Button B:
  - [ ] Plays audio cue for selected item (e.g., “Outside!”)
  - [ ] Visual flash/feedback on selected item

### Audio
- [ ] Pre-recorded or TTS clips per activity
- [ ] Use friendly, upbeat tone
- [ ] Prevent overlap if spammed

---

## 🎮 Input Mapping

- [ ] Map Xbox Adaptive Controller buttons:
  - [ ] A = Left (scroll or press left)
  - [ ] B = Right (select or press right)

---


## 🎨 Visual Design

- [ ] Dog-friendly color palette:
  - [ ] Avoid red/green
  - [ ] Use blue/yellow/high-contrast indicators
- [ ] Icons and touch targets ≥64px
- [ ] Minimal UI – remove distractions

---

## 🔊 Audio Handling

- [ ] Central audio service:
  - [ ] pre-recorded sounds
  - [ ] Rate-limited / queue-controlled
- [ ] Assets:
  - [ ] `good_boy.mp3`
  - [ ] `play.mp3`, `eat.mp3`, etc.
  - [ ] Fallback to TTS if asset missing

---

## ⚙️ Config / Constants

- [ ] Define activity options in config map:
  ```dart
  final List<Activity> activities = [
    Activity(label: 'Play', audio: 'play.mp3', icon: 'play.png'),
    ...
  ];

