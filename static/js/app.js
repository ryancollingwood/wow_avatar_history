function buildRacesPieChart() {
  const url = "api/count_by/char_class";

  d3.json(url).then(function(response) {
    var data = [{
      labels: response.map(d => d.char_class),
      values: response.map(d => d.total),
      type: 'pie'
    }];
    
    var layout = {
      height: 400,
      width: 500
    };
    
    Plotly.newPlot('character-races-plot', data, layout);

  });
}


function buildRacesByClassBarChart() {
  const url = "api/count_by/race/char_class";  

  d3.json(url).then(function(response) {

    var grouped_data = d3.group(response, d => d.race)
    console.log(grouped_data);

    var traces = [];

    grouped_data.forEach(element => {      
      traces.push({
        x: element.map(d => d.char_class),
        y: element.map(d => d.total),
        name: element[0].race,
        type: 'bar'
      });
    });
    
    var layout = {
      barmode: 'stack',
      height: 400,
      width: 500
    };
    
    Plotly.newPlot('races-by-class-plot', traces, layout);
  });
}


buildRacesPieChart();
buildRacesByClassBarChart();
