# RepoScan Detection Logic & Methodology

This document clarifies the conceptual framework behind RepoScan's detection engine, specifically addressing **why** particular methods are used and **how** they interpret legacy code.

---

## 1. "Real" vs "Related" AJAX
RepoScan distinguishes between code that *executes* a request and code that merely *supports* it.

| Category | Indicator | `Is_Counted` | Description |
| :--- | :--- | :--- | :--- |
| **Real AJAX** | `$.ajax`, `fetch`, `xhr.send()` | **YES** | **"The Trigger"**. This is code that initiates an actual network request. For migration, these are the exact API endpoints you must reimplement. |
| **Related** | `ajaxSetup`, `serialize()`, `xhr.open` | **NO** | **"The Preparation"**. This is configuration or data formatting. You typically do not migrate this code directly; you replace it with your new framework's equivalents (e.g., Axios Interceptors). |

**Why this matters:**
Counting "Related" items would inflate your workload estimation. By focusing on "Real" calls, the resulting **Inventory Count** represents the actual number of logical actions your new application must perform.

---

## 2. Static Analysis vs. Crawler
A common question is: *"Don't we need to run the app (Crawler/Console) to see what it does?"*

**The Verdict:** For Code Migration, **Static Analysis (Source Code Reading)** is sufficient for 95% of cases.

### Why Static Analysis Wins for Migration
*   **Visibility**: Code functionality is explicit in the text. `fetch('/api/user')` clearly indicates an intent to fetch user data. You do not need to execute the line to understand its purpose.
*   **Completeness**: A Crawler can only see pages it can click on. If a page is hidden behind a complex login or logic state, a Crawler misses it. Static Analysis reads **every file on the disk**, ensuring 100% coverage.

### When to use the Crawler
The Crawler is included only for **Dependency Discovery**, not logic migration.
*   **CSP Generation**: Detecting external scripts (CDNs, analytics) injected at runtime that a static scanner might miss.
*   **Obfuscated Injections**: Finding scripts loaded via complex `document.write` hacks.

---

## 3. Dynamic content ("The Smoking Gun")
RepoScan detects "Dynamic Writes" (generating HTML/JS/CSS via Strings) without running the code by hunting for **Sinks**.

### How it works
We don't know *what* variable `x` contains, but we know that passing it to certain "Sink" functions is a pattern.

| Code Pattern | The "Sink" (Smoking Gun) | Conclusion |
| :--- | :--- | :--- |
| `div.innerHTML = x` | `.innerHTML =` | UI Injection (HTML) |
| `eval(x)` | `eval(` | Dynamic Script Execution |
| `el.style.cssText = y` | `.cssText =` | Dynamic Styling |

### Why "Dynamic" Findings Matter
Even if the functionality works today, these patterns are **primary blockers** for modern migration.
1.  **Framework Conflict**: React/Angular/Vue expect to control the DOM. `innerHTML` fights against them.
2.  **Security**: These patterns are the main vector for Cross-Site Scripting (XSS).
3.  **Migration Action**: You cannot copy-paste this logic. It requires a **Redesign** (using Data Binding instead of String Concatenation).
