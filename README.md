# **Smart Monitoring System (Team 18)**

This project is an **IoT-based smart monitoring solution** utilizing two **Raspberry Pi 4** devices:

- **Dashboard Pi (MERN Stack)**: Manages user interactions, displays live video, logs alerts, and integrates Telegram notifications.
- **Analytics Pi (AI Processing)**: Performs **object detection, facial recognition, audio monitoring, and gesture recognition**, then sends results to Dashboard Pi via **MQTT**.

---

## **📌 System Overview**

The system consists of multiple **sensors and AI models** that detect environmental changes and respond accordingly.

### **📷 Live Video Feed**

- Users can view the live camera feed **from the Analytics Pi** on the dashboard.
- Video is streamed via **MQTT/WebRTC**.

### **⚠️ Alert Panel**

- Displays **alerts sent by Analytics Pi** when a security event is detected.
- Alerts include:
  - Unrecognized faces
  - Suspicious objects (e.g., unattended parcels)
  - Unrecognized voices
  - Gesture-based intruder detection

### **👥 User Management**

- Users can **add, edit, or delete household members**.
- Registered users' **faces and voices** are stored for recognition.
- Unrecognized individuals trigger **security alerts**.

### **📩 Telegram Notifications**

- When an **alert is triggered**, it is:
  1. **Logged into SQLite**.
  2. **Displayed on the alert panel**.
  3. **Sent as a Telegram message** via the bot.

---

## **📜 System Architecture**

This project is structured as follows:

```
smart-monitoring-system/
│── 📂 dashboard_pi/                 # Dashboard Raspberry Pi (MERN stack, UI, storage)
│    ├── 📂 backend/                  # Express.js API & MQTT processing
│    │    ├── routes/                 # API endpoints
│    │    ├── controllers/            # Main logic for API endpoints
│    │    ├── models/                 # SQLite database handlers
│    │    ├── services/               # MQTT & Telegram handlers
│    │    ├── server.js               # Main Express.js backend
│    │    ├── database/               # Local SQLite storage
│    ├── 📂 frontend/                  # React.js dashboard UI
│    │    ├── src/                     # Components & pages
│    │    ├── package.json             # React dependencies
│
│── 📂 analytics_pi/                   # AI Processing Raspberry Pi (Machine Learning)
│    ├── 📂 mqtt/                       # MQTT clients for AI processing
│    ├── 📂 ai_models/                  # AI models for detection
│    ├── 📂 devices/                    # Sensor data collection scripts
│    ├── analytics_main.py              # Main script for Analytics Pi (Runs everything)
│
│── 📂 docs/                            # Documentation
│    ├── system_architecture_block_diagram.jpeg
│    ├── flow_diagram.jpeg
│    ├── DesignDocument_Team18.pdf
│
│── .gitignore                          # Ignore unnecessary files
│── README.md                           # Project overview, setup instructions
│── docker-compose.yml                   # Docker for running services
```

---

## **🖼️ Architecture & Flow Diagram**

### **System Architecture**

![System Architecture](docs/system_architecture_block_diagram.jpeg)

### **Flow Diagram**

![Flow Diagram](docs/flow_diagram.jpeg)

---

## **🚀 Setup Instructions**

### **🔧 Hardware Requirements**

- **2 x Raspberry Pi 4 (4GB RAM minimum recommended)**
- **Raspberry Pi Camera Module** (for Analytics Pi)
- **USB Microphone** (for Analytics Pi)
- **Accelerometer Sensor** (for Analytics Pi)
- **MicroSD Card (32GB or larger)**
- **Power Supply for Raspberry Pi**
- **Local Network Connection (WiFi or Ethernet)**

---

### **🌐 Naming the Dashboard Pi for Network Access**

The **Dashboard Pi** must be named **`dashboard-pi`** to ensure that it can be accessed as `dashboard-pi.local` on the local network.

#### **🆕 Setting the Name When Installing the OS (Recommended)**

1. **Flash the Raspberry Pi OS** using **Raspberry Pi Imager** (from [here](https://www.raspberrypi.com/software/)).
2. **Before writing the image**, click the ⚙️ **Advanced Options**.
3. Enable **Set hostname** and enter:
   ```
   dashboard-pi
   ```
4. Complete the OS installation, insert the SD card, and boot the Raspberry Pi.
5. Verify the hostname by running:
   ```bash
   hostname
   ```
   It should return:
   ```
   dashboard-pi
   ```
6. Now, you can access the Pi using:
   ```
   ping dashboard-pi.local
   ```

---

#### **🔄 Changing the Hostname on an Already Installed OS**

If you've already installed the OS and need to rename your Raspberry Pi:

1️⃣ Open a terminal and check the current hostname:

```bash
hostname
```

2️⃣ Edit the **hostname file**:

```bash
sudo nano /etc/hostname
```

Replace the existing name with:

```
dashboard-pi
```

3️⃣ Also, update **hosts file**:

```bash
sudo nano /etc/hosts
```

Find the line:

```
127.0.1.1  raspberrypi
```

Change it to:

```
127.0.1.1  dashboard-pi
```

4️⃣ Save the file (**Ctrl+X → Y → Enter**) and reboot:

```bash
sudo reboot
```

5️⃣ After rebooting, verify with:

```bash
hostname
ping dashboard-pi.local
```

Now, the Dashboard Pi should be accessible via `dashboard-pi.local`.

Since the **Analytics Pi** connects to the **MQTT broker running on the Dashboard Pi**, the hostname **must be `dashboard-pi`** for correct operation.

✅ **All connections in the project (MQTT broker, API, website) rely on**:

```
dashboard-pi.local
```

This ensures that **the broker, frontend, and backend communicate seamlessly** without needing manual IP configurations.

---

### **🖥️ Setting Up Dashboard Pi** (MERN Stack, SQLite, MQTT)

The **Dashboard Pi** handles the **web interface, database, and MQTT broker**.

#### **1️⃣ Install Node.js**

If Node.js is not installed, run:

```bash
sudo apt update
sudo apt install -y nodejs npm
```

Verify installation:

```bash
node -v
npm -v
```

#### **2️⃣ Install Dependencies**

```bash
cd dashboard_pi/backend
npm install
cd ../frontend
npm install
```

#### **3️⃣ Install and Configure Mosquitto MQTT Broker**

Since the **Dashboard Pi** is the MQTT broker, install Mosquitto:

```bash
sudo apt update
sudo apt install -y mosquitto mosquitto-clients
```

Enable and start Mosquitto:

```bash
sudo systemctl enable mosquitto
sudo systemctl start mosquitto
```

Check if it's running:

```bash
systemctl status mosquitto
```

If `Active: active (running)` appears, Mosquitto is set up.

#### **5️⃣ Start Dashboard Services (Backend & Frontend)**

```bash
cd dashboard_pi/backend
node server.js  # Runs backend (includes Database, MQTT handling & Telegram bot)
```

```bash
cd ../frontend
npm run dev  # Starts React.js + Vite frontend
```

#### **6️⃣ Test MQTT Broker**

Open **two terminal windows**:

- **Terminal 1 (Subscribe to a topic)**:
  ```bash
  mosquitto_sub -h localhost -t "test/topic"
  ```
- **Terminal 2 (Publish a message to the topic)**:
  ```bash
  mosquitto_pub -h localhost -t "test/topic" -m "Hello MQTT!"
  ```

If Terminal 1 receives `"Hello MQTT!"`, the MQTT broker is working.

---

### **🖥️ Setting Up Analytics Pi** (AI Processing, Sensors, MQTT)

The **Analytics Pi** is responsible for **AI processing, sensor monitoring, and sending alerts to the Dashboard Pi**.

#### **1️⃣ Install Python**

If Python is not installed, run:

```bash
sudo apt update
sudo apt install -y python3 python3-pip
```

Verify installation:

```bash
python3 --version
pip3 --version
```

#### **2️⃣ Install Dependencies**

```bash
cd analytics_pi
pip install -r requirements.txt
```

#### **3️⃣ Start Analytics Services**

```bash
python analytics_main.py  # Runs AI models, MQTT communication, and sensors asynchronously
```

---

## **📌 Features Overview**

| Feature                | Description                                                         |
| ---------------------- | ------------------------------------------------------------------- |
| 🎥 **Live Video Feed** | View live camera feed from **Analytics Pi** on the dashboard.       |
| 🚨 **Alert Panel**     | Displays **security alerts** sent by Analytics Pi via MQTT.         |
| 👤 **User Management** | Add/edit/delete household members for **face & voice recognition**. |
| 🔔 **Telegram Alerts** | Sends **real-time notifications** for security events.              |

---

## **📜 Design Document**

For detailed project documentation, refer to **`docs/DesignDocument_Team18.pdf`**.

---

## **🤝 Team Members**

| Team Members            | Student ID |
| ----------------------- | ---------- |
| Abdullah Waafi Bin Adam | 2201228    |
| Gavin Tang Bing Yuan    | 2203660    |
| Goh Shuang Claire       | 2202682    |
| Claris Toh              | 2203422    |
| Vianiece Tan Yingqi     | 2202045    |

---

## **📜 License**

This project is licensed under **MIT License**.

---
