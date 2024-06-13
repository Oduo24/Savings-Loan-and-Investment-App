// Function to update the chart with fetched data
async function updateChart() {
    // Fetch data from backend
    const url = '/member_savings_data';
    const csrf_token = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    const mydata = 1;

    postJSON(mydata, url, csrf_token)
    .then(result => {
        if (result.error) {
            throw new Error(result.error);
        } else {
            const { amount, month } =result;

            // Get the canvas element
            let ctx = document.getElementById('myChart').getContext('2d');

            // Define the data for the chart
            let data = {
                labels: month, // Assuming month contains the names of the months
                datasets: [{
                    label: 'Amount',
                    data: amount,
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 1
                }]
            };

            // Create the chart
            let myChart = new Chart(ctx, {
                type: 'bar',
                data: data,
                options: {
                    scales: {
                        y: {
                            min: 0,
                            beginAtZero: true
                        }
                    }
                }
            });
        }
    })
    .catch(error => {

    });
}

// Call the updateChart function to initially render the chart
document.addEventListener('DOMContentLoaded', () => updateChart());