if (Meteor.isClient) {
  Template.hello.greeting = function () {
    return "Bem vindo ao Temporal.";
  };

  Template.hello.events({
    'click input': function () {
      // template data, if any, is available in 'this'
      if (typeof console !== 'undefined')
        console.log("oi ro!");
    }
  });
//  Template.hello.rendered=function(){
//Meteor.call("redeTeste",function(error,result){
//    tres=result;
//    terr=error;
//});
//};
Template.hello.rendered=function(){
    tsvg=d3.select("#svgTemporal");
var color = d3.scale.category20();
height="300";
width ="300";
var force = d3.layout.force()
    .charge(-120)
    .linkDistance(30)
    .size([width, height]);

//Meteor.call("redeTeste",function(error,result){
Meteor.call("redeOSCs",function(error,result){
    graph=result.data;
  force
      .nodes(graph.nodes)
      .links(graph.links)
      .start();

  var link = tsvg.selectAll(".link")
      .data(force.links())
    .enter().append("line")
      .attr("class", "link")
      .style("stroke-width", function(d) { return Math.sqrt(d.value); });

  var node = tsvg.selectAll(".node")
      .data(force.nodes())
    .enter().append("g")
      .attr("class", "node")
      .call(force.drag);
  
node.append("circle")
      .attr("r", 5)
      .style("fill", function(d) { ddd=d; return color(d.group); });

node.append("text")
    .attr("x", 12)
    .attr("dy", ".35em")
    .text(function(d) { return ""; });

  node.append("title")
      .text(function(d) { return d.name; });


  force.on("tick", function() {
    link.attr("x1", function(d) { return d.source.x; })
        .attr("y1", function(d) { return d.source.y; })
        .attr("x2", function(d) { return d.target.x; })
        .attr("y2", function(d) { return d.target.y; });

node.attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; });
//    node.attr("cx", function(d) { return d.x; })
//        .attr("cy", function(d) { return d.y; });
  });
});
};



}

if (Meteor.isServer) {
    Meteor.methods({
       redeTeste: function () {
            return Meteor.http.call("GET", "http://0.0.0.0:5000/redeTeste/"); },
       redeOSCs: function () {
            return Meteor.http.call("GET", "http://0.0.0.0:5000/redeOSCs/"); },
    });
  Meteor.startup(function () {
    // code to run on server at startup
  });
}
