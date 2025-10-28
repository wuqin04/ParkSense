function goBack() {
    window.history.back();
}

function homePage() {
    window.location.href = '../index.html';
}

function databasePanel() {
    window.location.href = './database.html';
}

function adminPanel() {
    window.location.href = 'pages/admin.html';
}

function userPanel() {
    window.location.href ='./pages/userpage2.html';
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
            feeCell.textContent = car.fee;

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
