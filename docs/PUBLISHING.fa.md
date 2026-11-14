# انتشار فالینو در گیت‌هاب

این راهنما برای اولین انتشار سورس آماده‌شده است. انتشار کد روی گیت‌هاب، ربات تلگرام را خودکار آنلاین نمی‌کند؛ اجرای دائمی همچنان به سرور و `.env` نیاز دارد.

## فایل‌های آماده

- `LICENSE`: متن کامل MIT به نام Pouya Poorrahman و مشارکت‌کنندگان فالینو.
- `README.md` و `README.fa.md`: معرفی، امکانات، نصب، پنل، محدودیت‌ها و حریم خصوصی.
- `NOTICE.md` و `REFERENCES.md`: اعتبار منبع محتوا، بسته‌ها و مخزن‌های بررسی‌شده.
- `CONTRIBUTING.md` و `SECURITY.md`: مشارکت و گزارش مشکل امنیتی.
- `.github/workflows/ci.yml`: تست Python و ساخت Docker بدون توکن واقعی.
- قالب گزارش باگ، درخواست قابلیت و توضیح pull request.

## مخزن این پروژه

مخزن اصلی با نام **Falino** در [ByeCoder/Falino](https://github.com/ByeCoder/Falino) قرار دارد. برای گرفتن کد:

```bash
git clone https://github.com/ByeCoder/Falino.git
cd Falino
```

راهنمای بعدی برای انتشار در مخزن شخصی تازه یا fork خودت است. مخزن اصلی را دوباره نساز. در نصب جدید، زبان ربات از انتخاب کاربر در اولین ورود می‌آید؛ README اصلی انگلیسی و راهنمای فارسی مستقل است.

نام نمونه برای مخزن شخصی: `Falino`. عمومی یا خصوصی‌بودن را خودت انتخاب کن؛ MIT نوع مجوز کد است و به تنهایی مخزن را عمومی نمی‌کند.

## روش ساده از وب

۱. در GitHub گزینه **New repository** را باز کن.

۲. نام مخزن و توضیح را وارد کن. توضیح پیشنهادی:

```text
A friendly multilingual Telegram horoscope and tarot bot built with Telethon, SQLite, admin analytics, support tickets and targeted channel membership.
```

۳. برای انتقال کامل این پروژه، مخزن را **بدون README، license و gitignore خودکار** بساز؛ نسخه‌های این فایل‌ها همین‌جا آماده‌اند.

۴. از **uploading an existing file** فایل‌های داخل پوشه پروژه را منتقل کن. ریشه مخزن باید مستقیماً شامل `astrobot/`، `README.md`، `LICENSE` و `compose.yaml` باشد؛ خود ZIP را به‌جای سورس آپلود نکن. برای انتقال پوشه‌های نقطه‌دار و تاریخچه، روش Git مطمئن‌تر است.

## روش Git

در سیستم خودت، ZIP را استخراج کن و وارد پوشه‌ای شو که `README.md` و `astrobot/` در آن قرار دارند:

```bash
git init -b main
git add .
git commit -m "Publish Falino with MIT license and documentation"
```

آدرس واقعی مخزنی که ساختی را جایگزین `YOUR_REPOSITORY_URL` کن:

```bash
git remote add origin YOUR_REPOSITORY_URL
git push -u origin main
```

این روش برای یک مخزن واقعاً خالی است؛ اگر مقصد از قبل محتوا دارد، تاریخچه را بررسی کن و از `force push` برای جایگزینی نامشخص استفاده نکن.

## روش GitHub CLI

اگر `gh` روی سیستم خودت نصب و وارد حساب خودت شده باشد:

```bash
gh auth login
```

پس از ساخت commit محلی، یکی از این دو را با توجه به انتخابت اجرا کن:

```bash
# مخزن خصوصی
gh repo create Falino --private --source=. --remote=origin --push
```

```bash
# مخزن عمومی
gh repo create Falino --public --source=. --remote=origin --push
```

این دو دستور جایگزین یکدیگرند؛ هر دو را اجرا نکن. رمز، PAT یا کد ورود را در چت یا داخل فایل پروژه قرار نده؛ از روش ورود امن خود GitHub استفاده کن.

## بعد از انتقال

- صفحه مخزن باید کد، لوگو، راهنمای فارسی و نشان MIT را نمایش بدهد.
- در تب **Actions**، نتیجه CI را ببین. سبزشدن تست محلی به معنی اجراشدن workflow در GitHub نیست.
- job ساخت Docker فقط تصویر را می‌سازد؛ هیچ سروری را deploy نمی‌کند.
- مسیرهای داده، `.env`، session، کلیدها و بکاپ‌ها توسط `.gitignore` کنار گذاشته می‌شوند.
- بدون اطلاعات واقعی Telegram یا مدل ترجمه، تست‌های خودکار قابل اجرا هستند؛ تست تولیدی و مجوز کانال‌ها جداست.

## منابع رسمی

- [ساخت مخزن](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-new-repository)
- [انتقال پروژه محلی به GitHub](https://docs.github.com/en/migrations/importing-source-code/using-the-command-line-to-import-source-code/adding-locally-hosted-code-to-github)
- [MIT License](https://choosealicense.com/licenses/mit/)
