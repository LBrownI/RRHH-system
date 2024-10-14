function fetchEmployeeName() {
    var employeeId = document.getElementById('employee_id').value;
    var employeeNameSpan = document.getElementById('employee_name');

    if (employeeId) {
        fetch(`/get_employee_name/${employeeId}`)
            .then(response => {
                if (response.ok) {
                    return response.text();
                } else {
                    return "Does not exist";
                }
            })
            .then(data => {
                employeeNameSpan.innerText = "Employee name: " + data;
            })
            .catch(error => {
                employeeNameSpan.innerText = "Error fetching employee name.";
            });
    } else {
        employeeNameSpan.innerText = "Enter ID to fetch name";
    }
}

// Function to update the rating based on evaluation factor (grade)
function updateRating() {
    const evaluationFactor = parseFloat(document.getElementById('evaluation_factor').value);
    let rating = "";

    if (evaluationFactor === 7) {
        rating = "Excellent";
    } else if (evaluationFactor >= 6.5 && evaluationFactor < 7) {
        rating = "Very Good";
    } else if (evaluationFactor >= 6 && evaluationFactor < 6.5) {
        rating = "Good";
    } else if (evaluationFactor >= 5 && evaluationFactor < 6) {
        rating = "Satisfactory";
    } else if (evaluationFactor >= 4 && evaluationFactor < 5) {
        rating = "Fair";
    } else if (evaluationFactor < 4) {
        rating = "Deficient";
    }

    // Set the calculated rating in the input field
    document.getElementById('rating').value = rating;
}