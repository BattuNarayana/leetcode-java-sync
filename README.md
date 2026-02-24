# 🔄 LeetCode Java Sync Tool

![Java](https://img.shields.io/badge/Language-Java-orange.svg)
![Python](https://img.shields.io/badge/Script-Python%203.x-blue.svg)
![Automation](https://img.shields.io/badge/Automation-Windows%20Task%20Scheduler-green.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

Automatically syncs your accepted Java submissions from LeetCode into a local folder — organized by topic (Array, Dynamic Programming, Trees, etc.) — and keeps it updated daily using Windows Task Scheduler.

---

### 💡 Why I Built This

Most developers use **VS Code** as their primary coding environment. But when it comes to LeetCode, we solve problems directly on the LeetCode platform — and those solutions just stay there, scattered across the profile with no local backup.

There was no easy way to have all my accepted solutions saved **locally in VS Code**, in a clean and structured format that I could actually browse, revise, and learn from.

**The Problem with existing tools:**
Tools like **LeetHub** and **LeetSync** exist — they are browser extensions that sync your LeetCode submissions to GitHub. But the problem is, **viewing code on GitHub isn't the same as having it locally in VS Code**. GitHub's code viewer lacks the comfort of a proper IDE — no syntax highlighting themes, no file tree navigation the way you're used to, and you can't just open and run the file instantly.

**This tool solves that:**
* 🏠 **Local First:** Your solutions live locally on your machine, inside your VS Code workspace.
* 📁 **Topic-Based:** Organized by topic — just like LeetCode categorizes them.
* 🔁 **Auto-Sync:** Syncs automatically every day in the background — no manual effort needed.
* ⚡ **Ready to Run:** You can open any solution instantly in VS Code, just like any other Java file.

---

### ✨ Features

* ✅ **Accepted Only:** Fetches all your Accepted Java submissions from LeetCode.
* 📁 **Auto-Categorization:** Organizes them into topic-based subfolders (Array, Binary Search, Trees, DP, etc.).
* 🔁 **Incremental Sync:** Only downloads new submissions each run.
* 🗂️ **Reset Option:** Wipe and re-sync everything from scratch when needed.
* 🕐 **Fully Automated:** via Windows Task Scheduler — runs daily without you doing anything.
* 📝 **Sync Logs:** Maintains a `sync_log.txt` so you can always verify it ran.

---

### 📂 Folder Structure After Sync

```text
Java programs/
├── Array/
│   ├── TwoSum.java
│   └── BestTimeToBuyAndSellStock.java
├── Dynamic Programming/
│   ├── ClimbingStairs.java
│   └── LongestCommonSubsequence.java
├── Tree/
│   └── MaximumDepthOfBinaryTree.java
├── sync_log.txt
└── .synced_ids.json
```
---

### 🛠️ Setup Guide

**Step 1 — Install Python**
Download and install Python 3.x from **python.org**. Make sure to check "Add Python to PATH" during installation.

**Step 2 — Install dependencies**
Open Command Prompt and run:

```bash
pip install requests
```

**Step 3 — Get your LeetCode cookies**
This tool uses your browser session to authenticate with LeetCode. Here's how to get your cookies:

Open Chrome or Edge and go to leetcode.com
Make sure you are logged in
Press F12 to open Developer Tools
Click the **Application tab**

On the left panel, expand Cookies → click https://leetcode.com

Find the cookie named LEETCODE_SESSION → copy its Value

Find the cookie named csrftoken → copy its Value

⚠️ Keep these values private! Anyone with your LEETCODE_SESSION cookie can access your account. Never share them or commit them to a public repo.

**Step 4 — Configure the script**
Open leetcode_sync.py in any text editor and fill in:

Python LEETCODE_SESSION = "paste your LEETCODE_SESSION value here"
CSRF_TOKEN = "paste your csrftoken value here"
DEST_FOLDER = r"C:\Users\YourName\path\to\your\Java programs"

**Step 5 — Run it manually first**

```bash
python leetcode_sync.py --reset
```

Type y when prompted. It will sync all your accepted Java submissions into topic folders.

---

### ⚙️ Automate with Windows Task Scheduler

To make the sync run automatically every day:

Find your Python path

```bash
where python
```

Copy the output (e.g. C:\Users\YourName\AppData\Local\Programs\Python\Python311\python.exe)

Open Task Scheduler
Press Windows + S → search Task Scheduler → open it
Create the task
Click "Create Basic Task" on the right
Name: LeetCode Sync → Next
Trigger: Daily → set your preferred time (e.g. 11:00 PM) → Next
Action: Start a program → Next
Program/script: paste your Python path from step 1
Add arguments: C:\path\to\leetcode_sync.py
Click Finish
Verify it's working
Open Task Scheduler → Task Scheduler Library → find LeetCode Sync
Check Last Run Time and Last Run Result (0x0 = success)
Or open sync_log.txt in your Java programs folder and check for a fresh timestamp

---

## Usage

Silent incremental sync (for Task Scheduler)

```bash
python leetcode_sync.py
```

Interactive reset + full re-sync from scratch

```bash
python leetcode_sync.py --reset
```

---

### 🔄 Updating your cookies

LeetCode session cookies expire after some time. If the sync stops working:

Get fresh cookie values from your browser (Step 3 above)
Update LEETCODE_SESSION and CSRF_TOKEN in the script
Run it again

---

### 📌 Notes

Only Accepted submissions are synced.
Only Java submissions are synced (can be changed in the script).
If a problem has multiple topics, it's placed in the first topic listed on LeetCode.
The .synced_ids.json file tracks which submissions have already been saved — don't delete it unless you want a full re-sync.

---

### 🤝 Contributing

Feel free to fork this repo and open pull requests! Some ideas for improvements:

Support for multiple languages
GitHub auto-push after sync
Email/notification after daily sync

---

### 👤 Author
Battu Narayana — built this to keep a clean, organized local backup of LeetCode solutions directly inside VS Code.