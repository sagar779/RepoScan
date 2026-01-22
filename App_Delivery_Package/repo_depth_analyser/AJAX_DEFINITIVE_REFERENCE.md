# Definitive AJAX Reference: Methods & Detection

Is the number of ways to use AJAX countable? **YES.**

While developers can write infinite variations of *wrapper functions*, there are only **2 Foundational Mechanisms** in browsers (XHR and Fetch) and a finite list of popular libraries that utilize them.

This document lists **all** standard ways to initiate a network request from client-side JavaScript, categorized by mechanism.

---

## 1. Foundational Browser APIs (The Roots)
Every AJAX library eventually calls one of these.

| Mechanism | Code Pattern | Detection Regex |
| :--- | :--- | :--- |
| **XMLHttpRequest (XHR)** | `new XMLHttpRequest()` | `new\s+XMLHttpRequest` |
| | `.open('GET', ...)` | `\.open\s*\(` |
| | `.send()` | `\.send\s*\(` |
| **Fetch API** (Modern) | `fetch('/api', ...)` | `fetch\s*\(` |
| **SendBeacon** (Analytics) | `navigator.sendBeacon(...)` | `navigator\.sendBeacon` |
| **ActiveX** (IE Legacy) | `new ActiveXObject('Microsoft.XMLHTTP')` | `ActiveXObject` |

---

## 2. Major Libraries (The Wrappers)
99% of web applications use one of these libraries.

### jQuery
| Method | Usage | Detection Regex |
| :--- | :--- | :--- |
| **Core** | `$.ajax({ ... })` | `\$\.ajax\s*\(` |
| **GET** | `$.get(...)` | `\$\.get\s*\(` |
| **POST** | `$.post(...)` | `\$\.post\s*\(` |
| **Script** | `$.getScript(...)` | `\$\.getScript\s*\(` |
| **JSON** | `$.getJSON(...)` | `\$\.getJSON\s*\(` |
| **Load** | `$('#div').load(...)` | `\.load\s*\(` |

### Axios (Most Popular Modern Lib)
| Method | Usage | Detection Regex |
| :--- | :--- | :--- |
| **Instance** | `axios(...)` | `\baxios\s*\(` |
| **Verbs** | `axios.get(...)` | `axios(\.(get|post|put|delete|patch))\s*\(` |
| **Create** | `axios.create(...)` | `axios\.create` |

### SuperAgent
| Method | Usage | Detection Regex |
| :--- | :--- | :--- |
| **Request** | `superagent.get(...)` | `superagent\.(get|post)` |
| | `request.post(...)` | `\brequest\.(get|post)` |

### Other Common Libraries
| Library | Detection Regex |
| :--- | :--- |
| **Angular 1.x** | `\$http` |
| **Angular 2+** | `HttpClient` |
| **Vue Resource** | `\$http` |
| **Prototype.js** | `Ajax\.Request` |
| **MooTools** | `new\s+Request` |

---

## 3. Real-Time & Streaming (The Cousins)
Technically not "AJAX" (which implies short-lived requests), but critical for data depth analysis.

| Mechanism | Usage | Detection Regex |
| :--- | :--- | :--- |
| **WebSockets** | `new WebSocket(...)` | `new\s+WebSocket` |
| **Server-Sent Events** | `new EventSource(...)` | `new\s+EventSource` |
| **Socket.io** | `io(...)` or `io.connect(...)` | `\bio\s*\(` |
| **SignalR** | `HubConnectionBuilder()` | `HubConnectionBuilder` |

---

## 4. Object Literal Context (The "Hidden" AJAX)
Developers often wrap calls in service objects.

| Pattern | Example | Detection Regex |
| :--- | :--- | :--- |
| **Method Definition** | `ajax: function(url) { ... }` | `\bajax\s*:\s*function` |
| **Method Definition** | `fetch: function(data) { ... }` | `\bfetch\s*:\s*function` |
| **Method Definition** | `request: function(opt) { ... }` | `\brequest\s*:\s*function` |

---

## 5. Summary Analysis Table

If you see... | It usually means... | Action Item
--- | --- | ---
`fetch` / `axios` | Modern Codebase | Check `.then()` for data usage
`$.ajax` / `xhr` | Legacy Codebase | Check `success:` or `onreadystatechange`
`sendBeacon` | Analytics/Tracking | Often 3rd party, low priority for logic
`WebSocket` | Chat/Notifications | High complexity, check message handlers
`eval()` inside AJAX | **RCE Vulnerability** | **CRITICAL SECURITY RISK**
`.innerHTML` inside AJAX | **XSS Vulnerability** | **HIGH SECURITY RISK**

---

### Conclusion
While code can be complex, the **entry points** for network traffic are finite. By monitoring the **2 Root APIs** and the **Top 5 Libraries**, you cover >99% of all traffic.
