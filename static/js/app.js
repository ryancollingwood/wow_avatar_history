function populateFilter() {
  // Let's populate the <option> elements in 
  // our <select> from the database. 
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

    // Bind an event to refresh the data
    // when an option is selected.
    d3.select("#sel-filter-race").on("change", refreshCharts);
  });
}

function refreshCharts(event) {
  // event.target will refer tp the selector
  // from which we will get the selected option
  var selectedValue = d3.select(event.target).property('value');

  // With the selectedValue we can refresh the charts
  // filtering if needed. 
  buildRacesPieChart(selectedValue);
  buildRacesByClassBarChart(selectedValue);
}

function buildRacesPieChart(selectedRace) {
  // If we have race to filter by let's pass it
  // in as a querystring parameter
  var url = "api/count_by/race/char_class";
  if (selectedRace != undefined) {
    url = `api/count_by/race/char_class?race=${selectedRace}`;
  }

  d3.json(url).then(function(response) {
    // In order to render a pie chart we need to 
    // extract the labels and values from the 
    // json response. For an example see:
    // https://plotly.com/javascript/pie-charts/ 
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

    // Using the group method in d3 we can
    // do grouping of the received json
    // for the purposes of creating multiple traces.
    // https://github.com/d3/d3-array#group
    var grouped_data = d3.group(response, d => d.race)

    var traces = Array();

    // then iterating over each group by it's
    // key we can create a trace for each group
    // https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/forEach
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

// Upon intial load of the page setup
// the visualisations and the select filter
populateFilter();
buildRacesPieChart();
buildRacesByClassBarChart();
