(function() {
  var App;

  App = (function() {
    function App(options) {
      var defaults = {};
      this.options = $.extend(defaults, options);
      this.init();  
    }   
    
    App.prototype.init = function(){
      var _this = this;
      
      this.player_loaded = new $.Deferred();
      this.zipcodes_loaded = new $.Deferred();
      this.subscribers_loaded = new $.Deferred();
      this.zipcodes = [];
      this.subscribers = [];
      
      $.when(this.zipcodes_loaded, this.subscribers_loaded).done(function() {
        
        // remove zipcodes without subscribers
        var valid_zipcodes = _.unique(_.pluck(_this.subscribers, 'z'));
        _this.zipcodes = _.filter(_this.zipcodes, function(z){ return _.indexOf(valid_zipcodes, z.i) >= 0; });
        
        _this.drawZipcodes(_this.zipcodes);
           
        _this.addListeners();      
      });
      
      this.loadSoundManager();
      this.loadData();      
    };
    
    App.prototype.addListeners = function(){      
      var _this = this,
          $map = $('#map'),
          mapLeft = $map.offset().left,
          mapTop = $map.offset().top,
          mapWidth = $map.width(),
          mapHeight = $map.height(),
          $marker = $('#marker'),
          mw = $marker.width() * 0.5,
          mh = $marker.height() * 0.5;
          
      this.zip_i = -1;
      
      $map.on('mouseover mousemove', function(e){
        var x = e.pageX - mapLeft,
            y = e.pageY - mapTop;
        
        $marker.css({
          left: x - mw,
          top: y - mh
        }).addClass('active');
        
        _this.lookupZip(x/mapWidth, y/mapHeight);
      });
      
      $map.on('mouseout', function(){
        $marker.removeClass('active');
        // $('.seat-group').removeClass('active');
      });
      
    };
    
    App.prototype.distance = function(x1, y1, x2, y2){
      sq1 = (x1-x2) * (x1-x2);
      sq2 = (y1-y2) * (y1-y2);
      return Math.sqrt(sq1 + sq2);
    };
    
    App.prototype.drawZipcodes = function(zips){      
      var $zips = $('<div class="zips"></div>');
      
      _.each(zips, function(z){        
        var $zip = $('<div class="zip"></div>');
        $zip.css({
          top: (z.y * 100) + '%',
          left: (z.x * 100) + '%'
        });
        $zips.append($zip);        
      });
      
      $('#map').append($zips);
      
    };
    
    App.prototype.loadData = function(){
      var _this = this;
      
      $.getJSON('data/zipcodes.json', function(data) {
        console.log('Loaded '+data.length+' zipcodes.');        
        _this.zipcodes = data;     
        _this.zipcodes_loaded.resolve();
      });
      
      $.getJSON('data/subscribers.json', function(data) {
        console.log('Loaded '+data.length+' subscribers.');
        _this.subscribers = data;
        _this.subscribers_loaded.resolve();
      });      
      
    };
    
    App.prototype.loadSoundManager = function(){
      var _this = this;
           
      soundManager.setup({
        url: 'vendor/',
        flashVersion: 9,
        preferFlash: false,
        onready: function() {
          _this.player_loaded.resolve();
        }
      });
    };
    
    App.prototype.lookupSeat = function(zip_i) {
      var $chart = $('#chart');      
      $chart.empty();
      
      var seats = _.where(this.subscribers, {z: zip_i});
      var seat_groups = _.groupBy(seats, function(seat){ return seat.x+','+seat.y; });
      
      $('.seat-group').removeClass('active');
      
      // existing zip group
      if ($('#seat-'+zip_i).length) {
        $('#seat-'+zip_i).addClass('active');
      
      // new zip group
      } else {
        $seats = $('<div id="seat-'+zip_i+'" class="seat-group active"></div>');
      
        _.each(seat_groups, function(group){
          var scale = 1 + group.length * 0.1,
              x = group[0].x * 100,
              y = group[0].y * 100,
              $seat = $('<div class="seat"></div>');
          
          $seat.css({
            left: x+'%',
            top: y+'%',
            transform: 'scale('+scale+')'
          });
          $seats.append($seat);
        });
        
        $chart.append($seats);
      }
      
    };
    
    App.prototype.lookupZip = function(x, y) {
      var zip_i = 0,
          min_distance = -1;
          
      function distance(x1, y1, x2, y2){
        sq1 = (x1-x2) * (x1-x2);
        sq2 = (y1-y2) * (y1-y2);
        return Math.sqrt(sq1 + sq2);
      }
          
      _.each(this.zipcodes, function(zip, i){
        var d = distance(x, y, zip.x, zip.y);
        if (d < min_distance || min_distance < 0) {
          min_distance = d;
          zip_i = zip.i; 
        }
      });
      
      if (this.zip_i != zip_i) {
        this.zip_i = zip_i;
        this.lookupSeat(zip_i);
      }
      
    };
    
    return App;

  })();

  $(function() {
    return new App({});
  });

}).call(this);
