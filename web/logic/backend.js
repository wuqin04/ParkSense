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

function openGate() {
  const selectedGate = document.getElementById("gateSelector").value;
  alert("Opening gate...");
  console.log(`Opening ${selectedGate} gate...`);
  // send command to micropython
}

function closeGate() {
  const selectedGate = document.getElementById("gateSelector").value;
  alert("Closing gate...");
  console.log(`Closing ${selectedGate} gate...`);
  // send command to micropython
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
