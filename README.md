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
- Implements **multithreading in MicroPython** to handle ultrasonic logic concurrently, allowing each sensor to operate in the background without interrupting other processes.  
- Introduces a **car plate–based eWallet system**, where users’ parking fees are deducted automatically from their account balance linked to their car plate.  
  - If the balance is insufficient, the user can pay via card as an alternative.  
- Designed to be **scalable and modular**, allowing future integration with mobile apps or payment gateways.

---

## 🌆 Relevance to Smart City Theme
Aligned with **Smart City principles**:

- **Sustainability**: Reduces idle engine time and CO₂ emissions by minimizing time spent searching for parking.  
- **Efficiency**: Automated processes minimize human management and improve space utilization.  
- **Convenience**: Enables **cashless and cardless** parking through car plate–linked payment.  
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
   - The **camera scans** the car plate again to match the entry record.
   - The system **calculates the total parking fee** based on duration.  
   - If the car plate is linked to a wallet account:
     - The **fee is automatically deducted** from the car plate’s balance.  
   - If the balance is **insufficient**, the user can **pay by card** at the gate.  
   - The system then **updates the database**, prints a receipt (if needed), and **opens the exit gate**.

---

### 2. Hardware Components
- **Laptop (Client)** – runs Python and OCR to send recognized plate data to Raspberry Pi 5.  
- **Laptop Webcam** – captures live feed for OCR-based plate recognition.  
- **Raspberry Pi 5 (Server)** – runs MicroPython to handle incoming data and coordinate devices.  
- **Raspberry Pi Pico W** – manages IoT sensors and LED indicators through wireless communication.  
- **Servo Motor** – acts as a gate controller for entry/exit operations.  
- **LCD 1602 I2C** – displays parking availability, welcome/exit messages, and total fee information.  
- **Active Infrared Sensor** – detects vehicles entering and exiting the car park.  
- **Ultrasonic Sensors** – detect car presence in individual parking slots.  
- **LED Indicators** – visually show slot availability.  

---

### 3. Software & Communication
- **Python (OpenCV + EasyOCR)** for plate recognition.  
- **MicroPython (on Pico W)** for IoT and sensor management.  
- **Multithreading in MicroPython** is used to run the **ultrasonic detection logic** continuously in parallel threads.  
  - This ensures the sensors collect data in real time without interrupting LED updates or socket communication.  
- **Socket Communication** between the laptop (Python client) and Raspberry Pi 5 (MicroPython server) ensures **real-time data exchange** and synchronization between devices.  
- This design was chosen because **USB webcams cause frame drops and high latency** during OCR processing.  
- Using the **laptop webcam via socket connection** achieves **smoother frame rates**, **higher accuracy**, and **better synchronization** with IoT updates.

---

## 🌍 Feasibility & Practical Impact
- **Low-cost prototype** using readily available components.  
- **Cashless and cardless payment system** via car plate wallet adds real-world practicality and scalability.  
- **Scalable** to larger parking areas or multi-level facilities.  
- **Modular design** allows easy integration with cloud services, banking APIs, or mobile apps.  
- **Environmentally friendly**: reduces fuel waste, emissions, and urban congestion.  

---

## 🗣️ Presentation & Communication
Our presentation will clearly demonstrate:

- Real-time car plate scanning and gate operation.  
- Dynamic slot availability updates through LED indicators.  
- Automated payment using the car plate wallet system.  
- Live database logging for entry, exit, and transaction records.  
- A clean visual dashboard to illustrate system logic and data flow.  

Each team member will explain one subsystem (OCR, IoT sensors, communication, payment, database, and interface), ensuring **clarity, confidence, and technical depth**.

---

## 🤝 Teamwork & Documentation
- Work is divided by **functionality** (camera/OCR, sensors, payment, database, server communication, presentation).  
- Collaboration is managed through **GitHub**, ensuring version control and consistent updates.  
- Documentation includes **system diagrams**, **code explanations**, and **setup instructions** for reproducibility and further development.

---

## ✅ Summary
The **Smart Parking System** embodies the Smart City vision through **automation**, **cashless payment**, and **real-time monitoring**.  
By integrating IoT with intelligent image processing, **multithreaded sensor control**, and a **car plate–linked eWallet**, our system enhances convenience, reduces traffic, and contributes to a more sustainable urban environment.
