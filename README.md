# Ostad EveLogExp (Enterprise Forensic & Threat Analysis Edition)

<p align="center">
  <img src="assets/ostad_logo.jpg" alt="Ostad Red Team Forge" width="220" />
</p>

<p align="center">
  <strong>Official Security & Forensic Log Investigation Tool</strong><br>
  <strong>Ostad Red Team Forge</strong><br>
  <em>Founder & Director: Ostad Rezaul Karim</em><br>
  <code>Top 1% Red Teamer • Cybersecurity Expert • Ethical Hacker • App & Web Developer • IT Expert</code>
</p>

---

## 📌 ওভারভিউ (Overview)

**Ostad EveLogExp** হলো একটি হাই-পারফরম্যান্স উইন্ডোজ ইভেন্ট লগ অ্যানালাইসিস এবং ফরেনসিক ইনভেস্টিগেশন প্ল্যাটফর্ম। এটি বড় বড় নেটওয়ার্ক, সার্ভার এবং ক্লায়েন্ট পিসি থেকে লাইভ চ্যানেল (System, Security, Application, PowerShell, Sysmon ইত্যাদি) এবং ড্যামেজড বা এক্সটার্নাল `.evtx` / `.evt` ফাইল গভীর পর্যবেক্ষণ, ফিল্টারিং, কালার-কোডিং এবং থ্রেট হান্টিংয়ের জন্য প্রস্তুত করা হয়েছে।

---

## 🚀 প্রধান ফিচারসমূহ (Core Features)

1. **উইন্ডো টাইটেল ও ব্র্যান্ডিং:**
   - টাইটেল: `Untitled.ELX - Ostad EveLogExp | Ostad Red Team Forge`
   - অফিশিয়াল লোগো ব্যাজ ও হাই-রেজোলিউশন `.ico` আইকন ইন্টিগ্রেশন।

2. **মাল্টি-মেশিন ও মাল্টি-চ্যানেল 'Merger' ভিউ:**
   - একাধিক সার্ভার/কম্পিউটার (SRV002, MIKE-LN, VM11) এবং চ্যানেল থেকে আসা ইভেন্টগুলোকে একটি একক টাইমলাইনে একত্রিত ও ক্রমানুসারে সাজিয়ে দেখার সুবিধা।

3. **ইনভেস্টিগেশন টাস্ক ও টেমপ্লেটস (Task Templates):**
   - **Audit Templates:** `Audit RDP logons`, `Audit failures`, `Audit logons`, `Audit interactive logons`, `Audit policy change`, `Clear event log`, `User account management`, `Member added to group`, `File deletion` ইত্যাদি।
   - **System Templates:** `Service installation & crashes`, `System boot & shutdown` ইত্যাদি।
   - 'Create task from template' উইজার্ডের মাধ্যমে XML কোয়েরি বিল্ড ও এক্সিকিউশনের সুবিধা।

4. **ফরেনসিক ডিপ স্ক্যান (Forensic Deep Scan):**
   - নষ্ট বা ক্ষতিগ্রস্ত `.evtx` ফাইল বা কাঁচা ডিস্ক ইমেজ থেকে ইনট্যাক্ট ইভেন্ট রেকর্ড পুনরুদ্ধার এবং ডায়াগনস্টিক আউটপুট লগ প্রদান।

5. **এনালিস্ট-কন্ট্রোল্ড AI Copilot:**
   - টুলবারে থাকা নীল `AI` বাটনের মাধ্যমে যেকোনো ইভেন্ট আইডির তাৎক্ষণিক থ্রেট হাইপোথিসিস ও টিআই/সিআইএ ট্রায়াজ প্রম্পট জেনারেশন।

6. **সিগনেচার কালার-কোডিং সিস্টেম:**
   - এরর ও ক্রিটিক্যাল ইভেন্টে রেড হাইলাইট, অডিট ফেইলিওরে ক্রিমসন, ওয়ার্নিং-এ অ্যাম্বার, অডিট সাকসেসে সফট গ্রিন।
   - কাস্টম রুল বিল্ডারের মাধ্যমে যেকোনো Event ID বা Text-এর ওপর ভিত্তি করে নিজস্ব কালার কোড যুক্ত করার সুবিধা (`Ctrl+K`)।

7. **এক্সপোর্ট ইঞ্জিন:**
   - রেসপনসিভ একক-ফাইল **HTML Web Report**, **Excel CSV**, **JSON**, এবং **XML** ফরম্যাটে সরাসরি এক্সপোর্ট।

---

## 🏃 কীভাবে রান করবেন? (How to Run)

### পদ্ধতি ১: স্ট্যান্ডঅ্যালোন EXE চালান (কোনো পাইথন লাগবে না)
সরাসরি ডাবল ক্লিক করুন:
`dist\OstadEveLogExp\OstadEveLogExp.exe`

### পদ্ধতি ২: স্ক্রিপ্ট রান করুন (Python)
ফোল্ডারে থাকা `run.bat` ফাইলটিতে ডাবল ক্লিক করুন অথবা টার্মিনালে চালান:
```powershell
python main.py
```

---

## 🌐 গিটহাবে কীভাবে পুশ করবেন? (How to Push to GitHub)

### পদ্ধতি ১: অটোমেটেড ব্যাচ ফাইলের মাধ্যমে (সহজ পদ্ধতি)
১. ফোল্ডারে থাকা `push_to_git.bat` ফাইলে ডাবল ক্লিক করুন।
২. আপনার গিটহাব রিপোজিটরির লিংক (e.g. `https://github.com/username/OstadEveLogExp.git`) পেস্ট করে Enter দিন। স্ক্রিপ্টটি স্বয়ংক্রিয়ভাবে গিটহাবে পুশ করে দেবে!

---

### পদ্ধতি ২: টার্মিনাল / কমান্ড লাইনের মাধ্যমে (Manual CLI)
১. [GitHub.com](https://github.com) এ লগইন করে **New Repository** তৈরি করুন (যেমন নাম দিন: `OstadEveLogExp`)।
২. PowerShell বা CMD খুলে এই প্রোজেক্ট ফোল্ডারে ঢুকুন:
   ```bash
   cd "c:\Users\USER\Downloads\All Clone Tools\EventLogExplorer"
   ```
৩. গিট ইনিশিয়ালাইজ করুন ও ফাইল অ্যাড করুন:
   ```bash
   git init
   git add .
   git commit -m "Initial Release: Ostad EveLogExp v1.0 - Ostad Red Team Forge"
   ```
৪. মেইন ব্রাঞ্চ সেট করে রিমোট রিপো লিংক যুক্ত করুন:
   ```bash
   git branch -M main
   git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/OstadEveLogExp.git
   ```
   *(নোট: `<YOUR_GITHUB_USERNAME>`-এর জায়গায় আপনার গিটহাব ইউজারনেম দিন)*
৫. গিটহাবে পুশ করুন:
   ```bash
   git push -u origin main
   ```

---

### পদ্ধতি ৩: GitHub Desktop অ্যাপ্লিকেশনের মাধ্যমে
১. আপনার পিসিতে **GitHub Desktop** ওপেন করুন।
২. মেনু থেকে `File` ➔ `Add Local Repository` নির্বাচন করুন।
৩. পাথ হিসেবে সিলেক্ট করুন: `c:\Users\USER\Downloads\All Clone Tools\EventLogExplorer`
৪. Commit বক্সে লিখুন: `Initial release of Ostad EveLogExp` এবং **Commit to main** বাটনে ক্লিক করুন।
৫. উপরের **Publish repository** বাটনে ক্লিক করলেই প্রজেক্টটি সরাসরি আপনার গিটহাব একাউন্টে চলে যাবে!
