function fetchEmployeeName() {
    var employeeRut = document.getElementById('employee_rut').value; // Cambiado de employee_id a employee_rut
    var employeeNameSpan = document.getElementById('employee_name');

    if (employeeRut) {
        fetch(`/get_employee_name/${employeeRut}`) // Modificado para usar el RUT
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
        employeeNameSpan.innerText = "Enter RUT to fetch name"; // Modificado el texto indicativo
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