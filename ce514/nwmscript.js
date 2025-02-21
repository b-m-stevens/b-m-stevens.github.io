// script.js
async function getForecast() {
  const reachId = document.getElementById('reachIdInput').value;
  if (!reachId) {
    alert("Please enter a Reach ID.");
    return;
  }

  const forecastContainer = document.getElementById('forecast-container');
  forecastContainer.style.display = 'block';

  try {
    const apiUrl = `https://api.water.noaa.gov/nwps/v1/reaches/${reachId}/streamflow?series=short_range`;
    const response = await fetch(apiUrl);
    if (!response.ok) {
      throw new Error(`HTTP error status: ${response.status} - ${response.statusText}`);
    }

    const json_data = await response.json();

    if (!json_data.shortRange || !json_data.shortRange.series || !json_data.shortRange.series.data || json_data.shortRange.series.data.length === 0) {
        throw new Error("No forecast data available for this Reach ID.");
    }

    const streamflowData = json_data.shortRange.series.data;
    const timestamps = streamflowData.map(item => item.validTime);
    const flowValues = streamflowData.map(item => item.flow);

    // Update the table
    const table = document.getElementById('timeseries-datatable').getElementsByTagName('tbody')[0];
    table.innerHTML = "";

    for (let i = 0; i < streamflowData.length; i++) {
      const row = table.insertRow();
      const timestampCell = row.insertCell();
      const flowCell = row.insertCell();
      
      // Format timestamp (optional - customize as needed)
      const formattedTimestamp = new Date(timestamps[i]).toLocaleString(); // Example formatting
        timestampCell.textContent = formattedTimestamp;

        // Format flow value to one decimal place
        const formattedFlow = parseFloat(flowValues[i]).toFixed(1); // Format to 1 decimal place
        flowCell.textContent = formattedFlow;


        // Add alternating row colors for readability
        if (i % 2 === 0) {
            row.classList.add('even-row'); // Add class for even rows
        } else {
            row.classList.add('odd-row');  // Add class for odd rows
        }

    }

// Thresholds object: 2 year flood
    const thresholds = {
        15954494: 34.02, // Threshold for reach ID 15954494
        17483383: 85.18, // Threshold for reach ID 17483383
        22107367: 205.55,  // Threshold for reach ID 22107367
        15950892: 32.31,  // Threshold for reach ID 15950892
        18312556: 247.88, // Threshold for reach ID 18312556
        10093052: 40.83   // Threshold for reach ID 10093052
    // Update or create the chart
    };
    const ctx = document.getElementById('streamflowChart').getContext('2d');
    let chart = Chart.getChart('streamflowChart');

    if (chart) {
      chart.destroy();
    }
    
    const chartData = {
        labels: timestamps,
        datasets: [{
            label: 'Streamflow Forecast (Short Range)',
            data: flowValues,
            borderColor: 'blue',
            borderWidth: 1,
            fill: false
        }]
    };

    // Add horizontal threshold line if it exists for the current reachId
    if (thresholds.hasOwnProperty(reachId)) {
        const thresholdValue = thresholds[reachId]; // Store the threshold value

        chartData.datasets.push({
            label: 'Flood Stage',
            // Create an array of the threshold VALUE, not timestamps
            data: Array(timestamps.length).fill(thresholdValue), 
            borderColor: 'red',
            borderWidth: 1,
            fill: false,
            pointRadius: 0
        });
    }
    
    chart = new Chart(ctx, {
        type: 'line',
        data: chartData,
        options: {
            responsive: true,
            scales: {
                x: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Time'
                    }
                },
                y: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Streamflow'
                    }
                }
            }
        }
    });

}
catch (error) {
    console.error('Error fetching or processing data:', error);
    alert("Error fetching forecast: " + error.message);

    const table = document.getElementById('timeseries-datatable').getElementsByTagName('tbody')[0];
    table.innerHTML = "";

    const chartCanvas = document.getElementById('streamflowChart');
    chartCanvas.innerHTML = "";

  }
}
