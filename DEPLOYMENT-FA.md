# راهنمای دقیق نصب روی mhnamdar.github.io

این پروژه برای ریپازیتوری فعلی زیر آماده شده است:

```text
https://github.com/mhnamdar/mhnamdar.github.io
```

شاخه فعلی ریپازیتوری `master` است، ولی workflow روی هر دو شاخه `master` و `main` کار می‌کند.

## روش پیشنهادی و امن

### ۱. فایل ZIP را باز کن

```bash
cd ~/Downloads
unzip mhnamdar-faculty-site.zip
```

### ۲. ریپازیتوری فعلی را clone یا update کن

```bash
cd ~/Documents
git clone https://github.com/mhnamdar/mhnamdar.github.io.git
cd mhnamdar.github.io
git pull
```

اگر قبلاً clone شده:

```bash
cd /PATH/TO/mhnamdar.github.io
git pull
```

قبل از ادامه باید این دستور خروجی خالی بدهد:

```bash
git status --porcelain
```

### ۳. اسکریپت جایگزینی امن را اجرا کن

از پوشه پروژه جدید:

```bash
cd ~/Downloads/mhnamdar-faculty-site
bash scripts/replace_existing_site.sh ~/Documents/mhnamdar.github.io
```

این اسکریپت:

1. از سایت قدیمی یک branch آرشیوی محلی می‌سازد.
2. پوشه `.git` را دست نمی‌زند.
3. فایل‌های Jekyll/AcademicPages قدیمی را پاک می‌کند.
4. پروژه جدید را منتقل می‌کند.
5. داده‌ها و build را تست می‌کند.

### ۴. قبل از انتشار سایت را ببین

```bash
cd ~/Documents/mhnamdar.github.io
python3 scripts/dev.py
```

مرورگر:

```text
http://localhost:8000
```

توقف سرور:

```text
Ctrl + C
```

### ۵. Commit و Push

```bash
git add -A
git commit -m "Launch redesigned academic website"
git push origin master
```

برای ذخیره branch آرشیوی روی GitHub، نام branch را که اسکریپت چاپ کرده push کن؛ مثلاً:

```bash
git push origin archive-before-redesign-20260804-030000
```

## فعال‌کردن GitHub Pages

در GitHub وارد ریپازیتوری شو:

```text
Settings → Pages → Build and deployment → Source → GitHub Actions
```

بعد در تب `Actions`، workflow زیر اجرا می‌شود:

```text
Build and deploy academic website
```

پس از سبزشدن workflow، آدرس سایت:

```text
https://mhnamdar.github.io/
```

## برای تغییر اطلاعات سایت

فایل اصلی:

```text
data/site.json
```

پس از تغییر:

```bash
python3 scripts/check.py
python3 scripts/build.py
git add -A
git commit -m "Update academic profile"
git push origin master
```

## برای نوشتن بلاگ، خاطره یا Research Note

یک فایل Markdown در این پوشه بساز:

```text
content/blog/
```

نمونه:

```md
---
title: First months in Santiago
date: 2026-08-10
category: Memories
tags: [Chile, Santiago, academic life]
excerpt: A short memory from the beginning of my PhD in Chile.
featured: false
---

متن اصلی اینجا نوشته می‌شود.
```

دسته‌ها خودکار به فیلترهای صفحه Blog تبدیل می‌شوند. برای پست ناتمام بنویس:

```text
draft: true
```

## نکته‌های مهم

- پوشه `.git` را حذف نکن.
- فقط پوشه `dist` را دستی push نکن؛ کل سورس پروژه باید در GitHub باشد.
- فایل‌های سایت با GitHub Actions ساخته می‌شوند.
- هیچ آمار جعلی مثل citation count، h-index، سن جهان یا Ωm در پروفایل قرار داده نشده است.
- پروژه‌های پیشنهادی با برچسب `Exploratory direction` از کارهای فعال جدا شده‌اند.
- برای تغییر ایمیل، لینک‌ها، همکاران یا وضعیت مقاله‌ها فقط `data/site.json` را ویرایش کن.
