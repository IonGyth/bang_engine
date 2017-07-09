$(document).ready(function() {
//    connectionString = 'http://' + location.host
//    console.log('Connecting web socket: '+connectionString)
//    ws = io.connect(connectionString);
//
//    console.log('Registering beers')
//    $( "button" ).on( "beers", function() {
//        ws.send('request', {who: $(this).attr('id'), data: $(this).val()});
//    });
//    console.log('Registering shot1')
//    $( "button" ).on( "shot1", function() {
//        ws.send('request', {who: $(this).attr('id'), data: $(this).val()});
//    });
//    console.log('Registering shot1')
//    $( "button" ).on( "shot1", function() {
//        ws.send('request', {who: $(this).attr('id'), data: $(this).val()});
//    });
//    console.log('Registering beers')
//    $( "button" ).on( "gatlings", function() {
//        ws.send('request', {who: $(this).attr('id'), data: $(this).val()});
//    });
//    console.log('Registering beers')
//    $( "button" ).on( "arrows", function() {
//        ws.send('request', {who: $(this).attr('id'), data: $(this).val()});
//    });
//    console.log('Registering rolls')
//    $( "button" ).on( "rolls", function() {
//        ws.send('request', {who: $(this).attr('id'), data: $(this).val()});
//    });
//    $( "button" ).on( "rolls", function() {
//        ws.send('request', {who: $(this).attr('id'), data: $(this).val()});
//    });

    // Use a "/test" namespace.
    // An application can open a connection on multiple namespaces, and
    // Socket.IO will multiplex all those connections on a single
    // physical channel. If you don't care about multiple channels, you
    // can set the namespace to an empty string.
    namespace = '';
    // Connect to the Socket.IO server.
    // The connection URL has the following format:
    //     http[s]://<domain>:<port>[/<namespace>]
//    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);
    var socket = io.connect('http://' + location.host);
    // Event handler for new connections.
    // The callback function is invoked when a connection with the
    // server is established.
    socket.on('connect', function() {
        socket.emit('my_event', {data: 'I\'m connected!'});
    });
    // Event handler for server sent data.
    // The callback function is invoked whenever the server emits data
    // to the client. The data is then displayed in the "Received"
    // section of the page.
    socket.on('my_response', function(msg) {
        $('#log').append('<br>' + $('<div/>').text('Received #' + msg.count + ': ' + msg.data).html());
    });
    // Interval function that tests message latency by sending a "ping"
    // message. The server then responds with a "pong" message and the
    // round trip time is measured.
    var ping_pong_times = [];
    var start_time;
    window.setInterval(function() {
        start_time = (new Date).getTime();
        socket.emit('my_ping');
    }, 10000);

    // These accept data from the user and send it to the server in a
    // variety of ways
    $('form#emit').submit(function(event) {
        socket.emit('my_event', {data: $('#emit_data').val()});
        return false;
    });
    $( "Button" ).submit( "roll", function() {
        socket.emit('roll', {
            'beers': $("button.beers").val(),
            'shot1': $("button.shot1").val(),
            'shot2': $("button.shot2").val(),
            'gatlings': $("button.gatlings").val(),
            'dynamite': $("button.dynamite").val()
        });
    });
    $( "Button.start_game" ).click( "start_game", function() {
        socket.emit('start_game');
    });
    socket.on('push_players', function(players) {
        return players.each(function(idx, player) {
        $('<div/>').text('Player ' + player['player_no'] + ' ' + player['role'] +
        ' : hp = ' + player['hp'] +
        ' ,ap = ' + player['arrows'])
        });
    });
    socket.on('start_game', function(   game) {
        var player_container = $("#playerContainer");
        var players = game['players']
        player_container.text('');

        return $.each(players, function(idx, player) {
            for (var player_no in player){
                player = player[player_no]
                player_container.append(
                    $("<div />").text('Player ' + player_no + ' ' + player.role +
                    ' : hp = ' + player.life +
                    ' ,ap = ' + player.arrows)
                );
            }
        });
    });

    // Beer
    $( "#Beer Button.Plus" ).click(function() {
        var $number = $("#Beer Span");
        $number.html((parseInt($number.html(),10) || 0) + 1);
    });
    $( "#Beer Button.Minus" ).click(function() {
        var $number = $("#Beer Span");
        $number.html((parseInt($number.html(),10) || 0) - 1);
    });

    // Shot1
    $( "#Shot1 Button.Plus" ).click(function() {
        var $number = $("#Shot1 Span");
        $number.html((parseInt($number.html(),10) || 0) + 1);
    });
    $( "#Shot1 Button.Minus" ).click(function() {
        var $number = $("#Shot1 Span");
        $number.html((parseInt($number.html(),10) || 0) - 1);
    });

    // Shot2
    $( "#Shot2 Button.Plus" ).click(function() {
        var $number = $("#Shot2 Span");
        $number.html((parseInt($number.html(),10) || 0) + 1);
    });
    $( "#Shot2 Button.Minus" ).click(function() {
        var $number = $("#Shot2 Span");
        $number.html((parseInt($number.html(),10) || 0) - 1);
    });

    // Arrow
    $( "#Arrow Button.Plus" ).click(function() {
        var $number = $("#Arrow Span");
        $number.html((parseInt($number.html(),10) || 0) + 1);
    });
    $( "#Arrow Button.Minus" ).click(function() {
        var $number = $("#Arrow Span");
        $number.html((parseInt($number.html(),10) || 0) - 1);
    });

    // Gatling
    $( "#Gatling Button.Plus" ).click(function() {
        var $number = $("#Gatling Span");
        $number.html((parseInt($number.html(),10) || 0) + 1);
    });
    $( "#Gatling Button.Minus" ).click(function() {
        var $number = $("#Gatling Span");
        $number.html((parseInt($number.html(),10) || 0) - 1);
    });

    // Dynamite
    $( "#Dynamite Button.Plus" ).click(function() {
        var $number = $("#Dynamite Span");
        $number.html((parseInt($number.html(),10) || 0) + 1);
    });
    $( "#Dynamite Button.Minus" ).click(function() {
        var $number = $("#Dynamite Span");
        $number.html((parseInt($number.html(),10) || 0) - 1);
    });

});
