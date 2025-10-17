# 🎓 MedGuard Step-by-Step Execution Guide
## For Complete Beginners - Every Command Explained

This guide assumes you have **ZERO experience** with coding, data science, or cloud platforms. Follow every step exactly as written.

---

## 📋 Pre-Requirements Checklist

Before starting, make sure you have:

- [ ] Access to https://datalab.dive.edito.eu/
- [ ] Your EDITO login credentials
- [ ] GitLab account access (https://gitlab.mercator-ocean.fr/)
- [ ] Copernicus Marine account (create at https://data.marine.copernicus.eu/)
- [ ] Internet connection
- [ ] Computer with at least 8GB RAM

---

## 🌟 DAY 1: SETUP & DATA DOWNLOAD (3-4 hours)

### Step 1.1: Login to EDITO Datalab

1. Open your web browser
2. Go to: https://datalab.dive.edito.eu/
3. Click "Sign In"
4. Enter your credentials
5. You should see the EDITO dashboard

### Step 1.2: Open a Jupyter Lab Service

1. On EDITO dashboard, click "**Catalog**"
2. Find "**Jupyter Python**" service
3. Click "**Launch**"
4. In the configuration screen:
   - **Service Name**: `medguard-dev`
   - **CPU**: Select `2 cores`
   - **Memory**: Select `4GB`
   - **Storage**: `10GB`
5. Click "**Launch Service**"
6. Wait 2-3 minutes for the service to start
7. Click "**Open**" when ready

**What just happened?** You created a cloud-based Python development environment.

### Step 1.3: Open Terminal in Jupyter Lab

1. In Jupyter Lab, look at the top menu
2. Click "**File**" → "**New**" → "**Terminal**"
3. A black terminal window will open
4. This is where you'll type commands

**What is a terminal?** It's a text-based interface to give commands to the computer.

### Step 1.4: Configure Git

In the terminal, type these commands one by one (press Enter after each):

```bash
git config --global user.name "patmekury"
```
Press Enter, then:

```bash
git config --global user.email "patrickobumselu@gmail.com"
```

**What did this do?** It told Git who you are, so your code changes are attributed to you.

### Step 1.5: Create Project Directory

```bash
mkdir medguard-project
```
Press Enter, then:

```bash
cd medguard-project
```

**What did this do?** 
- `mkdir` = "make directory" (create a folder)
- `cd` = "change directory" (move into that folder)

### Step 1.6: Create All Project Files

Copy the code I provided earlier and save them as files. Here's how:

**For each Python file:**

1. In Jupyter Lab, click "**File**" → "**New**" → "**Text File**"
2. Copy the code from the artifact
3. Paste it into the new file
4. Click "**File**" → "**Save As**"
5. Name it exactly as shown (e.g., `download_all_data.py`)
6. Click "**Save**"

**Create these files:**
- `requirements.txt`
- `download_all_data.py`
- `process_data.py`
- `train_models.py`
- `dashboard_app.py`
- `Dockerfile`
- `env.yaml`
- `README.md`

### Step 1.7: Install Python Dependencies

In the terminal, type:

```bash
pip install -r requirements.txt
```

**What does this do?** Installs all the software libraries needed for the project.

**How long does this take?** 10-15 minutes. You'll see lots of text scrolling. This is normal.

**Wait for it to finish** - you'll see a message like "Successfully installed..."

### Step 1.8: Set Up Copernicus Marine Credentials

1. Go to https://data.marine.copernicus.eu/
2. Login or create account
3. In the terminal, type:

```bash
copernicusmarine login
```

4. Enter your Copernicus username when prompted
5. Enter your password when prompted (you won't see it as you type - this is normal)

### Step 1.9: Download Data

Now run the data download script:

```bash
python download_all_data.py
```

**What happens?** The script will download ocean data from various sources.

**How long?** 1-2 hours depending on internet speed.

**What you'll see:**
- Progress bars
- "✓" marks for successful downloads
- "✗" marks if something fails (this is OK, not all data might be available)

**Important:** Some datasets require manual download. The script will give you URLs. If you see manual download instructions:

1. Copy the URL from the terminal
2. Open it in your browser
3. Download the file
4. Save it to the `data/emodnet/` or `data/copernicus/` folder as instructed

### Step 1.10: Verify Data Downloaded

In terminal, type:

```bash
ls -la data/copernicus/
```

You should see files ending in `.nc` (NetCDF files).

```bash
ls -la data/emodnet/
```

You should see files ending in `.geojson`.

**If you see files** - Great! Move to next step.
**If folders are empty** - Check the download script output for errors.

---

## 🌟 DAY 2: DATA PROCESSING (2-3 hours)

### Step 2.1: Process the Raw Data

In terminal, type:

```bash
python process_data.py
```

**What does this do?** Calculates overfishing risk, habitat quality, and other metrics from raw data.

**How long?** 20-30 minutes.

**What you'll see:**
- "Loading..." messages
- "Calculating..." messages
- "✓ Exported..." when files are saved

**Output:** Processed data saved to `data/processed/` folder

### Step 2.2: Check Processed Data

```bash
ls -la data/processed/
```

You should see files like:
- `overfishing_risk_index.nc`
- `juvenile_habitat_score.nc`
- `sst_anomaly.nc`
- `summary_statistics.csv`

### Step 2.3: Read the Processing Report

```bash
cat data/processed/processing_report.txt
```

This shows a summary of what was calculated.

---

## 🌟 DAY 3: TRAIN MODELS (2-3 hours)

### Step 3.1: Train Machine Learning Models

In terminal, type:

```bash
python train_models.py
```

**What does this do?** Trains AI models to predict overfishing risk and forecast juvenile catch.

**How long?** 15-30 minutes.

**What you'll see:**
- Training progress
- Accuracy scores
- Feature importance rankings

**Output:** Models saved to `models/` folder

### Step 3.2: Verify Models Were Created

```bash
ls -la models/
```

You should see:
- `overfishing_risk_model.pkl`
- `juvenile_catch_model.pkl`
- `mpa_scenarios.json`
- `training_summary.json`

---

## 🌟 DAY 4: TEST THE DASHBOARD (1-2 hours)

### Step 4.1: Install Streamlit

```bash
pip install streamlit
```

### Step 4.2: Run Dashboard Locally

```bash
streamlit run dashboard_app.py
```

**What happens?** A web server starts.

**What you'll see:**
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
Network URL: http://xxx.xxx.xxx.xxx:8501
```

### Step 4.3: Access the Dashboard

In EDITO Jupyter Lab:
1. Look for the URL in the terminal output
2. If using EDITO, you might need to set up port forwarding
3. Alternatively, the dashboard will automatically open in a new tab

**What you see:** Interactive dashboard with maps, charts, and controls!

### Step 4.4: Explore the Dashboard

1. **Risk Assessment Tab**: See the overfishing risk map
2. **Trends Tab**: View historical trends and forecasts
3. **Policy Simulator Tab**: Try different MPA expansion scenarios
4. **Data Explorer Tab**: Browse all the data

### Step 4.5: Test Interactivity

- Use the sliders in the sidebar
- Change the MPA expansion percentage
- Adjust the forecast period
- Toggle different map layers

**If something doesn't load:** Don't worry! It might be because some data is missing. The dashboard will show helpful messages.

---

## 🌟 DAY 5: CREATE DOCKER CONTAINER (2-3 hours)

### Step 5.1: Install Docker (if not already installed)

Check if Docker is installed:

```bash
docker --version
```

If you see a version number, Docker is installed. Skip to Step 5.2.

If not, in EDITO, Docker should already be available.

### Step 5.2: Build Docker Image

```bash
docker build -t medguard:1.0 .
```

**What does this do?** Packages your entire application into a container.

**How long?** 10-20 minutes.

**What you'll see:** Many steps executing. Each one is building a layer of your container.

### Step 5.3: Test Docker Container Locally

```bash
docker run -p 8888:8888 medguard:1.0
```

**Access:** Open http://localhost:8888 in your browser

### Step 5.4: Stop the Container

Press `Ctrl+C` in the terminal to stop.

---

## 🌟 DAY 6: PUSH TO DOCKER HUB (1 hour)

### Step 6.1: Create Docker Hub Account

1. Go to https://hub.docker.com/
2. Click "Sign Up"
3. Create free account
4. Remember your username!

### Step 6.2: Login to Docker Hub

In terminal:

```bash
docker login
```

Enter your Docker Hub username and password.

### Step 6.3: Tag Your Image

Replace `<your-dockerhub-username>` with your actual username:

```bash
docker tag medguard:1.0 <your-dockerhub-username>/medguard:1.0
```

Example: If your username is `johndoe`:
```bash
docker tag medguard:1.0 johndoe/medguard:1.0
```

### Step 6.4: Push to Docker Hub

```bash
docker push <your-dockerhub-username>/medguard:1.0
```

**How long?** 5-15 minutes depending on internet speed.

**What you'll see:** Upload progress bars.

---

## 🌟 DAY 7: DEPLOY TO EDITO (2-3 hours)

### Step 7.1: Prepare GitLab Repository

1. Go to https://gitlab.mercator-ocean.fr/
2. Login with your credentials
3. Click "**New Project**"
4. Name it: `medguard-app`
5. Click "**Create Project**"

### Step 7.2: Push Code to GitLab

In terminal, initialize git (if not already):

```bash
git init
git add .
git commit -m "Initial MedGuard application"
```

Add your GitLab repository:

```bash
git remote add origin https://gitlab.mercator-ocean.fr/<your-username>/medguard-app.git
```

Push the code:

```bash
git push -u origin main
```

**If asked for credentials:** Enter your GitLab username and personal access token.

### Step 7.3: Deploy Service on EDITO

1. Go back to EDITO Datalab homepage
2. Click "**My Services**"
3. Click "**+ New Service**"
4. Select "**Custom Docker Image**"
5. Fill in:
   - **Service Name**: `MedGuard`
   - **Docker Image**: `<your-dockerhub-username>/medguard:1.0`
   - **Port**: `8501`
   - **CPU**: `2 cores`
   - **Memory**: `4GB`
   - **Storage**: `10GB`
6. Toggle "**Enable S3 Access**" to ON
7. Click "**Create Service**"

### Step 7.4: Wait for Deployment

**Time:** 5-10 minutes

**What happens:**
- EDITO pulls your Docker image
- Creates a running container
- Assigns a public URL

### Step 7.5: Access Your Deployed Application

1. In "My Services", find your MedGuard service
2. Click "**Open**"
3. Your dashboard opens in a new tab!
4. Share the URL with others

**Your URL will look like:**
```
https://medguard-<random-id>.lab.dive.edito.eu
```

---

## 🎉 CONGRATULATIONS!

You've successfully:
- ✅ Set up EDITO development environment
- ✅ Downloaded ocean data from multiple sources
- ✅ Processed data and calculated overfishing risk
- ✅ Trained machine learning models
- ✅ Created an interactive dashboard
- ✅ Containerized your application
- ✅ Deployed to EDITO cloud platform

---

## 🆘 Common Problems & Solutions

### Problem 1: "Permission Denied" Error

**Solution:**
```bash
chmod +x download_all_data.py
chmod +x process_data.py
chmod +x train_models.py
```

### Problem 2: "Module not found" Error

**Solution:**
```bash
pip install <module-name>
```

### Problem 3: Data Download Fails

**Solution:**
- Check internet connection
- Verify Copernicus credentials
- Try downloading one dataset at a time

### Problem 4: Out of Memory

**Solution:**
- Restart Jupyter kernel: Kernel → Restart Kernel
- Increase service memory in EDITO
- Process smaller data subsets

### Problem 5: Dashboard Won't Load

**Solution:**
```bash
# Check if streamlit is installed
pip install --upgrade streamlit

# Clear cache
streamlit cache clear

# Restart dashboard
streamlit run dashboard_app.py
```

### Problem 6: Docker Build Fails

**Solution:**
```bash
# Clean Docker system
docker system prune -a

# Rebuild with no cache
docker build --no-cache -t medguard:1.0 .
```

---

## 📞 Getting Help

If you're stuck:

1. **Check error messages** - They usually tell you what's wrong
2. **Read the logs** - In EDITO, click on your service and check "Logs" tab
3. **Consult EDITO documentation** - https://docs.lab.dive.edito.eu/
4. **Ask in hackathon Slack/Teams** - Other participants can help
5. **Contact EDITO support** - Use the help button in EDITO Datalab

---

## 📝 Before Presentation

Make sure you have:

- [ ] Working dashboard URL
- [ ] Screenshots of key features
- [ ] Sample results and visualizations
- [ ] Performance metrics
- [ ] Clear explanation of how it addresses SDG 14.4
- [ ] Demonstration plan (2-5 minutes)

---

## 🎓 Key Concepts Explained

**What is NetCDF?** A file format for storing scientific data, especially ocean/climate data.

**What is Docker?** A way to package software so it runs the same everywhere.

**What is an API?** A way for programs to talk to each other and exchange data.

**What is S3?** Cloud storage system (like Dropbox for servers).