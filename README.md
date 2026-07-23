# Catholic Calendar — Daily Email (GitHub Actions edition) ✝️

A personal daily email: every day, if it's a Catholic feast day,
solemnity, or saint's day, you get a message with:

- **What today is**
- **A short reflection** on that saint or feast's life
- **Do's and Don'ts** for the day
- **A Bible verse** tied to that specific saint or feast

No web server, no hosting account, no database. This runs entirely as
a **GitHub Actions scheduled workflow** — GitHub runs the script for
you, on a timer, for free.

---

## How it works

- `liturgical_calendar.py` — the feast/saint database (Easter math for
  moveable feasts, plus 190+ fixed feasts and saints' days, each with
  its own reflection and Bible verse).
- `send_daily_email.py` — checks today's date against that calendar,
  and if there's a feast, emails you. Sends either through **SendGrid**
  or plain **SMTP** (e.g. Gmail) — you only need to set up one of them.
- `.github/workflows/daily-feast-email.yml` — the schedule. GitHub
  spins up a temporary machine once a day, checks out your code, and
  runs the script.

Nothing to deploy, nothing to keep running yourself — as long as the
repo exists on GitHub with the workflow file in it, the schedule runs
on its own.

---

## 1. Choose how to send email

You only need ONE of these two.

### Option A: Gmail (simplest if you already have a Gmail account)
1. Turn on 2-Step Verification on your Google Account, if it isn't already.
2. Go to Google Account → Security → **App Passwords**, and generate one
   for "Mail". You'll get a 16-character password.
3. You'll use your Gmail address as `EMAIL_USER` and that 16-character
   code as `EMAIL_PASSWORD` (not your real Gmail password).

### Option B: SendGrid (free tier, ~100 emails/day)
1. Sign up free at https://signup.sendgrid.com
2. Create an API key: **Settings → API Keys → Create API Key** ("Mail
   Send" permission).
3. Verify a sender address: **Settings → Sender Authentication**.

If you fill in `SENDGRID_API_KEY`, the script uses SendGrid. If you
leave it blank, it falls back to SMTP automatically — you don't need to
set both.

---

## 2. Add your secrets to GitHub (not to any file in the repo)

On GitHub, go to your repo → **Settings → Secrets and variables →
Actions → New repository secret**, and add these one at a time:

| Secret name | Required? | Example |
|---|---|---|
| `TO_EMAIL` | Always | `you@example.com` |
| `FROM_EMAIL` | Always | `you@example.com` |
| `SENDGRID_API_KEY` | Only if using SendGrid | `SG.xxxxx...` |
| `EMAIL_HOST` | Only if using SMTP | `smtp.gmail.com` |
| `EMAIL_PORT` | Only if using SMTP | `587` |
| `EMAIL_USER` | Only if using SMTP | `you@gmail.com` |
| `EMAIL_PASSWORD` | Only if using SMTP | the 16-char app password |

These never appear in your code or your commit history — GitHub
injects them as environment variables only while the workflow is
running.

---

## 3. Upload to GitHub

```bash
git init
git add .
git commit -m "Daily Catholic feast email via GitHub Actions"
git branch -M main
git remote add origin https://github.com/<your-username>/catholic-calendar-email.git
git push -u origin main
```

Once pushed, go to the **Actions** tab on your repo — you should see
the "Daily Catholic Feast Email" workflow listed.

---

## 4. Test it right now (don't wait for the schedule)

Actions tab → **Daily Catholic Feast Email** → **Run workflow** button
→ Run workflow. This triggers it immediately (that's what
`workflow_dispatch` in the yml enables), so you can confirm your
secrets are correct without waiting until tomorrow.

Click into the run to see the log output — it'll tell you exactly what
happened (which feast it found, or why it sent/didn't send).

---

## 5. About the schedule time

```yaml
schedule:
  - cron: "0 5 * * *"
```

This cron is always in **UTC**, and is currently set to `05:00 UTC`
(≈ 06:00 in Lagos/WAT). To change the time, edit the two numbers in
`"0 5 * * *"` (minute, then hour, both UTC) — e.g. `"30 4 * * *"` is
04:30 UTC.

**Honest caveat, already handled:** GitHub automatically disables
scheduled workflows if a repo goes **60 days with no commits** (only
new commits reset that clock — workflow runs, issues, and tags don't
count). Since you likely won't be pushing to this repo often, I've
included a second workflow, `.github/workflows/keepalive.yml`, that
runs once a month and makes a tiny commit (just a timestamp file) if
the repo's been quiet — so the daily email workflow never silently
goes dark. You don't need to do anything for this to work; it's on the
same schedule-based trigger as the main workflow.

---

## Run it locally (optional, for testing before you push)

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
nano .env      # fill in your real values
python3 send_daily_email.py
```

`.env` is git-ignored — it's only for local testing and is never
uploaded or used by the GitHub Actions workflow (which uses the repo
Secrets instead).

---

## Customizing

- **Add more feast/saint days:** open `liturgical_calendar.py` — add a
  row to `_RAW_SAINTS` (reuses a category template for dos/donts) or to
  `FIXED_FEASTS` (fully custom). Format is documented at the top of
  the file.
- **Also message on ordinary (non-feast) days:** set
  `SEND_ON_ORDINARY_DAYS` to `"true"` in the workflow's `env:` block.
- **Change the Bible translation:** verses currently use the
  public-domain Douay-Rheims (Challoner) translation.

---

## License

Use and modify freely for your own personal use.
