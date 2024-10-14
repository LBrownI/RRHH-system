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