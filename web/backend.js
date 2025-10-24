function get_data() {
    fetch('data.json')
        .then(response => {
            if (!response.ok) {
                throw new Error('HTTP Error! status: ${response.status}');
            }
            return response.json();
        })

        .then(data => {
            console.log(data);

            const database_div = document.getElementById('database');

            // Example: Displaying a specific property from the JSON data
            // Assuming your JSON has a structure like: { "name": "John Doe", "age": 30 }
            if (Array.isArray(data)) {
                // If the JSON is an array, you can iterate and display each item
                let htmlContent = '<ul>';
                data.forEach(item => {
                    htmlContent += `<li>${item.name} - ${item.description}</li>`; // Adjust based on your JSON structure
                });
                htmlContent += '</ul>';
                database_div.innerHTML = htmlContent;
            }
        })

        .catch(error => {
            console.error('Error fetching or parsing JSON:', error);
            const database_div = document.getElementById('database');
            database_div.innerHTML = `<p style="color: red;">Failed to load data: ${error.message}</p>`;
        });
}