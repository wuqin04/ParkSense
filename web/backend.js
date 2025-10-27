function databasePanel() {
    window.location.href = './pages/database.html';
}

function adminPanel() {
    window.location.href = '../index.html';
}

async function fetchData() {
    try {
        const response = await fetch("../../data.json");
        
        if (!response.ok) {
            document.getElementById("data").innerHTML = "<strong>Status:</strong> The data was failed to fetch.";
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        // successfully fetch the json data
        document.getElementById("data").innerHTML = "<strong>Status:</strong> The data is fetched successfully."
        const data = await response.json();
        console.log("Fetched data: ", data);

        // work with data here
    } catch (error) {
        console.error("Error fetching data: ", error);
    }
}
