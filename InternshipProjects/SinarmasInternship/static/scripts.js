document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('prediction-form');
    const resultsTableBody = document.getElementById('prediction-results');

    // Fetch existing data when the page loads
    fetch('/api/view_data')
        .then(response => response.json())
        .then(data => {
            data.forEach(item => {
                addRowToTable(item);
            });
        });

    form.addEventListener('submit', function(event) {
        event.preventDefault();

        // Get the selected model type
        const modelType = event.submitter.value;
        
        const formData = new FormData(form);
        const data = {
            OverallQual: parseFloat(formData.get('OverallQual')),
            TotalBsmtSF: parseFloat(formData.get('TotalBsmtSF')),
            '1stFlrSF': parseFloat(formData.get('1stFlrSF')),
            '2ndFlrSF': parseFloat(formData.get('2ndFlrSF')),
            GrLivArea: parseFloat(formData.get('GrLivArea')),
            GarageCars: parseFloat(formData.get('GarageCars')),
            GarageArea: parseFloat(formData.get('GarageArea')),
            model: modelType // Add model type to data
        };

        // Send the prediction request
        fetch('/api/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        })
        .then(response => response.json())
        .then(result => {
            const now = new Date().toLocaleString();
            data.TotalSF = data.TotalBsmtSF + data['1stFlrSF'] + data['2ndFlrSF'];
            data.TotalLivingArea = data.TotalBsmtSF + data['1stFlrSF'] + data['2ndFlrSF'] + data.GrLivArea;
            data.GarageScore = data.GarageCars * data.GarageArea;
            data.predictedPrice = result.predictedPrice;
            data.dateTime = now;

            // Add the prediction result to the table
            addRowToTable(data);

            // Store the prediction data
            fetch('/api/store_data', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
            });
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });

    function addRowToTable(data) {
        const row = document.createElement('tr');
        row.setAttribute('data-id', data._id);
        row.innerHTML = `
            <td>${data.dateTime}</td>
            <td>${data.OverallQual}</td>
            <td>${data.TotalLivingArea}</td>
            <td>${data.TotalSF}</td>
            <td>${data.TotalBsmtSF}</td>
            <td>${data['1stFlrSF']}</td>
            <td>${data['2ndFlrSF']}</td>
            <td>${data.GrLivArea}</td>
            <td>${data.GarageScore}</td>
            <td>${data.GarageCars}</td>
            <td>${data.GarageArea}</td>
            <td>${data.predictedPrice}</td>
            <td><button class="btn btn-danger btn-sm delete-btn"><i class="fa-solid fa-trash-can"></i></button></td>
        `;
        resultsTableBody.appendChild(row);

        // Add event listener for the delete button
        row.querySelector('.delete-btn').addEventListener('click', function() {
            const id = row.getAttribute('data-id');
            fetch(`/api/delete_data/${id}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                }
            })
            .then(response => response.json())
            .then(result => {
                if (result.status === 'Data deleted successfully') {
                    row.remove();
                } else {
                    console.error('Error:', result);
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });
    }
});