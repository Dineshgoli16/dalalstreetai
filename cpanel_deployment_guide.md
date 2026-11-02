# cPanel Deployment Guide: Dalal Street AI (24/7 Cloud Backend)

This guide walks you through deploying the **Dalal Street AI** backend, web dashboard, and automated 24/7 Telegram cron alerts to your **cPanel hosting** account.

---

## 📦 What's Inside `cpanel_dalal_backend.zip`

The pre-packaged archive is located on your PC at:
- **`c:\Users\dines\CascadeProjects\cpanel_dalal_backend.zip`**
- **`c:\Users\dines\CascadeProjects\indian-stock-ai-agent\cpanel_dalal_backend.zip`**

Contents:
- `passenger_wsgi.py`: WSGI bridge converting FastAPI (ASGI) for cPanel Phusion Passenger via `a2wsgi`.
- `server.py`: Complete FastAPI trading backend.
- `cron_telegram_alerts.py`: Autonomous 24/7 market scanner & Telegram alert script for cPanel Cron Jobs.
- `requirements.txt`: Python package dependencies.
- `.htaccess`: Apache HTTPS redirect and CORS routing rules.
- `.env.example`: Configuration template for API keys and Telegram tokens.
- `public_html/`: Light Theme web dashboard (`index.html`) + downloadable Android APK (`dalal-street-ai.apk`).
- `agents/`, `data_ingestion/`, `screening/`, `risk/`, `data/`: Full quant models and paper trading state.

---

## 🚀 Step 1: Create the Python App in cPanel

1. Log into your **cPanel** dashboard.
2. In the **Software** section, click **"Setup Python App"**.
3. Click the blue **"Create Application"** button.
4. Configure the application:
   - **Python version**: Select **3.10**, **3.11**, or **3.12** (recommended: **3.11**).
   - **Application root**: Enter `dalal-backend` (this creates a folder named `dalal-backend` in your home directory).
   - **Application URL**: 
     - If you want a subdomain: select `api.yourdomain.com`.
     - Or if you want a subfolder: select `yourdomain.com` and type `api` in the box.
     - Or select your main domain if this is the only app.
   - **Application startup file**: Enter `passenger_wsgi.py`.
   - **Application Entry point**: Leave as `application`.
5. Click **"Create"** in the top right.

---

## 📂 Step 2: Upload Files & Install Packages

1. Open cPanel **File Manager**.
2. Navigate into the `dalal-backend` directory created in Step 1.
3. Click **"Upload"** in the top toolbar.
4. Select and upload `cpanel_dalal_backend.zip`.
5. Once uploaded, right-click `cpanel_dalal_backend.zip` in File Manager and select **"Extract"**.
6. Now go back to **cPanel -> Setup Python App** and click on your application:
   - Look at the top for the command to enter the virtual environment, e.g.:
     ```bash
     source /home/youruser/virtualenv/dalal-backend/3.11/bin/activate && cd /home/youruser/dalal-backend
     ```
   - In the **"Configuration files"** field, type `requirements.txt` and click **"Add"**.
   - Click **"Run Pip Install"**.
   *(Alternatively: open cPanel **Terminal**, paste the virtualenv source command above, and run `pip install -r requirements.txt`)*.

---

## 🔑 Step 3: Configure Environment Variables

Under the same **"Setup Python App"** page, scroll down to the **"Environment variables"** section:
1. Click **"Add Variable"**:
   - **Name**: `GEMINI_API_KEY`
   - **Value**: *(Your Google Gemini API Key)*
2. Add another variable (optional):
   - **Name**: `LLM_PROVIDER`
   - **Value**: `gemini`
3. If you want 24/7 Telegram alerts:
   - **Name**: `TELEGRAM_BOT_TOKEN`
   - **Value**: *(Your bot token from @BotFather)*
   - **Name**: `TELEGRAM_CHAT_ID`
   - **Value**: *(Your user/chat ID from @userinfobot)*

*(You can also simply rename `.env.example` to `.env` in File Manager and paste your keys there)*.

---

## 🔄 Step 4: Restart and Verify the Backend

1. At the top of the **Setup Python App** page, click the **"Restart"** button.
2. Open your browser and navigate to:
   ```
   https://api.yourdomain.com/api/health
   ```
3. You will see:
   ```json
   {
     "status": "online",
     "system": "Dalal Street AI",
     "version": "1.1.0"
   }
   ```
   And Swagger interactive API documentation at:
   ```
   https://api.yourdomain.com/docs
   ```

---

## 🌐 Step 5: Deploy the Web Dashboard (Frontend)

If you want the web dashboard accessible at your main website (e.g. `https://yourdomain.com`):
1. In cPanel **File Manager**, go inside `public_html/`.
2. Copy or upload `index.html` and `dalal-street-ai.apk` from the `public_html` folder inside the zip into your cPanel `public_html/`.
3. Open `https://yourdomain.com` in any browser.
4. If your API is on a subdomain (e.g. `https://api.yourdomain.com`), click the **Server (🖧)** button in the top header, enter `https://api.yourdomain.com`, and click OK. The dashboard will now permanently talk to your cPanel API!

---

## 📰 Step 6: Live News & Catalyst Scanning (No Cron Jobs Required)

**No cron jobs or background server daemons are needed!**
The system is architected for on-demand live scanning:
- Whenever you open the **DalalStreetAI** app on your phone (or visit the web dashboard), it automatically:
  1. Triggers `/api/news/scan` to ingest fresh RSS headlines from Moneycontrol, Economic Times, and LiveMint.
  2. Cross-references the news titles and summaries with tracked Nifty Largecaps and high-volume Penny Stocks.
  3. Tags detected ticker catalysts (e.g. `[INFY]`, `[RELIANCE]`, `[SUZLON]`, `[YESBANK]`) with a 1-tap **"Analyze / Trade"** button.
  4. Scans live technical setups and institutional FII/DII cash flows.
- This ensures **zero server background CPU/RAM usage** when you are not using the app, while giving you the freshest breaking news the second you launch the app on your phone.


---

## 📱 Step 7: Connect the Android App

Once your cPanel backend is live:
1. Open the **DalalStreetAI** app on your phone.
2. Tap the **⚙ (Settings)** icon in the top right.
3. Enter your cPanel HTTPS address:
   ```
   https://yourdomain.com
   ```
   *(or `https://api.yourdomain.com`)*.
4. Tap **"Save & Reload"**.
5. Your Android app will now load live data 24/7 over mobile data (4G/5G) or any Wi-Fi network without needing your home PC!
