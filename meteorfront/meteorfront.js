if (Meteor.isClient) {
Session.set("stats","orgao concedente");
  Template.hello.greeting = function () {
    return Session.get("stats");
  };
SWITCH=0;
  Template.hello.events({
    'click input': function () {
      // template data, if any, is available in 'this'
      if (typeof console !== 'undefined')
        console.log("oi ro!");
        //links=tsvg.selectAll("line.link").data(graph.links2);
        if(SWITCH===0){ // vai p areas de hab
            force.links(graph.links2).start();
            link=link.data(graph.links2);
            SWITCH=1;
            Session.set("stats","area de habilitacao");
        } else if(SWITCH===1){ // vai p misto 
            force.links(graph.links3).start();
            link=link.data(graph.links3);
            SWITCH=2;
            Session.set("stats","orgao concedente + area de habilitacao");
        } else if(SWITCH===2){ // vai p orgs conveniadas
            force.links(graph.links).start();
            link=link.data(graph.links);
            SWITCH=0;
            Session.set("stats","orgao concedente");
        }

                    link
                            .enter().insert("line")
                              .attr("class", "link")
                              .style("stroke-width", function(d) { return Math.sqrt(d.value); });
        link.exit().remove();
// var node = tsvg.selectAll("g.node")
//            .data(force.nodes());
//
//        node.enter().append("g")
//            .attr("class", "node")
//            .call(force.drag);
//
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
force = d3.layout.force()
    .charge(-120)
    .linkDistance(30)
    .size([width, height]);

//Meteor.call("redeTeste",function(error,result){
Meteor.call("redeOSCs3",function(error,result){
    graph3=result.data;
});
Meteor.call("redeOSCs2",function(error,result){
    graph=result.data;
    graph.links3=graph.links.concat(graph.links2);
  force
      .nodes(graph.nodes)
      .links(graph.links)
      .start();

  link = tsvg.selectAll(".link")
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
       redeOSCs3: function () {
            return Meteor.http.call("GET", "http://0.0.0.0:5000/redeOSCs3/"); },
       redeOSCs2: function () {
            return Meteor.http.call("GET", "http://0.0.0.0:5000/redeOSCs2/"); },
    });
  Meteor.startup(function () {
    // code to run on server at startup
  });
}
