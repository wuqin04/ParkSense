# 🚗 Smart Parking System  
**Team Project for Smart City Innovation Challenge**

---

## 🏙️ Project Overview
The **Smart Parking System** aims to enhance urban mobility and parking efficiency by automating parking management using **IoT sensors**, **computer vision (OCR)**, and **real-time data processing**.  
Our solution provides a **seamless parking experience** by automating slot detection, car plate recognition, and fee calculation — reducing human intervention, congestion, and time wasted searching for parking.

---

## 💡 Creativity & Innovation
Our system integrates **IoT and computer vision** in a compact, cost-efficient design:

- Combines **ultrasonic sensors**, **LED indicators**, and **OCR-based car plate recognition**.  
- Provides **real-time availability updates** before entry.  
- Suggests the **nearest available slot** automatically.  
- Uses a **lightweight Python socket connection** to stream camera data efficiently, overcoming the frame drops common with USB webcams when running **EasyOCR**.  
- Designed to be **scalable and modular**, allowing future integration with mobile apps or payment gateways.

---

## 🌆 Relevance to Smart City Theme
Aligned with **Smart City principles**:

- **Sustainability**: Reduces idle engine time and CO₂ emissions by minimizing time spent searching for parking.  
- **Efficiency**: Automated processes minimize human management and improve space utilization.  
- **Safety**: Reduces congestion at parking entrances and exits.  

This system directly supports **urban automation, traffic efficiency**, and **digital transformation** goals.

---

## ⚙️ Technical Implementation

### 1. System Flow
1. **Before Entry:**
   - A display screen shows the **current available parking slots**.
   - The camera scans the **car plate** using **OCR**.
   - If slots are available, the system:
     - Records the car data in the **database**.
     - Suggests the **nearest available slot**.
     - Opens the **gate automatically**.

2. **Inside the Car Park:**
   - Each parking slot has an **ultrasonic sensor** to detect car presence.
   - **LED indicators** show:
     - 🟢 Green Light Enable → Slot available  
     - 🟢 Green Light Disable → Slot occupied  
   - Data updates in real time to maintain accurate occupancy records.

3. **Exiting the Car Park:**
   - The **camera scans** the plate again to match the entry record.
   - System **updates the database**, calculates the **parking fee**, and displays/prints the total.

### 2. Hardware Components
- **Laptop (Client)** - for running Python and OCR to send data to Raspberry Pi 5
- **Laptop Webcam** – captures live feed for OCR-based plate recognition.  
- **Raspberry Pi 5 (Server)** – for running MicroPython and receive data from Laptop.
- **Raspberry Pi Pico W** – for IoT sensor control and data transmission.  
- **Servo Motor** - act as a control gate for entry/exit.
- **LCD 1602 I2C** - show the availability slots, welcome message, exit message, and total fee texts.
- **Active Infrared Sensor** - detect the car entrying/exiting the car park.
- **Ultrasonic Sensors** – detect car presence in parking slots.  
- **LED Indicators** – display slot availability. 

### 3. Software & Communication
- **Python (OpenCV + EasyOCR)** for plate recognition.  
- **MicroPython (on Pico W)** for sensor control.  
- **Socket Communication** between Python server (laptop) and MicroPython device ensures **real-time data exchange**.  
  - This method was chosen because **USB webcams cause frame drops** and **high latency** during OCR processing.  
  - Using the **laptop webcam via socket connection** allows **smoother frame rates**, higher accuracy, and better synchronization with sensor data.

---

## 🌍 Feasibility & Practical Impact
- **Low-cost prototype** using readily available components.  
- **Scalable** to larger parking areas or multi-level facilities.  
- **Modular design** allows easy integration with cloud services or mobile payment systems.  
- **Environmentally friendly**: reduces fuel waste and urban congestion.  

---

## 🗣️ Presentation & Communication
Our presentation will clearly demonstrate:

- Real-time camera scanning and gate control.  
- Dynamic slot availability updates via LEDs.  
- Live database logging for entries and exits.  
- A clean visual dashboard showing the system flow.  

Each member will explain a specific subsystem (OCR, IoT sensors, communication, database, and UI), ensuring **clarity and confidence**.

---

## 🤝 Teamwork & Documentation
- Work is divided by **functionality** (camera/OCR, sensors, database, server communication, presentation).  
- Version control is managed through **GitHub** for smooth collaboration.  
- Documentation includes **system diagrams**, **code explanations**, and **setup instructions** for reproducibility.

---

## ✅ Summary
The **Smart Parking System** embodies the Smart City vision through **automation**, **real-time monitoring**, and **data-driven efficiency**.  
By integrating IoT with intelligent image processing, our system enhances convenience, reduces traffic, and contributes to a more sustainable urban environment.
