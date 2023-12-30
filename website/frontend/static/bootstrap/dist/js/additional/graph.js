// script.js

// Function to fetch data from the API and update the Plotly graph
function fetchDataAndUpdateGraph(graphId, apiEndpoint) {
    fetch(apiEndpoint)
      .then(response => response.json())
      .then(data => {
        updateGraph(graphId, data);
      })
      .catch(error => console.error('Error fetching data:', error));
}
  
// Function to update the Plotly graph with new data
function updateGraph(graphId, data) {
    const trace = {
      x: Array.from({ length: data.length }, (_, i) => i),
      y: data,
      type: 'scatter',
      mode: 'lines',
    };
  
    const layout = {
      title: 'Live Plotly Graph',
      xaxis: {
        title: 'Time',
      },
      yaxis: {
        title: 'Values',
      },
    };
  
    if (!window.plotlyGraph) {
      window.plotlyGraph = Plotly.newPlot(graphId, [trace], layout);
    } else {
      Plotly.update(graphId, [trace], layout);
    }
}