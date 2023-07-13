/**
 * node.js
 *
 * Este programa es un servidor Node.js que recibe datos UDP y los envía a través de WebSocket a clientes conectados.
 * También sirve un archivo HTML estático en respuesta a las solicitudes HTTP.
 *
 * Requiere las siguientes bibliotecas y módulos:
 * - dgram: módulo para la comunicación UDP en Node.js.
 * - http: módulo para crear un servidor HTTP en Node.js.
 * - fs: módulo para leer archivos del sistema de archivos en Node.js.
 * - socket.io: módulo para la comunicación en tiempo real basada en WebSocket.
 */

const dgram = require('dgram');
const http = require('http').createServer(handler);
const fs = require('fs');
const io = require('socket.io')(http);

const UDP_PORT = 5005;

// Crea un socket UDP
const server = dgram.createSocket('udp4');

// Función que se ejecuta cuando se recibe un mensaje UDP
server.on('message', (message, remote) => {
  console.log('Recibido:', message.toString());
  io.sockets.emit('data', parseData(message.toString()));
});

// Enlaza el socket UDP al puerto especificado
server.bind(UDP_PORT, () => {
  console.log('Esperando por datos UDP...');
});

/**
 * Parsea los datos recibidos en formato de cadena y los devuelve como un objeto.
 *
 * @param {string} data - Los datos recibidos en formato de cadena.
 * @returns {object} - Los datos parseados como un objeto con las siguientes propiedades: temp, pressure, humidity, latitude, longitude.
 */
function parseData(data) {
  const [temp, pressure, humidity, latitude, longitude] = data.split('   ');

  return {
    temp: temp.split(':')[1].trim(),
    pressure: pressure.split(':')[1].trim(),
    humidity: humidity.split(':')[1].trim(),
    latitude: latitude.split(':')[1].trim(),
    longitude: longitude.split(':')[1].trim(),
  };
}

/**
 * Manejador para las solicitudes HTTP. Sirve un archivo HTML estático.
 *
 * @param {object} req - El objeto de solicitud HTTP.
 * @param {object} res - El objeto de respuesta HTTP.
 */
function handler(req, res) {
  fs.readFile(__dirname + '/public/index.html', function(err, data) {
    if (err) {
      res.writeHead(404, { 'Content-Type': 'text/html' });
      return res.end("404 Not Found");
    }
    res.writeHead(200, { 'Content-Type': 'text/html' });
    res.write(data);
    return res.end();
  });
}

// Evento para cuando un cliente se conecta a través de WebSocket
io.sockets.on('connection', function(socket) {
  console.log('Cliente conectado');
});

// Inicia el servidor HTTP y escucha en el puerto 8080
http.listen(8080, function() {
  console.log('Servidor HTTP escuchando en el puerto 8080');
});
