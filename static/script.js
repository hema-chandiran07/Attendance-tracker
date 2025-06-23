// Function to fetch and display attendance records
function fetchAttendance() {
    // Fetch the attendance data from the Flask backend
    fetch('/attendance')
        .then(response => response.json())  // Parse the JSON response
        .then(data => {
            // Get the attendance list container from HTML
            const list = document.getElementById('attendanceList');
            
            // Clear the current list
            list.innerHTML = '';

            // Loop through the data and create list items
            data.forEach(record => {
                const li = document.createElement('li');
                li.textContent = `${record[1]} (${record[2]}) at ${record[3]}`; // Format: Name (Status) at Timestamp
                list.appendChild(li);  // Append the new list item to the attendance list
            });
        })
        .catch(err => console.error('Error fetching attendance:', err));  // Handle any errors
}

// Call the function to fetch attendance when the page loads
window.onload = fetchAttendance;
