function populateFilter() {
  const url = "api/values/race";

  d3.json(url).then(function(response) {
    
    var filerOptions = ["All"];
    filerOptions = filerOptions.concat(response);
    
    d3.select("#sel-filter-race")
      .selectAll("option")
      .data(filerOptions)
      .enter()
      .append("option")
      .text(d => d);

    d3.select("#sel-filter-race").on("change", refreshCharts);
  });
}

function refreshCharts(event) {
  var selectedValue = d3.select(event.target).property('value')
  buildRacesPieChart(selectedValue);
  buildRacesByClassBarChart(selectedValue);
}

function buildRacesPieChart(selectedRace) {
  var url = "api/count_by/race/char_class";
  if (selectedRace != undefined) {
    url = `api/count_by/race/char_class?race=${selectedRace}`;
  }

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


function buildRacesByClassBarChart(selectedRace) {
  var url = "api/count_by/race/char_class";
  if (selectedRace != undefined) {
    url = `api/count_by/race/char_class?race=${selectedRace}`;
  }

  d3.json(url).then(function(response) {

    var grouped_data = d3.group(response, d => d.race)

    var traces = Array();

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

populateFilter();
buildRacesPieChart();
buildRacesByClassBarChart();
