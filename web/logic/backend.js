function goBack() {
    window.history.back();
}

function homePage() {
    window.location.href = '../index.html';
}

function adminPanel() {
    window.location.href = '../web/pages/admin.html';
}

function userPanel() {
    window.location.href ='~/web/pages/user_panel.html';
}

function TrackCar() {
        window.location.href ='../pages/track_car.html'
}

function TrackFee(){
        window.location.href ='../pages/user_check_fee.html'
}

async function checkFee(){
    const plateInput = document.getElementById("plate");
    const plate = plateInput.value.trim().toUpperCase().replace(/\s+/g, ""); //.replace(/\s+/g, "") to remove internal space

    const feeBox = document.getElementById("feeBox");
    const entryBox = document.getElementById("entryBox");
    const durationBox = document.getElementById("durationBox");

    // Clear previous results
    feeBox.textContent = "";
    entryBox.textContent = "";
    durationBox.textContent = "";
    
    if(!plate){
        feeBox.textContent = "⚠️ Please enter your car plate number.";
        return;
    }

    try{
        // Change URL if your JSON is hosted elsewhere
        const response = await fetch("../../data.json");
        if (!response.ok) throw new Error(`HTTP ${response.status}`);

        const data = await response.json();
        const cars = data.cars || [];

        const car = cars.find(c => c.car_plate.toUpperCase() === plate);

        if (!car){
            feeBox.textContent = `❌ No record found for ${plate}`;
            return;
        }

        const entry = car.entry_time;
        const exit = car.exit_time;

        if (!entry){
            feeBox.textContent = "⚠️ Entry time not recorded.";
            return;
        }

        const entryTime = new Date(entry);
        const now = exit ? new Date(exit) : new Date();
        const durationTime = Math.max((now - entryTime) / 1000, 0);
        const secondRounded = Math.ceil(durationTime * 100) / 100; // keep 2 decimals

        // === Fee Calculation Logic ===
        let fee = 0;
        if (fee < 20.0 ){
            fee = durationTime / 100.0; // RM1 per next hour
        }

        if (fee >= 20.0) fee = 20.0; // max per day

        // Display values
        entryBox.textContent = entry;
        durationBox.textContent = `${secondRounded.toFixed(2)} seconds`;
        feeBox.textContent = `RM ${fee.toFixed(2)}`;

    } 
    catch (error) {
        console.error("Error fetching data:", error);
        feeBox.textContent = "⚠️ Unable to load parking data. Check your connection or file path.";
    }

}

async function sendGateCommand(gate, action){
    const MICROPYTHON_IP = "172.27.247.193"; // pico IP
    const PORT = 8888; // HTTP port
    const buttons = document.querySelectorAll("button");
    buttons.forEach(b => b.disabled = true); //disable button when gate opening
    const data = {gate, action};

    try{
        const response = await fetch(`http://${MICROPYTHON_IP}:${PORT}/gate`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });
    }

    catch(err){
        console.error("Failed to send command:", err);
        alert(`Error on sending command to ${gate} gate`);
    }

    finally{
        buttons.forEach(b => b.disabled = false);
    }
}

function openGate(){
    const selectedGate = document.getElementById("gateSelector").value;
    console.log(`Opening ${selectedGate} gate...`);
    sendGateCommand(selectedGate, "open");
}

function closeGate(){
    const selectedGate = document.getElementById("gateSelector").value;
    console.log(`Closing ${selectedGate} gate...`);
    sendGateCommand(selectedGate, "close");
}

async function fetchData() {
    try {
        const response = await fetch("../../data.json");
        
        if (!response.ok) {
            document.getElementById("status").innerHTML = "<strong>Status:</strong> The data was failed to fetch.";
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        // successfully fetch the json data
        document.getElementById("status").innerHTML = "<strong>Status:</strong> The data is fetched successfully."
        const rawJsonData = await response.json();
        console.log("Fetched data: ", rawJsonData);

        const data = rawJsonData.cars;
        console.log(data.length);
        
        const tableBody = document.querySelector(".database-table tbody");
        tableBody.innerHTML = "";

        // work with data here
        for (let i = 0; i < data.length; i++) {
            const car = data[i];
            const row = document.createElement("tr");

            const noCell = document.createElement("td");
            noCell.textContent = i + 1;
            
            const plateCell = document.createElement("td");
            plateCell.textContent = car.car_plate;

            const entryTimeCell = document.createElement("td");
            entryTimeCell.textContent = car.entry_time;

            const exitTimeCell = document.createElement("td");
            exitTimeCell.textContent = car.exit_time;

            const feeCell = document.createElement("td");
            feeCell.textContent = car.fee ? parseFloat(car.fee).toFixed(2) : "0.00";

            row.appendChild(noCell);
            row.appendChild(plateCell);
            row.appendChild(entryTimeCell);
            row.appendChild(exitTimeCell);
            row.appendChild(feeCell);

            tableBody.appendChild(row);

        }

    } catch (error) {
        console.error("Error fetching data: ", error);
    }
}

async function updateAdminStatus() {
    const databaseStatus = document.getElementById("database-status");
    const lastAction = document.getElementById("last-action");

    try {
        const response = await fetch("../../data.json");

        if (!response.ok) {
            databaseStatus.innerHTML = 'Database: <span style="color:red;">Disconnected</span>';
            lastAction.innerHTML = "Last Action: <span>—</span>";
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        // If connected
        databaseStatus.innerHTML = 'Database: <span style="color:green;">Connected</span>';

        const data = await response.json();
        console.log("Fetched admin data:", data);

        // Update last action if it exists
        if (data.last_action) {
            lastAction.innerHTML = "Last Action: <span>" + data.last_action + "</span>";
        } else {
            lastAction.innerHTML = "Last Action: <span>None recorded</span>";
        }

    } catch (error) {
        console.error("Error fetching admin status: ", error);
    }
}

// Run this when the admin page loads
if (window.location.pathname.includes("admin.html")) {
    window.onload = updateAdminStatus;
}


/* Function for car tracking panel*/

function randomizeSlots() {
  const slots = document.querySelectorAll('.slot');

  slots.forEach(slot => {
    // Randomly decide if slot is occupied (true/false)
    const isOccupied = Math.random() < 0.5; // 50% chance

    if (isOccupied) {
      slot.classList.remove('available');
      slot.classList.add('occupied');
      slot.style.backgroundColor = 'red';
    } else {
      slot.classList.remove('occupied');
      slot.classList.add('available');
      slot.style.backgroundColor = 'green';
    }
  });
}

setInterval(randomizeSlots, 2000);
// Run once immediately on load
randomizeSlots();





