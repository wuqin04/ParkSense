function goBack() {
    window.history.back();
}

function homePage() {
    window.location.href = '../index.html';
}

function adminPanel() {
    window.location.href = 'pages/admin.html';
}

function userPanel() {
    window.location.href ='./pages/user_panel.html';
}

function TrackCar() {
        window.location.href ='../pages/track_car.html'
}

async function sendGateCommand(gate, action){
    const MICROPYTHON_IP = "10.38.61.193"; // pico IP
    const PORT = 80; // HTTP port
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
    alert("Opening gate...");
    console.log(`Opening ${selectedGate} gate...`);
    // send command to micropython
    sendGateCommand(selectedGate, "open");
}

function closeGate(){
    const selectedGate = document.getElementById("gateSelector").value;
    alert("Closing gate...");
    console.log(`Closing ${selectedGate} gate...`);
    // send command to micropython
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
